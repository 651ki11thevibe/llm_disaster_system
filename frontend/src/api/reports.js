// src/api/reports.js
import axios from "axios";

const BASE_URL = "http://localhost:8080";

// 上报灾情：传入 text 字段
export function submitReport(text) {
  return axios.post(`${BASE_URL}/report`, { text });
}

// 查询报告列表（分页 + 关键词）
export function fetchReports(params = {}) {
  return axios.get(`${BASE_URL}/reports`, { params });
}

// 更新报告，重新全文推理（管理员）
export function updateReport(id, text) {
  return axios.put(`${BASE_URL}/report/${id}`, { text });
}

// 删除报告（管理员）
export function deleteReport(id) {
  return axios.delete(`${BASE_URL}/report/${id}`);
}

//手写更新元组信息（管理员）
export function updateDisasterInfo(id, data) {
  return axios.put(`${BASE_URL}/disaster-info/${id}`, data);
}

// 导出为 Excel 文件（用户/管理员均可）
export function exportExcel(token, keyword = "") {
  return axios.get(`${BASE_URL}/reports/export_excel`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    params: { q: keyword },
    responseType: "blob",
  });
}

//去重合并(管理员)
export function runDedup(token) {
  return axios.post(`${BASE_URL}/dedup`, {}, {
    headers: { Authorization: `Bearer ${token}` }
  });
}