// src/pages/Dashboard.jsx

import { useEffect, useState } from "react";
import { getDashboardMetrics } from "../api/dashboard";
import { Line } from "react-chartjs-2";
import RequireAuth from "../components/RequireAuth";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from "chart.js";
ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getDashboardMetrics()
      .then(res => setData(res.data))
      .catch(err => alert("获取仪表盘数据失败"));
  }, []);

  if (!data) return <p>加载中...</p>;

  const { total_reports, today_reports, pending_dedup, last_dedup, report_trend } = data;

  const trendData = {
    labels: report_trend.map(d => d.date.slice(5)), // 显示 MM-DD
    datasets: [
      {
        label: "7日上报趋势",
        data: report_trend.map(d => d.count),
        fill: false,
        borderColor: "#5151E5",
        backgroundColor: "#5151E5",
        tension: 0.3,
        pointRadius: 4
      }
    ]
  };

  return (
    <RequireAuth>
    <div>
      <h2>仪表盘</h2>

      {/* 卡片区域 */}
      <div style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "1rem",
        marginBottom: "1.5rem",
        justifyContent: "space-between"
      }}>
        <Card title="总上报数" value={total_reports} color="#3498db" />
        <Card title="今日上报" value={today_reports} color="#2ecc71" />
        <Card title="待去重数" value={pending_dedup} color="#e67e22" />
      </div>

      {/* 去重摘要 */}
      <div style={{
        background: "white",
        padding: "1rem 1.5rem",
        borderRadius: "8px",
        boxShadow: "0 0 6px rgba(0,0,0,0.05)",
        marginBottom: "1.5rem"
      }}>
        <h3>最近一次去重</h3>
        {last_dedup ? (
          <ul style={{ lineHeight: "1.8" }}>
            <li><strong>运行时间：</strong>{new Date(last_dedup.run_at).toLocaleString()}</li>
            <li><strong>重复条数：</strong>{last_dedup.duplicates_detected}</li>
            <li><strong>合并簇数：</strong>{last_dedup.merged_clusters}</li>
            <li><strong>删除记录：</strong>{last_dedup.deleted_records}</li>
          </ul>
        ) : (
          <p>暂无去重记录</p>
        )}
      </div>

      {/* 趋势图 */}
      <div style={{
        background: "white",
        padding: "1rem 1.5rem",
        borderRadius: "8px",
        boxShadow: "0 0 6px rgba(0,0,0,0.05)"
      }}>
        <h3>近 7 日上报趋势</h3>
        <Line data={trendData} />
      </div>
    </div>
    </RequireAuth>
  );
}

function Card({ title, value, color = "#5151E5" }) {
  return (
    <div style={{
      background: color,
      color: "white",
      padding: "1rem 1.2rem",
      borderRadius: "12px",
      boxShadow: "0 6px 12px rgba(0,0,0,0.1)",
      flex: "1 1 200px",
      transition: "transform 0.2s ease",
      cursor: "default"
    }}
      onMouseEnter={(e) => e.currentTarget.style.transform = "scale(1.03)"}
      onMouseLeave={(e) => e.currentTarget.style.transform = "scale(1)"}
    >
      <p style={{ fontSize: "0.9rem", opacity: 0.9 }}>{title}</p>
      <h2 style={{ margin: 0, fontSize: "1.8rem" }}>{value}</h2>
    </div>
  );
}
