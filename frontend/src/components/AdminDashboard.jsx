import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { getApiErrorMessage, tokenStorage } from "../api";
import { userStorage } from "../utils/auth";

const defaultRegisterState = {
  name: "",
  phone: "",
  password: "",
  role: "employee",
};

const defaultAttendanceState = {
  employee_id: "",
};

const defaultPayrollGenerateState = {
  employee_id: "",
  month: "",
  year: "",
  base_salary: "",
};

const defaultPayrollHistoryState = {
  employee_id: "",
};

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [activeView, setActiveView] = useState("register");
  const [registerForm, setRegisterForm] = useState(defaultRegisterState);
  const [attendanceForm, setAttendanceForm] = useState(defaultAttendanceState);
  const [attendanceReport, setAttendanceReport] = useState(null);
  const [payrollGenerateForm, setPayrollGenerateForm] = useState(
    defaultPayrollGenerateState,
  );
  const [payrollGenerated, setPayrollGenerated] = useState(null);
  const [payrollHistoryForm, setPayrollHistoryForm] = useState(
    defaultPayrollHistoryState,
  );
  const [payrollHistory, setPayrollHistory] = useState([]);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [attendanceLoading, setAttendanceLoading] = useState(false);
  const [payrollGenerateLoading, setPayrollGenerateLoading] = useState(false);
  const [payrollHistoryLoading, setPayrollHistoryLoading] = useState(false);

  const handleLogout = () => {
    tokenStorage.clear();
    userStorage.clear();
    navigate("/", { replace: true });
  };

  const handleRegisterSubmit = async (event) => {
    event.preventDefault();

    try {
      setRegisterLoading(true);
      await api.post("/register", registerForm);
      alert("Employee registered successfully");
      setRegisterForm(defaultRegisterState);
    } catch (error) {
      alert(getApiErrorMessage(error, "Failed to register employee"));
    } finally {
      setRegisterLoading(false);
    }
  };

  const handleAttendanceReportSubmit = async (event) => {
    event.preventDefault();

    try {
      setAttendanceLoading(true);
      const employeeId = Number(attendanceForm.employee_id);
      const response = await api.get(`/attendance/report/${employeeId}`);
      setAttendanceReport(response.data || null);
    } catch (error) {
      alert(getApiErrorMessage(error, "Failed to fetch attendance report"));
    } finally {
      setAttendanceLoading(false);
    }
  };

  const handlePayrollGenerateSubmit = async (event) => {
    event.preventDefault();

    const employeeId = Number(payrollGenerateForm.employee_id);
    const payload = {
      employee_id: employeeId,
      month: Number(payrollGenerateForm.month),
      year: Number(payrollGenerateForm.year),
      base_salary: Number(payrollGenerateForm.base_salary),
    };

    try {
      setPayrollGenerateLoading(true);
      const response = await api.post(
        `/payroll/generate/${employeeId}`,
        payload,
      );
      setPayrollGenerated(response.data || null);
      alert("Payroll generated successfully");
    } catch (error) {
      alert(getApiErrorMessage(error, "Failed to generate payroll"));
    } finally {
      setPayrollGenerateLoading(false);
    }
  };

  const handlePayrollHistorySubmit = async (event) => {
    event.preventDefault();

    try {
      setPayrollHistoryLoading(true);
      const employeeId = Number(payrollHistoryForm.employee_id);
      const response = await api.get(`/payroll/${employeeId}`);
      setPayrollHistory(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      alert(getApiErrorMessage(error, "Failed to fetch payroll history"));
    } finally {
      setPayrollHistoryLoading(false);
    }
  };

  return (
    <div className="page dashboard-page">
      <header className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <button type="button" onClick={handleLogout}>
          Logout
        </button>
      </header>

      <section className="card">
        <h2>Choose Option</h2>
        <div className="option-actions">
          <button
            type="button"
            className={`option-btn ${activeView === "register" ? "active" : ""}`}
            onClick={() => setActiveView("register")}
          >
            Register Employee
          </button>
          <button
            type="button"
            className={`option-btn ${activeView === "attendance-report" ? "active" : ""}`}
            onClick={() => setActiveView("attendance-report")}
          >
            Attendance Report
          </button>
          <button
            type="button"
            className={`option-btn ${activeView === "payroll-generate" ? "active" : ""}`}
            onClick={() => setActiveView("payroll-generate")}
          >
            Payroll Generate
          </button>
          <button
            type="button"
            className={`option-btn ${activeView === "payroll-history" ? "active" : ""}`}
            onClick={() => setActiveView("payroll-history")}
          >
            Payroll History
          </button>
        </div>
      </section>

      {activeView === "register" ? (
        <section className="card">
          <h2>Register Employee</h2>
          <form onSubmit={handleRegisterSubmit} className="grid-form">
            <input
              type="text"
              placeholder="Name"
              value={registerForm.name}
              onChange={(event) =>
                setRegisterForm((prev) => ({
                  ...prev,
                  name: event.target.value,
                }))
              }
              required
              disabled={registerLoading}
            />
            <input
              type="text"
              placeholder="Phone"
              value={registerForm.phone}
              onChange={(event) =>
                setRegisterForm((prev) => ({
                  ...prev,
                  phone: event.target.value,
                }))
              }
              required
              disabled={registerLoading}
            />
            <input
              type="password"
              placeholder="Password"
              value={registerForm.password}
              onChange={(event) =>
                setRegisterForm((prev) => ({
                  ...prev,
                  password: event.target.value,
                }))
              }
              required
              disabled={registerLoading}
            />
            <select
              value={registerForm.role}
              onChange={(event) =>
                setRegisterForm((prev) => ({
                  ...prev,
                  role: event.target.value,
                }))
              }
              disabled={registerLoading}
            >
              <option value="employee">Employee</option>
              <option value="admin">Admin</option>
            </select>
            <button type="submit" disabled={registerLoading}>
              {registerLoading ? "Saving..." : "Register"}
            </button>
          </form>
        </section>
      ) : activeView === "attendance-report" ? (
        <section className="card">
          <h2>Attendance Report</h2>
          <form onSubmit={handleAttendanceReportSubmit} className="grid-form">
            <input
              type="number"
              placeholder="Employee ID"
              value={attendanceForm.employee_id}
              onChange={(event) =>
                setAttendanceForm((prev) => ({
                  ...prev,
                  employee_id: event.target.value,
                }))
              }
              required
              disabled={attendanceLoading}
            />
            <button type="submit" disabled={attendanceLoading}>
              {attendanceLoading ? "Loading..." : "View Report"}
            </button>
          </form>
          {attendanceReport && (
            <div className="stats">
              <div>
                <span>Work Days</span>
                <strong>{attendanceReport.total_work_days}</strong>
              </div>
              <div>
                <span>Leaves</span>
                <strong>{attendanceReport.total_leaves}</strong>
              </div>
            </div>
          )}
        </section>
      ) : activeView === "payroll-generate" ? (
        <section className="card">
          <h2>Payroll Generate</h2>
          <form onSubmit={handlePayrollGenerateSubmit} className="grid-form">
            <input
              type="number"
              placeholder="Employee ID"
              value={payrollGenerateForm.employee_id}
              onChange={(event) =>
                setPayrollGenerateForm((prev) => ({
                  ...prev,
                  employee_id: event.target.value,
                }))
              }
              required
              disabled={payrollGenerateLoading}
            />
            <input
              type="number"
              placeholder="Month (1-12)"
              value={payrollGenerateForm.month}
              onChange={(event) =>
                setPayrollGenerateForm((prev) => ({
                  ...prev,
                  month: event.target.value,
                }))
              }
              required
              disabled={payrollGenerateLoading}
            />
            <input
              type="number"
              placeholder="Year"
              value={payrollGenerateForm.year}
              onChange={(event) =>
                setPayrollGenerateForm((prev) => ({
                  ...prev,
                  year: event.target.value,
                }))
              }
              required
              disabled={payrollGenerateLoading}
            />
            <input
              type="number"
              placeholder="Base Salary"
              value={payrollGenerateForm.base_salary}
              onChange={(event) =>
                setPayrollGenerateForm((prev) => ({
                  ...prev,
                  base_salary: event.target.value,
                }))
              }
              required
              disabled={payrollGenerateLoading}
            />
            <button type="submit" disabled={payrollGenerateLoading}>
              {payrollGenerateLoading ? "Generating..." : "Generate Payroll"}
            </button>
          </form>
          {payrollGenerated && (
            <div className="table-wrapper">
              <table>
                <tbody>
                  <tr>
                    <th>Employee ID</th>
                    <td>{payrollGenerated.employee_id}</td>
                  </tr>
                  <tr>
                    <th>Month</th>
                    <td>{payrollGenerated.month}</td>
                  </tr>
                  <tr>
                    <th>Year</th>
                    <td>{payrollGenerated.year}</td>
                  </tr>
                  <tr>
                    <th>Total Work Days</th>
                    <td>{payrollGenerated.total_work_days}</td>
                  </tr>
                  <tr>
                    <th>Total Leaves</th>
                    <td>{payrollGenerated.total_leaves}</td>
                  </tr>
                  <tr>
                    <th>Total Work Hours</th>
                    <td>{payrollGenerated.total_work_hours}</td>
                  </tr>
                  <tr>
                    <th>Salary Paid</th>
                    <td>{payrollGenerated.salary_paid}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </section>
      ) : activeView === "payroll-history" ? (
        <section className="card">
          <h2>Payroll History</h2>
          <form onSubmit={handlePayrollHistorySubmit} className="grid-form">
            <input
              type="number"
              placeholder="Employee ID"
              value={payrollHistoryForm.employee_id}
              onChange={(event) =>
                setPayrollHistoryForm((prev) => ({
                  ...prev,
                  employee_id: event.target.value,
                }))
              }
              required
              disabled={payrollHistoryLoading}
            />
            <button type="submit" disabled={payrollHistoryLoading}>
              {payrollHistoryLoading ? "Loading..." : "View History"}
            </button>
          </form>
          {payrollHistory.length > 0 ? (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Month</th>
                    <th>Year</th>
                    <th>Base Salary</th>
                    <th>Work Days</th>
                    <th>Leaves</th>
                    <th>Salary Paid</th>
                  </tr>
                </thead>
                <tbody>
                  {payrollHistory.map((item, index) => (
                    <tr
                      key={`${item.employee_id}-${item.year}-${item.month}-${index}`}
                    >
                      <td>{item.month}</td>
                      <td>{item.year}</td>
                      <td>{item.base_salary}</td>
                      <td>{item.total_work_days}</td>
                      <td>{item.total_leaves}</td>
                      <td>{item.salary_paid}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No payroll history available.</p>
          )}
        </section>
      ) : null}
    </div>
  );
};

export default AdminDashboard;
