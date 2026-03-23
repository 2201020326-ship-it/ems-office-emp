"""Compatibility database module for FastAPI entrypoint."""

from datetime import date
from typing import Any

from logs.logger import get_logger
from sql import queries
from sql.db import get_connection, initialize_database

logger = get_logger(__name__)


def fetch_attendance_by_employee_date(employee_id: int, attendance_date: date) -> dict[str, Any] | None:
	connection = None
	cursor = None
	try:
		connection = get_connection()
		cursor = connection.cursor(dictionary=True)
		cursor.execute(queries.SELECT_ATTENDANCE_BY_EMPLOYEE_DATE, (employee_id, attendance_date))
		row = cursor.fetchone()
		return dict(row) if row else None
	finally:
		if cursor:
			cursor.close()
		if connection and connection.is_connected():
			connection.close()


def insert_attendance_record(
	employee_id: int,
	attendance_date: date,
	login_time: Any,
	status: str,
) -> int:
	connection = None
	cursor = None
	try:
		connection = get_connection()
		cursor = connection.cursor(dictionary=True)
		cursor.execute(
			queries.INSERT_ATTENDANCE,
			(employee_id, attendance_date, login_time, status),
		)
		connection.commit()
		return int(cursor.lastrowid or 0)
	except Exception:
		if connection:
			connection.rollback()
		logger.exception("Failed to insert attendance record")
		raise
	finally:
		if cursor:
			cursor.close()
		if connection and connection.is_connected():
			connection.close()


def fetch_attendance_report(employee_id: int) -> dict[str, Any]:
	connection = None
	cursor = None
	try:
		connection = get_connection()
		cursor = connection.cursor(dictionary=True)
		cursor.execute(queries.SELECT_ATTENDANCE_REPORT, (employee_id,))
		row = cursor.fetchone() or {}
		return dict(row)
	finally:
		if cursor:
			cursor.close()
		if connection and connection.is_connected():
			connection.close()


def fetch_attendance_counts_by_month_year(employee_id: int, month: int, year: int) -> dict[str, Any]:
	connection = None
	cursor = None
	try:
		connection = get_connection()
		cursor = connection.cursor(dictionary=True)
		cursor.execute(queries.SELECT_ATTENDANCE_COUNTS_BY_MONTH_YEAR, (employee_id, month, year))
		row = cursor.fetchone() or {}
		return dict(row)
	finally:
		if cursor:
			cursor.close()
		if connection and connection.is_connected():
			connection.close()


def fetch_employee_by_id(employee_id: int) -> dict[str, Any] | None:
	connection = None
	cursor = None
	try:
		connection = get_connection()
		cursor = connection.cursor(dictionary=True)
		cursor.execute(queries.SELECT_EMPLOYEE_BY_ID, (employee_id,))
		row = cursor.fetchone()
		return dict(row) if row else None
	finally:
		if cursor:
			cursor.close()
		if connection and connection.is_connected():
			connection.close()


def fetch_work_hours_by_month_year(employee_id: int, month: int, year: int) -> float:
	connection = None
	cursor = None
	try:
		connection = get_connection()
		cursor = connection.cursor(dictionary=True)
		cursor.execute(queries.SELECT_WORK_HOURS_BY_MONTH_YEAR, (employee_id, month, year))
		row = cursor.fetchone() or {}
		return float(row.get("total_work_hours") or 0.0)
	finally:
		if cursor:
			cursor.close()
		if connection and connection.is_connected():
			connection.close()


def upsert_payroll_record(
	employee_id: int,
	month: int,
	year: int,
	base_salary: float,
	total_work_days: int,
	total_leaves: int,
	salary_paid: float,
) -> None:
	connection = None
	cursor = None
	try:
		connection = get_connection()
		cursor = connection.cursor(dictionary=True)
		cursor.execute(
			queries.UPSERT_PAYROLL,
			(
				employee_id,
				month,
				year,
				base_salary,
				total_work_days,
				total_leaves,
				salary_paid,
			),
		)
		connection.commit()
	except Exception:
		if connection:
			connection.rollback()
		logger.exception("Failed to upsert payroll record")
		raise
	finally:
		if cursor:
			cursor.close()
		if connection and connection.is_connected():
			connection.close()


def fetch_payroll_history(employee_id: int) -> list[dict[str, Any]]:
	connection = None
	cursor = None
	try:
		connection = get_connection()
		cursor = connection.cursor(dictionary=True)
		cursor.execute(queries.SELECT_PAYROLL_BY_EMPLOYEE, (employee_id,))
		rows = cursor.fetchall() or []
		return [dict(row) for row in rows]
	finally:
		if cursor:
			cursor.close()
		if connection and connection.is_connected():
			connection.close()


__all__ = [
	"get_connection",
	"initialize_database",
	"fetch_attendance_by_employee_date",
	"insert_attendance_record",
	"fetch_attendance_report",
	"fetch_attendance_counts_by_month_year",
	"fetch_employee_by_id",
	"fetch_work_hours_by_month_year",
	"upsert_payroll_record",
	"fetch_payroll_history",
]
