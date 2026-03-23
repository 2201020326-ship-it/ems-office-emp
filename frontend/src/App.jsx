import { Navigate, Route, Routes } from "react-router-dom";
import AdminDashboard from "./components/AdminDashboard";
import ChatbotWidget from "./components/ChatbotWidget";
import EmployeeDashboard from "./components/EmployeeDashboard";
import LandingPage from "./components/LandingPage";
import Login from "./components/Login";
import { tokenStorage } from "./api";
import { userStorage } from "./utils/auth";

const ProtectedRoute = ({ children, allowedRoles }) => {
  const token = tokenStorage.get();
  const user = userStorage.get();

  if (!token || !user) {
    return <Navigate to="/" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

const App = () => {
  const user = userStorage.get();

  return (
    <div className="app-shell">
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/employee"
          element={
            <ProtectedRoute allowedRoles={["employee", "admin"]}>
              <EmployeeDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="*"
          element={
            <Navigate
              to={user?.role === "admin" ? "/admin" : user ? "/employee" : "/"}
              replace
            />
          }
        />
      </Routes>
      <ChatbotWidget />
      <footer className="site-footer">
        Copyright (c) Umashankar Pradhan &amp; Gayatri Mohanty. All rights
        reserved.
      </footer>
    </div>
  );
};

export default App;
