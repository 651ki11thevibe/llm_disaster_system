// src/pages/Login.jsx
import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { loginAPI } from "../api/auth";
import { AuthContext } from "../context/AuthContext";
import "../App.css";

export default function Login() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await loginAPI(form);
      login(res.data);
      navigate("/dashboard");
    } catch (err) {
      alert("登录失败: " + err.response?.data?.detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
      <h1 className="app-title">基于大模型的灾害信息处理系统</h1>
       <h2>登录</h2>
        <form onSubmit={handleSubmit}>
          <div>
            <input
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="用户名"
              required
            />
          </div>
          <div>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="密码"
              required
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? "登录中..." : "登录"}
          </button>
        </form>
        <p>
          没有账号？<Link to="/signup">注册</Link>
        </p>
      </div>
    </div>
  );
}
