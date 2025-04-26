// src/pages/ReportNew.jsx
import { useState } from "react";
import { submitReport } from "../api/reports";
import RequireAuth from "../components/RequireAuth";

export default function ReportNew() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return alert("请输入灾情描述");
    setLoading(true);
    setResult(null);

    try {
      const res = await submitReport(text);
      setResult(res.data);
      setText("");  // 提交成功后清空输入框
    } catch (err) {
      alert("提交失败：" + (err.response?.data?.detail || "网络异常"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <RequireAuth>
    <div style={styles.container}>
      <h2>上报灾情</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={10}
          placeholder="请输入灾情描述文本（时间、地点、事件、影响）"
          style={styles.textarea}
        />
        <button type="submit" disabled={loading} style={styles.button}>
          {loading ? "提交中..." : "提交上报"}
        </button>
      </form>

      {result && (
        <div style={styles.result}>
          <h3>摘要结果</h3>
          <p><strong>原始文本：</strong>{result.text}</p>
          <p><strong>模型摘要：</strong>{result.summary}</p>
          <h4>提取事件：</h4>
          <ul>
            {result.disaster_infos?.map((d, idx) => (
              <li key={idx}>
                <span>{d.time} - {d.location} - {d.event} - {d.level}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
    </RequireAuth>
  );
}

const styles = {
  container: {
    maxWidth: "800px",
    margin: "0 auto",
    background: "white",
    padding: "2rem",
    borderRadius: "8px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.08)"
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "1rem"
  },
  textarea: {
    fontSize: "1rem",
    padding: "1rem",
    border: "1px solid #ccc",
    borderRadius: "6px",
    resize: "vertical",
    minHeight: "160px"
  },
  button: {
    padding: "0.75rem",
    fontSize: "1rem",
    backgroundColor: "#5151E5",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer"
  },
  result: {
    marginTop: "2rem",
    padding: "1.5rem",
    backgroundColor: "#f8f8f8",
    borderRadius: "6px",
    boxShadow: "inset 0 0 4px rgba(0,0,0,0.05)"
  }
};
