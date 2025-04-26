// src/pages/ReportList.jsx
import { useEffect, useState, useContext } from "react";
import { fetchReports, deleteReport, updateReport, updateDisasterInfo, exportExcel, runDedup } from "../api/reports";
import { AuthContext } from "../context/AuthContext";
import RequireAuth from "../components/RequireAuth";
import "../App.css";

export default function ReportList() {
  const { role } = useContext(AuthContext);
  const { token } = useContext(AuthContext);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10); // 固定每页数量
  const [total, setTotal] = useState(0);
  const [editRecord, setEditRecord] = useState(null);
  const [editInfos, setEditInfos] = useState([]);
  const [useRerun, setUseRerun] = useState(false);
  const [editText, setEditText] = useState("");
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [dedupLoading, setDedupLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchReports({ q: keyword, page, page_size: pageSize });
      setData(res.data.items || res.data);  // 适配接口格式
      setTotal(res.data.total || res.data.length);
    } catch (err) {
      alert("获取报告失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const timer = setInterval(loadData, 10000); // 每 10 秒自动刷新
    return () => clearInterval(timer);
  }, [page, keyword]);

  const handleDelete = async (id) => {
    if (!window.confirm("确认删除该报告？")) return;
    await deleteReport(id);
    loadData(); // 删除后刷新列表
  };

  const handleExport = async () => {
    try {
      const res = await exportExcel(token, keyword);
      const blob = new Blob([res.data], { type: res.headers["content-type"] });
      const url = window.URL.createObjectURL(blob);
      
      const link = document.createElement("a");
      link.href = url;
      link.download = "灾情报告.xlsx";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert("导出失败：" + (e.response?.data?.detail || e.message));
    }
  };

  // 处理去重
  const handleDedup = async () => {
    if (!window.confirm("确认运行去重？此操作会删除重复条目。")) return;
    setDedupLoading(true);
    try {
      const res = await runDedup(token);
      const clusters = res.data?.cluster_details || [];
  
      if (clusters.length === 0) {
        alert("没有发现需要合并的记录。");
      } else {
        let msg = "以下是本次合并的结果：\n\n";
        clusters.forEach((c, i) => {
          msg += `簇 ${i + 1}：主记录 ${c.main_display_id}，合并了 ${c.merged_display_ids.join("、")}\n`;
        });
        alert(msg);
      }
  
      loadData();  // 刷新页面
    } catch (err) {
      alert("去重失败：" + (err.response?.data?.detail || err.message));
    } finally {
      setDedupLoading(false);
    }
  };
  


  const cellStyle = {
    padding: "0.75rem",
    borderBottom: "1px solid #eee",
    whiteSpace: "normal",     // 允许换行
    wordBreak: "break-word", // 防止长文本撑出
    verticalAlign: "middle", 
  };

  function openEditModal(report) {
    setEditRecord(report);
    setEditInfos(report.disaster_infos.map(d => ({ ...d })));
    setEditText(report.text);
    setUseRerun(false);
  }
  
  function closeEditModal() {
    setEditRecord(null);
    }
  
  const [expandedRow, setExpandedRow] = useState(null);

  const toggleExpand = (id) => {
    setExpandedRow(prev => (prev === id ? null : id));
  };

  return (
    <RequireAuth>
    <div>
      <h2>报告列表</h2>

      {/* 查询栏 */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem", alignItems: "center" }}>
        <input
          placeholder="关键词搜索（摘要、地点、类型）"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") loadData();  // 支持回车搜索
          }}
          style={{ padding: "0.5rem", flex: 1 }}
        />

        <button
          onClick={loadData}
          style={{
            padding: "0.5rem 1rem",
            background: "#1890ff",
            color: "#fff",
            border: "none",
            borderRadius: 4,
            fontSize: "0.9rem"
          }}
        >
          搜索
        </button>
        <button
          onClick={handleExport}
          style={{
            padding: "0.5rem 1rem",
            background: "#52c41a",
            color: "#fff",
            border: "none",
            borderRadius: 4,
            fontSize: "0.9rem",
            whiteSpace: "nowrap"
          }}
        >
          导出 Excel
        </button>
      {role === "admin" && (
        <button
          onClick={handleDedup}
          disabled={dedupLoading}
          style={{
            padding: "0.5rem 1rem",
            background: "#f56c6c",       // 红色区分
            color: "#fff",
            border: "none",
            borderRadius: 4,
            fontSize: "0.9rem",
            whiteSpace: "nowrap",
            marginLeft: "0.5rem"        // 按需加点间距
          }}
        >
          {dedupLoading ? "去重中…" : "运行去重"}
        </button>
        )}
      </div>
      <div style={{
          backgroundColor: "#fff",
          borderRadius: "8px",
          padding: "1rem",
          boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
          overflowX: "auto",
          maxHeight: "500px",       
          overflowY: "auto",
          marginBottom: "1.5rem"
        }}>
      {/* 表格 */}
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          borderRadius: "8px",
          overflow: "hidden",
          backgroundColor: "#fff",
          boxShadow: "0 4px 12px rgba(0,0,0,0.05)"
        }}
      >
        <thead>
          <tr style={{ background: "#f9fafb", borderBottom: "1px solid #ddd" }}>
            <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: "600", color: "#333" }}>ID</th>
            <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: "600", color: "#333" }}>摘要</th>
            <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: "600", color: "#333" }}>时间</th>
            <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: "600", color: "#333" }}>地点</th>
            <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: "600", color: "#333" }}>灾害类型</th>
            <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: "600", color: "#333" }}>受灾程度</th>
            <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: "600", color: "#333" }}>上报时间</th>
            <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: "600", color: "#333" }}>上报次数</th>
            {role === "admin" && (
              <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: "600", color: "#333" }}>操作</th>
            )}
          </tr>
        </thead>
        <tbody>
        {data.map((r) =>
          r.disaster_infos.map((d, idx) => (
            <tr key={`${r.id}-${idx}`} style={{ borderBottom: "1px solid #ddd", verticalAlign: "top" }}>
              {idx === 0 && (
                <>
                  <td rowSpan={r.disaster_infos.length} style={{...cellStyle, minWidth: "40px", whiteSpace: "nowrap", textAlign: "center"}}>{r.id}</td>
                  <td
                    rowSpan={r.disaster_infos.length}
                    style={{
                      maxWidth: "300px",
                      wordBreak: "break-word",
                      whiteSpace: "normal",
                      padding: "0.75rem"
                    }}
                    title={r.summary}
                  >
                    {r.summary}
                  </td>
                </>
              )}

              <td style={cellStyle}>{d.time || "—"}</td>
              <td style={cellStyle}>{d.location || "—"}</td>
              <td style={cellStyle}>{d.event || "—"}</td>
              <td style={cellStyle}>{d.level || "—"}</td>

              {idx === 0 && (
                <>
                  <td rowSpan={r.disaster_infos.length} style={cellStyle}>{new Date(r.created_at).toLocaleString()}</td>
                  <td rowSpan={r.disaster_infos.length} style={{...cellStyle, minWidth: "40px", whiteSpace: "nowrap", textAlign: "center"}}>{r.disaster_infos?.[0]?.report_count || "—"}</td>
                  {role === "admin" && (
                    <td rowSpan={r.disaster_infos.length} style={cellStyle}>
                      <button
                        onClick={() => openEditModal(r)}
                        style={{
                          padding: "4px 8px",
                          borderRadius: "4px",
                          background: "#409eff",
                          color: "#fff",
                          border: "none",
                          marginRight: 6,
                          cursor: "pointer",
                          fontSize: "0.9rem"
                        }}
                      >编辑</button>
                      <button
                        onClick={() => handleDelete(r.id)}
                        style={{
                          padding: "4px 8px",
                          borderRadius: "4px",
                          background: "#ff4d4f",
                          color: "#fff",
                          border: "none",
                          cursor: "pointer",
                          fontSize: "0.9rem"
                        }}
                      >删除</button>
                    </td>
                  )}
                </>
              )}
            </tr>
          ))
        )}
      </tbody>
      </table>
    </div>
      {/* 分页栏 */}
      <div style={{ marginTop: "1rem", display: "flex", justifyContent: "center", alignItems: "center", gap: "1rem" }}>
        <button
          onClick={() => {
            setPage(prev => Math.max(prev - 1, 1));
            window.scrollTo({ top: 0, behavior: "smooth" });
          }}
          disabled={page === 1}
          style={{
            padding: "0.5rem 1rem",
            background: page === 1 ? "#ccc" : "#409eff",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: page === 1 ? "not-allowed" : "pointer"
          }}
        >
          上一页
        </button>

        <span style={{ fontSize: "0.9rem" }}>
          第 {page} 页 / 共 {Math.ceil(total / pageSize) || 1} 页
        </span>

        <button
          onClick={() => {
            setPage(prev => prev + 1);
            window.scrollTo({ top: 0, behavior: "smooth" });
          }}
          disabled={(page * pageSize) >= total}
          style={{
            padding: "0.5rem 1rem",
            background: (page * pageSize) >= total ? "#ccc" : "#409eff",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: (page * pageSize) >= total ? "not-allowed" : "pointer"
          }}
        >
          下一页
        </button>
      </div>
      
      {editRecord && (
      <div className="modal-overlay">
        <div className="modal-box">
          <h3>编辑报告 #{editRecord.id}</h3>

          <label style={{ display: "block", marginBottom: "0.5rem" }}>
            <input
              type="checkbox"
              checked={useRerun}
              onChange={(e) => setUseRerun(e.target.checked)}
            />
            &nbsp;使用原始文本重新推理
          </label>

          {useRerun ? (
            <textarea
              rows={6}
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              style={{ width: "100%", padding: 8 }}
            />
          ) : (
            <table style={{ width: "100%", marginTop: 8 }}>
              <thead>
                <tr><th>时间</th><th>地点</th><th>事件</th><th>受灾程度</th></tr>
              </thead>
              <tbody>
                {editInfos.map((d, i) => (
                  <tr key={d.id}>
                    <td><input value={d.time} onChange={e => {
                      const tmp = [...editInfos]; tmp[i].time = e.target.value; setEditInfos(tmp);
                    }} /></td>
                    <td><input value={d.location} onChange={e => {
                      const tmp = [...editInfos]; tmp[i].location = e.target.value; setEditInfos(tmp);
                    }} /></td>
                    <td><input value={d.event} onChange={e => {
                      const tmp = [...editInfos]; tmp[i].event = e.target.value; setEditInfos(tmp);
                    }} /></td>
                    <td><input value={d.level} onChange={e => {
                      const tmp = [...editInfos]; tmp[i].level = e.target.value; setEditInfos(tmp);
                    }} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div style={{ marginTop: "1rem", textAlign: "right" }}>
            <button onClick={closeEditModal} style={{ marginRight: 8 }}>取消</button>
            <button
              disabled={confirmLoading}
              onClick={async () => {
                setConfirmLoading(true);
                try {
                  if (useRerun) {
                    await updateReport(editRecord.id, editText);
                  } else {
                    for (const d of editInfos) {
                      await updateDisasterInfo(d.id, {
                        time: d.time,
                        location: d.location,
                        event: d.event,
                        level: d.level,
                      });
                    }
                  }
                  closeEditModal();
                  loadData(); // 刷新表格
                } catch (e) {
                  alert("更新失败：" + (e.response?.data?.detail || e.message));
                } finally {
                  setConfirmLoading(false);
                }
              }}
            >
              {confirmLoading ? "提交中..." : "确认提交"}
            </button>
          </div>
        </div>
      </div>
    )}
    </div>
    </RequireAuth>
  );
}
