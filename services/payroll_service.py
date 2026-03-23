"""Business logic for payroll generation and retrieval."""

from database.db import (
    fetch_attendance_counts_by_month_year,
    fetch_employee_by_id,
    fetch_payroll_history,
    fetch_work_hours_by_month_year,
    initialize_database,
    upsert_payroll_record,
)
from logs.logger import get_logger

logger = get_logger(__name__)

_DB_READY = False


def _ensure_database_ready() -> None:
    global _DB_READY
    if _DB_READY:
        return
    initialize_database()
    _DB_READY = True


def generate_payroll(employee_id: int, month: int, year: int, base_salary: float) -> dict:
    _ensure_database_ready()

    employee = fetch_employee_by_id(employee_id)
    if not employee:
        raise ValueError("Employee not found")

    counts = fetch_attendance_counts_by_month_year(employee_id, month, year)
    present_days = int(counts.get("present_days") or 0)
    leave_days = int(counts.get("leave_days") or 0)
    total_days = present_days + leave_days
    total_work_hours = round(fetch_work_hours_by_month_year(employee_id, month, year), 2)

    if total_days <= 0:
        raise ValueError("No attendance data found for the selected month and year")

    salary_paid = round((float(base_salary) / total_days) * present_days, 2)

    upsert_payroll_record(
        employee_id=employee_id,
        month=month,
        year=year,
        base_salary=float(base_salary),
        total_work_days=present_days,
        total_leaves=leave_days,
        salary_paid=salary_paid,
    )
    logger.info("Payroll generated for employee_id=%s month=%s year=%s", employee_id, month, year)

    return {
        "message": "Payroll generated successfully",
        "employee_id": employee_id,
        "month": month,
        "year": year,
        "base_salary": float(base_salary),
        "total_work_days": present_days,
        "total_leaves": leave_days,
        "total_work_hours": total_work_hours,
        "salary_paid": salary_paid,
    }


def get_payroll_history(employee_id: int) -> list[dict]:
    _ensure_database_ready()

    employee = fetch_employee_by_id(employee_id)
    if not employee:
        raise ValueError("Employee not found")

    return fetch_payroll_history(employee_id)
