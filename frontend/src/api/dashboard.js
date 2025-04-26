// src/api/dashboard.js
import axios from "axios";

const BASE_URL = "http://localhost:8080";

// 获取仪表盘统计数据
export function getDashboardMetrics() {
  return axios.get(`${BASE_URL}/dashboard/metrics`);
}
