// src/api/auth.js
import axios from "axios";

const API_BASE = "http://localhost:8080";  // 后端地址

// 登录，返回 { access_token, token_type }
export function loginAPI({ username, password }) {
  // FastAPI 要求 x-www-form-urlencoded
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);
  return axios.post(`${API_BASE}/auth/token`, params, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
}

// 注册，返回新用户信息
export function signupAPI({ username, password, admin_key }) {
  return axios.post(`${API_BASE}/auth/signup`, {
    username,
    password,
    admin_key: admin_key || "",
  });
}
