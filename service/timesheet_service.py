"""Service layer for timesheet operations."""

from datetime import datetime

import mysql.connector

from core.validation import normalize_time, validate_date, validate_time
from logs.logger import get_logger
from schema.models import Timesheet
from sql.db import get_connection, initialize_database
from sql import queries

logger = get_logger(__name__)

_DB_READY = False


def _ensure_database_ready() -> None:
    global _DB_READY
    if _DB_READY:
        return
    initialize_database()
    _DB_READY = True


def _validate_slot(start_time: str, end_time: str, description: str) -> tuple[bool, str]:
    valid_start, msg_start = validate_time(start_time)
    if not valid_start:
        return False, msg_start

    valid_end, msg_end = validate_time(end_time)
    if not valid_end:
        return False, msg_end

    if not description or not description.strip():
        return False, "Description cannot be empty."

    start_dt = datetime.strptime(normalize_time(start_time), "%H:%M:%S")
    end_dt = datetime.strptime(normalize_time(end_time), "%H:%M:%S")
    if end_dt <= start_dt:
        return False, "End time must be greater than start time."

    return True, ""


def submit_timesheet(
    employee_id: int,
    work_date: str,
    slots: list[dict[str, str]],
) -> tuple[bool, str]:
    try:
        _ensure_database_ready()
    except Exception:
        return False, "Database is not accessible. Please check DB credentials."

    valid_date, date_msg = validate_date(work_date)
    if not valid_date:
        return False, date_msg

    if not slots:
        return False, "At least one timesheet slot is required."

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        first_slot_start_time = ""

        cursor.execute(
            queries.SELECT_MAX_SLOT_BY_EMPLOYEE_DATE,
            (employee_id, work_date),
        )
        existing_slot_row = cursor.fetchone() or {}
        current_max_slot = int(existing_slot_row.get("max_slot") or 0)

        for index, slot in enumerate(slots, start=1):
            start_time = slot.get("start_time", "")
            end_time = slot.get("end_time", "")
            description = slot.get("description", "")

            valid_slot, message = _validate_slot(start_time, end_time, description)
            if not valid_slot:
                return False, message

            normalized_start_time = normalize_time(start_time)
            normalized_end_time = normalize_time(end_time)
            if index == 1:
                first_slot_start_time = normalized_start_time

            cursor.execute(
                queries.INSERT_TIMESHEET,
                (
                    employee_id,
                    work_date,
                    current_max_slot + index,
                    normalized_start_time,
                    normalized_end_time,
                    description.strip(),
                ),
            )

        cursor.execute(
            queries.UPSERT_ATTENDANCE_PRESENT,
            (
                employee_id,
                work_date,
                first_slot_start_time or None,
            ),
        )

        connection.commit()
        logger.info("Timesheet submitted for employee_id=%s date=%s", employee_id, work_date)
        return True, "Timesheet submitted successfully."

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()
        logger.exception("Database error during timesheet submit: %s", error)
        return False, "Failed to submit timesheet due to a database error."
    except Exception as error:
        if connection:
            connection.rollback()
        logger.exception("Unexpected error during timesheet submit: %s", error)
        return False, "Failed to submit timesheet due to an unexpected error."
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_timesheets(employee_id: int) -> tuple[bool, str, list[Timesheet]]:
    try:
        _ensure_database_ready()
    except Exception:
        return False, "Database is not accessible. Please check DB credentials.", []

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(queries.SELECT_TIMESHEETS_BY_EMPLOYEE, (employee_id,))
        rows = cursor.fetchall() or []
        timesheets = [Timesheet.from_row(dict(row)) for row in rows]
        return True, "Timesheets fetched successfully.", timesheets

    except mysql.connector.Error as error:
        logger.exception("Database error while fetching timesheets: %s", error)
        return False, "Failed to fetch timesheets due to a database error.", []
    except Exception as error:
        logger.exception("Unexpected error while fetching timesheets: %s", error)
        return False, "Failed to fetch timesheets due to an unexpected error.", []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def delete_work_details(employee_id: int, work_date: str) -> tuple[bool, str, int]:
    try:
        _ensure_database_ready()
    except Exception:
        return False, "Database is not accessible. Please check DB credentials.", 0

    valid_date, date_msg = validate_date(work_date)
    if not valid_date:
        return False, date_msg, 0

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            queries.DELETE_TIMESHEETS_BY_EMPLOYEE_DATE,
            (employee_id, work_date),
        )
        deleted_count = int(cursor.rowcount or 0)
        connection.commit()

        if deleted_count == 0:
            return False, "No work details found for the selected date.", 0

        logger.info(
            "Deleted %s work detail slot(s) for employee_id=%s date=%s",
            deleted_count,
            employee_id,
            work_date,
        )
        return True, "Work details deleted successfully.", deleted_count

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()
        logger.exception("Database error while deleting work details: %s", error)
        return False, "Failed to delete work details due to a database error.", 0
    except Exception as error:
        if connection:
            connection.rollback()
        logger.exception("Unexpected error while deleting work details: %s", error)
        return False, "Failed to delete work details due to an unexpected error.", 0
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
