// src/pages/Profile.jsx
import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { getProfile, updateUserId, changePassword } from "../api/profile";
import { useNavigate } from "react-router-dom";
import RequireAuth from "../components/RequireAuth";

export default function Profile() {
  const { token, logout } = useContext(AuthContext);
  const [profile, setProfile] = useState(null);
  const [showIdModal, setShowIdModal] = useState(false);
  const [newId, setNewId] = useState("");
  const [showPwdModal, setShowPwdModal] = useState(false);
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const navigate = useNavigate();

  const fetchProfile = async () => {
    try {
      const res = await getProfile(token);
      setProfile(res.data);
    } catch (e) {
      console.error("获取用户信息失败", e);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const cardStyle = {
    maxWidth: "500px",
    margin: "5rem auto",
    background: "#fff",
    padding: "2rem",
    borderRadius: "8px",
    boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
    textAlign: "center", 
  };

  if (!profile) return <div style={{ textAlign: "center", marginTop: "5rem" }}>加载中...</div>;

  return (
    <RequireAuth>
    <div style={cardStyle}>
      <h2 style={{ textAlign: "center", marginBottom: "2rem" }}>用户中心</h2>
      <p><strong>用户名：</strong> {profile.username}</p>
      <p><strong>角色：</strong> {profile.role === "admin" ? "管理员" : "普通用户"}</p>

      <div style={{ marginTop: "2rem", display: "flex", gap: "1rem", justifyContent: "center" }}>
        <button onClick={() => setShowIdModal(true)}>修改用户名</button>
        <button onClick={() => setShowPwdModal(true)}>修改密码</button>
      </div>

      {/* 修改用户名弹窗 */}
      {showIdModal && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h3>修改用户名</h3>
            <input
              value={newId}
              onChange={(e) => setNewId(e.target.value)}
              placeholder="请输入新用户名"
              style={{ width: "100%", marginBottom: "1rem", padding: 8 }}
            />
            <div style={{ textAlign: "right" }}>
              <button onClick={() => setShowIdModal(false)} style={{ marginRight: 8 }}>取消</button>
              <button onClick={async () => {
                try {
                  await updateUserId(token, { new_user_id: newId });
                  alert("用户名修改成功，请重新登录");
                  logout();
                  navigate("/login");
                } catch (e) {
                  alert("修改失败：" + (e.response?.data?.detail || e.message));
                }
              }}>确认</button>
            </div>
          </div>
        </div>
      )}

      {/* 修改密码弹窗 */}
      {showPwdModal && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h3>修改密码</h3>
            <input
              type="password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              placeholder="请输入旧密码"
              style={{ width: "100%", marginBottom: "1rem", padding: 8 }}
            />
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="请输入新密码"
              style={{ width: "100%", marginBottom: "1rem", padding: 8 }}
            />
            <div style={{ textAlign: "right" }}>
              <button onClick={() => setShowPwdModal(false)} style={{ marginRight: 8 }}>取消</button>
              <button onClick={async () => {
                try {
                  await changePassword(token, {
                    old_password: oldPassword,
                    new_password: newPassword,
                  });
                  alert("密码修改成功，请重新登录");
                  logout();
                  navigate("/login");
                } catch (e) {
                  alert("修改失败：" + (e.response?.data?.detail || e.message));
                }
              }}>确认</button>
            </div>
          </div>
        </div>
      )}
        {/* Footer 内容 */}
        <div style={{ marginTop: "2rem", textAlign: "center", color: "#888", fontSize: "0.9rem" }}>
          发现问题请联系作者：<a href="mailto:Yates_Huuu@163.com">Yates_Huuu@163.com</a><br />
          本系统部分功能依赖大语言模型（LLM），使用中请遵循以下原则：
          <ul style={{
            listStyleType: "disc",
            margin: "0.5rem auto",
            paddingLeft: "1.5rem",
            maxWidth: "600px",
            textAlign: "center",
          }}>
            <li>输出结果可能存在不确定性，请谨慎用于决策。</li>
            <li>避免提交涉及敏感、涉政等信息的文本。</li>
            <li>仅作学术与毕业设计用途，禁止用于商业发布。</li>
          </ul>
        </div>
    </div>
    </RequireAuth>
  );
}
