// src/pages/Signup.jsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { signupAPI } from "../api/auth";
import "../App.css";

export default function Signup() {
  const [form, setForm] = useState({ username: "", password: "", admin_key: "" });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await signupAPI(form);
      alert("注册成功，请登录！");
      navigate("/");
    } catch (err) {
      alert("注册失败: " + err.response?.data?.detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
       <h1 className="app-title">基于大模型的灾害信息处理系统</h1>
        <h2>注册</h2>
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
          <div>
            <input
              name="admin_key"
              value={form.admin_key}
              onChange={handleChange}
              placeholder="管理员密钥（可选）"
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? "注册中..." : "注册"}
          </button>
        </form>
        <p>
          已有账号？<Link to="/">登录</Link>
        </p>
      </div>
    </div>
  );
}
