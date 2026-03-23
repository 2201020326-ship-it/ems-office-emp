"""Centralized SQL queries used by the EMS application."""

CREATE_EMPLOYEES_TABLE = """
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'employee') NOT NULL DEFAULT 'employee',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_TIMESHEETS_TABLE = """
CREATE TABLE IF NOT EXISTS timesheets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    work_date DATE NOT NULL,
    slot_number INT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    description VARCHAR(500) NOT NULL,
    CONSTRAINT fk_timesheet_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(id)
        ON DELETE CASCADE
)
"""

CREATE_ATTENDANCE_TABLE = """
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    date DATE NOT NULL,
    login_time TIME NULL,
    status ENUM('present', 'leave') NOT NULL,
    CONSTRAINT uq_attendance_employee_date UNIQUE (employee_id, date),
    CONSTRAINT fk_attendance_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(id)
        ON DELETE CASCADE
)
"""

CREATE_PAYROLL_TABLE = """
CREATE TABLE IF NOT EXISTS payroll (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    base_salary FLOAT NOT NULL,
    total_work_days INT NOT NULL,
    total_leaves INT NOT NULL,
    salary_paid FLOAT NOT NULL,
    CONSTRAINT uq_payroll_employee_month_year UNIQUE (employee_id, month, year),
    CONSTRAINT fk_payroll_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(id)
        ON DELETE CASCADE
)
"""

INSERT_EMPLOYEE = """
INSERT INTO employees (name, phone, password, role)
VALUES (%s, %s, %s, %s)
"""

SELECT_EMPLOYEE_BY_PHONE = """
SELECT id, name, phone, password, role, created_at
FROM employees
WHERE phone = %s
"""

SELECT_EMPLOYEE_BY_ID = """
SELECT id, name, phone, password, role, created_at
FROM employees
WHERE id = %s
LIMIT 1
"""

INSERT_TIMESHEET = """
INSERT INTO timesheets (employee_id, work_date, slot_number, start_time, end_time, description)
VALUES (%s, %s, %s, %s, %s, %s)
"""

SELECT_TIMESHEETS_BY_EMPLOYEE = """
SELECT id, employee_id, work_date, slot_number, start_time, end_time, description
FROM timesheets
WHERE employee_id = %s
ORDER BY work_date DESC, slot_number ASC, start_time ASC
"""

SELECT_MAX_SLOT_BY_EMPLOYEE_DATE = """
SELECT COALESCE(MAX(slot_number), 0) AS max_slot
FROM timesheets
WHERE employee_id = %s AND work_date = %s
"""

DELETE_TIMESHEETS_BY_EMPLOYEE_DATE = """
DELETE FROM timesheets
WHERE employee_id = %s AND work_date = %s
"""

INSERT_ATTENDANCE = """
INSERT INTO attendance (employee_id, date, login_time, status)
VALUES (%s, %s, %s, %s)
"""

UPSERT_ATTENDANCE_PRESENT = """
INSERT INTO attendance (employee_id, date, login_time, status)
VALUES (%s, %s, %s, 'present')
ON DUPLICATE KEY UPDATE
    status = 'present',
    login_time = COALESCE(attendance.login_time, VALUES(login_time))
"""

SELECT_ATTENDANCE_BY_EMPLOYEE_DATE = """
SELECT id, employee_id, date, login_time, status
FROM attendance
WHERE employee_id = %s AND date = %s
LIMIT 1
"""

SELECT_ATTENDANCE_REPORT = """
SELECT
    COALESCE(SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END), 0) AS total_work_days,
    COALESCE(SUM(CASE WHEN status = 'leave' THEN 1 ELSE 0 END), 0) AS total_leaves
FROM attendance
WHERE employee_id = %s
"""

SELECT_ATTENDANCE_COUNTS_BY_MONTH_YEAR = """
SELECT
    COALESCE(SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END), 0) AS present_days,
    COALESCE(SUM(CASE WHEN status = 'leave' THEN 1 ELSE 0 END), 0) AS leave_days
FROM attendance
WHERE employee_id = %s
  AND MONTH(date) = %s
  AND YEAR(date) = %s
"""

SELECT_WORK_HOURS_BY_MONTH_YEAR = """
SELECT
        COALESCE(
                SUM(
                        TIME_TO_SEC(TIMEDIFF(end_time, start_time))
                ) / 3600,
                0
        ) AS total_work_hours
FROM timesheets
WHERE employee_id = %s
    AND MONTH(work_date) = %s
    AND YEAR(work_date) = %s
"""

UPSERT_PAYROLL = """
INSERT INTO payroll (
    employee_id,
    month,
    year,
    base_salary,
    total_work_days,
    total_leaves,
    salary_paid
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    base_salary = VALUES(base_salary),
    total_work_days = VALUES(total_work_days),
    total_leaves = VALUES(total_leaves),
    salary_paid = VALUES(salary_paid)
"""

SELECT_PAYROLL_BY_EMPLOYEE = """
SELECT
    employee_id,
    month,
    year,
    base_salary,
    total_work_days,
    total_leaves,
    salary_paid
FROM payroll
WHERE employee_id = %s
ORDER BY year DESC, month DESC
"""

ALTER_TIMESHEETS_ADD_SLOT_NUMBER = """
ALTER TABLE timesheets
ADD COLUMN slot_number INT NOT NULL DEFAULT 1
"""
