// src/layouts/MainLayout.jsx
import { Outlet, useNavigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import "./MainLayout.css";

export default function MainLayout() {
  const { logout, role } = useContext(AuthContext);
  const navigate = useNavigate();

  const menu = [
    { path: "/dashboard", label: "仪表盘" },
    { path: "/reports/new", label: "上报灾情" },
    { path: "/reports", label: "报告列表" },
    { path: "/profile", label: "用户中心" },
  ];

  return (
    <div className="layout-root">
      <div className="sidebar">
        <h2 className="sidebar-title">灾害信息处理系统</h2>
        <ul>
          {menu.map((item) => (
            <li key={item.path} onClick={() => navigate(item.path)}>
              {item.label}
            </li>
          ))}
        </ul>
        <button className="logout-btn" onClick={logout}>退出登录</button>
      </div>
      <div className="main-content">
        <Outlet />
      </div>
    </div>
  );
}
