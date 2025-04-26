import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function RequireAuth({ children }) {
  const { token } = useContext(AuthContext);
  const navigate = useNavigate();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setChecking(false);
    }, 100); // 给token一点点时间从localStorage恢复，比如100ms
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!checking && !token) {
      navigate("/");
    }
  }, [checking, token, navigate]);

  if (checking) {
    return <div style={{ textAlign: "center", marginTop: "2rem" }}>加载中...</div>;
  }

  return children;
}
