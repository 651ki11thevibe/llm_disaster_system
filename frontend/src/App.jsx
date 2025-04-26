import { Routes, Route, Navigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "./context/AuthContext";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import MainLayout from "./layouts/MainLayout";

import Dashboard from "./pages/Dashboard";
import ReportNew from "./pages/ReportNew";
import ReportList from "./pages/ReportList";
import Profile from "./pages/Profile";
import RequireAuth from "./components/RequireAuth";

function App() {
  const { token } = useContext(AuthContext);

  return (
    <Routes>
      {/* 未登录时显示登录/注册页 */}
      <Route path="/" element={!token ? <Login /> : <Navigate to="/dashboard" />} />
      <Route path="/signup" element={!token ? <Signup /> : <Navigate to="/dashboard" />} />

      {/* 登录后显示主界面 */}
      <Route path="/" element={<RequireAuth><MainLayout /></RequireAuth>}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="reports/new" element={<ReportNew />} />
        <Route path="reports" element={<ReportList />} />
        <Route path="profile" element={<Profile />} />
      </Route>
    </Routes>
  );
}

export default App;
