import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { getApiErrorMessage, tokenStorage } from "../api";
import { userStorage } from "../utils/auth";

const defaultWorkDetailsState = {
  work_date: "",
  start_time: "",
  end_time: "",
  description: "",
};

const defaultLeaveState = {
  date: "",
};

const EmployeeDashboard = () => {
  const navigate = useNavigate();
  const user = useMemo(() => userStorage.get(), []);
  const [activeView, setActiveView] = useState("work-details");
  const [workDetailsForm, setWorkDetailsForm] = useState(
    defaultWorkDetailsState,
  );
  const [leaveForm, setLeaveForm] = useState(defaultLeaveState);
  const [workSaveLoading, setWorkSaveLoading] = useState(false);
  const [leaveLoading, setLeaveLoading] = useState(false);
  const [timesheets, setTimesheets] = useState([]);
  const [attendance, setAttendance] = useState({
    total_work_days: 0,
    total_leaves: 0,
  });
  const [loading, setLoading] = useState(true);

  const fetchEmployeeData = async () => {
    if (!user?.userId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const [timesheetRes, attendanceRes] = await Promise.all([
        api.get(`/timesheets/${user.userId}`),
        api.get(`/attendance/report/${user.userId}`),
      ]);

      setTimesheets(Array.isArray(timesheetRes.data) ? timesheetRes.data : []);
      setAttendance(
        attendanceRes.data || { total_work_days: 0, total_leaves: 0 },
      );
    } catch (error) {
      alert(getApiErrorMessage(error, "Failed to load employee dashboard"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployeeData();
  }, [user?.userId]);

  useEffect(() => {
    if (!user?.userId) {
      return undefined;
    }

    const intervalId = setInterval(() => {
      fetchEmployeeData();
    }, 10000);

    return () => clearInterval(intervalId);
  }, [user?.userId]);

  const handleWorkDetailsSubmit = async (event) => {
    event.preventDefault();

    if (!user?.userId) {
      alert("Unable to identify logged in employee");
      return;
    }

    const payload = {
      employee_id: Number(user.userId),
      work_date: workDetailsForm.work_date,
      slots: [
        {
          start_time: workDetailsForm.start_time,
          end_time: workDetailsForm.end_time,
          description: workDetailsForm.description,
        },
      ],
    };

    try {
      setWorkSaveLoading(true);
      await api.post("/work-details", payload);
      alert("Work details saved successfully");
      setWorkDetailsForm(defaultWorkDetailsState);
      await fetchEmployeeData();
      setActiveView("timesheets");
    } catch (error) {
      alert(getApiErrorMessage(error, "Failed to save work details"));
    } finally {
      setWorkSaveLoading(false);
    }
  };

  const handleLogout = () => {
    tokenStorage.clear();
    userStorage.clear();
    navigate("/", { replace: true });
  };

  const handleApplyLeave = async (event) => {
    event.preventDefault();

    if (!leaveForm.date) {
      alert("Please select a leave date");
      return;
    }

    try {
      setLeaveLoading(true);
      await api.post("/attendance/leave", { date: leaveForm.date });
      alert("Leave applied successfully");
      setLeaveForm(defaultLeaveState);
      await fetchEmployeeData();
      setActiveView("attendance");
    } catch (error) {
      alert(getApiErrorMessage(error, "Failed to apply leave"));
    } finally {
      setLeaveLoading(false);
    }
  };

  return (
    <div className="page dashboard-page">
      <header className="dashboard-header">
        <h1>Employee Dashboard</h1>
        <button type="button" onClick={handleLogout}>
          Logout
        </button>
      </header>

      <section className="card">
        <h2>Choose Option</h2>
        <div className="option-actions">
          <button
            type="button"
            className={`option-btn ${activeView === "work-details" ? "active" : ""}`}
            onClick={() => setActiveView("work-details")}
          >
            Work Details
          </button>
          <button
            type="button"
            className={`option-btn ${activeView === "timesheets" ? "active" : ""}`}
            onClick={() => setActiveView("timesheets")}
          >
            Timesheets
          </button>
          <button
            type="button"
            className={`option-btn ${activeView === "attendance" ? "active" : ""}`}
            onClick={() => setActiveView("attendance")}
          >
            Attendance Report
          </button>
          <button
            type="button"
            className={`option-btn ${activeView === "apply-leave" ? "active" : ""}`}
            onClick={() => setActiveView("apply-leave")}
          >
            Attendance Leave
          </button>
        </div>
      </section>

      {activeView === "work-details" ? (
        <section className="card">
          <h2>Submit Work Details</h2>
          <form className="grid-form" onSubmit={handleWorkDetailsSubmit}>
            <input
              type="date"
              value={workDetailsForm.work_date}
              onChange={(event) =>
                setWorkDetailsForm((prev) => ({
                  ...prev,
                  work_date: event.target.value,
                }))
              }
              required
              disabled={workSaveLoading}
            />
            <input
              type="time"
              value={workDetailsForm.start_time}
              onChange={(event) =>
                setWorkDetailsForm((prev) => ({
                  ...prev,
                  start_time: event.target.value,
                }))
              }
              required
              disabled={workSaveLoading}
            />
            <input
              type="time"
              value={workDetailsForm.end_time}
              onChange={(event) =>
                setWorkDetailsForm((prev) => ({
                  ...prev,
                  end_time: event.target.value,
                }))
              }
              required
              disabled={workSaveLoading}
            />
            <input
              type="text"
              placeholder="Description"
              value={workDetailsForm.description}
              onChange={(event) =>
                setWorkDetailsForm((prev) => ({
                  ...prev,
                  description: event.target.value,
                }))
              }
              required
              disabled={workSaveLoading}
            />
            <button type="submit" disabled={workSaveLoading}>
              {workSaveLoading ? "Saving..." : "Save Work Details"}
            </button>
          </form>
        </section>
      ) : activeView === "timesheets" ? (
        <section className="card">
          <h2>Timesheets</h2>
          {loading ? (
            <p>Loading timesheets...</p>
          ) : timesheets.length === 0 ? (
            <p>No timesheets available.</p>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Slot</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {timesheets.map((item) => (
                    <tr
                      key={`${item.id ?? item.work_date}-${item.slot_number}`}
                    >
                      <td>{item.work_date}</td>
                      <td>{item.slot_number}</td>
                      <td>{item.start_time}</td>
                      <td>{item.end_time}</td>
                      <td>{item.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      ) : activeView === "attendance" ? (
        <>
          <section className="card">
            <h2>View Attendance Report</h2>
            {loading ? (
              <p>Loading report...</p>
            ) : (
              <div className="stats">
                <div>
                  <span>Work Days</span>
                  <strong>{attendance.total_work_days}</strong>
                </div>
                <div>
                  <span>Leaves</span>
                  <strong>{attendance.total_leaves}</strong>
                </div>
              </div>
            )}
          </section>
        </>
      ) : (
        <section className="card">
          <h2>Attendance Leave</h2>
          <form className="grid-form" onSubmit={handleApplyLeave}>
            <input
              type="date"
              value={leaveForm.date}
              onChange={(event) =>
                setLeaveForm((prev) => ({ ...prev, date: event.target.value }))
              }
              required
              disabled={leaveLoading}
            />
            <button type="submit" disabled={leaveLoading}>
              {leaveLoading ? "Applying..." : "Apply Leave"}
            </button>
          </form>
        </section>
      )}
    </div>
  );
};

export default EmployeeDashboard;
