"""Business logic for minimal attendance management."""

from datetime import date, datetime

from database.db import (
    fetch_attendance_by_employee_date,
    fetch_attendance_report,
    initialize_database,
    insert_attendance_record,
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


def mark_present_on_login(employee_id: int) -> None:
    """Create today's attendance as present on first successful login."""
    _ensure_database_ready()

    attendance_date = date.today()
    existing = fetch_attendance_by_employee_date(employee_id, attendance_date)
    if existing:
        logger.info("Attendance already exists for employee_id=%s date=%s", employee_id, attendance_date)
        return

    login_time = datetime.now().time().replace(microsecond=0)
    insert_attendance_record(
        employee_id=employee_id,
        attendance_date=attendance_date,
        login_time=login_time,
        status="present",
    )
    logger.info("Marked present on login for employee_id=%s", employee_id)


def apply_leave(employee_id: int, leave_date: date) -> dict:
    _ensure_database_ready()

    existing = fetch_attendance_by_employee_date(employee_id, leave_date)
    if existing:
        existing_status = str(existing.get("status") or "").lower()
        if existing_status == "present":
            raise ValueError("Leave cannot be applied because attendance is already marked present")
        if existing_status == "leave":
            raise ValueError("Leave already applied for this date")
        raise ValueError("Attendance already marked for this date")

    insert_attendance_record(
        employee_id=employee_id,
        attendance_date=leave_date,
        login_time=None,
        status="leave",
    )
    logger.info("Leave applied for employee_id=%s date=%s", employee_id, leave_date)

    return {
        "message": "Leave applied successfully",
        "date": leave_date,
        "status": "leave",
    }


def get_attendance_report(employee_id: int) -> dict:
    _ensure_database_ready()

    summary = fetch_attendance_report(employee_id)
    return {
        "total_work_days": int(summary.get("total_work_days") or 0),
        "total_leaves": int(summary.get("total_leaves") or 0),
    }
