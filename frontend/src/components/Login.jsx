import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { getApiErrorMessage, tokenStorage } from "../api";
import { getUserFromToken, userStorage } from "../utils/auth";

const Login = () => {
  const navigate = useNavigate();
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const currentUser = userStorage.get();
    if (tokenStorage.get() && currentUser) {
      navigate(currentUser.role === "admin" ? "/admin" : "/employee", {
        replace: true,
      });
    }
  }, [navigate]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!phone || !password) {
      alert("Please enter both phone and password.");
      return;
    }

    try {
      setLoading(true);
      const response = await api.post("/login", { phone, password });
      const token = response?.data?.token;

      if (!token) {
        throw new Error("No token returned from login API");
      }

      const user = getUserFromToken(token);
      tokenStorage.set(token);
      userStorage.set(user);

      navigate(user.role === "admin" ? "/admin" : "/employee", {
        replace: true,
      });
    } catch (error) {
      alert(getApiErrorMessage(error, "Login failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page login-page">
      <div className="card login-card">
        <h1>Employee Management System</h1>
        <p>Sign in to continue</p>
        <form onSubmit={handleSubmit}>
          <label htmlFor="phone">Phone</label>
          <input
            id="phone"
            type="text"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
            placeholder="10 digit phone"
            autoComplete="username"
            disabled={loading}
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter password"
            autoComplete="current-password"
            disabled={loading}
          />

          <button type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
