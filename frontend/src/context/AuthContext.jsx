// src/context/AuthContext.jsx
import { createContext, useState, useEffect } from "react";
import axios from "axios";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [role, setRole] = useState(null);

  // 启动时从 localStorage 恢复
  useEffect(() => {
    const t = localStorage.getItem("token");
    const r = localStorage.getItem("role");
    if (t) {
      setToken(t);
      setRole(r);
      axios.defaults.headers.common["Authorization"] = `Bearer ${t}`;
    }
  }, []);

  const login = ({ access_token, token_type }) => {
    const t = access_token;
    localStorage.setItem("token", t);
    // 从 JWT payload 中解析 role（简单做法）
    const payload = JSON.parse(atob(t.split(".")[1]));
    localStorage.setItem("role", payload.role);
    setRole(payload.role);
    setToken(t);
    axios.defaults.headers.common["Authorization"] = `Bearer ${t}`;
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setToken(null);
    setRole(null);
    delete axios.defaults.headers.common["Authorization"];
  };

  return (
    <AuthContext.Provider value={{ token, role, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
