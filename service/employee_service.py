"""Service layer for employee registration and login."""

from typing import Any

import mysql.connector

from core.auth import hash_password, validate_registration_input, verify_password
from logs.logger import get_logger
from schema.models import Employee
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


def register_employee(name: str, phone: str, password: str, role: str = "employee") -> tuple[bool, str, Employee | None]:
    try:
        _ensure_database_ready()
    except Exception:
        return False, "Database is not accessible. Please check DB credentials.", None

    valid, message = validate_registration_input(name, phone, password)
    if not valid:
        return False, message, None

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(queries.SELECT_EMPLOYEE_BY_PHONE, (phone,))
        existing = cursor.fetchone()
        if existing:
            return False, "Phone number is already registered.", None

        secured_password = hash_password(password)
        cursor.execute(queries.INSERT_EMPLOYEE, (name.strip(), phone, secured_password, role))
        connection.commit()

        employee = Employee(
            id=cursor.lastrowid,
            name=name.strip(),
            phone=phone,
            role=role,
            password=None,
        )
        logger.info("Employee registered successfully with id=%s", employee.id)
        return True, "Registration successful.", employee

    except mysql.connector.Error as error:
        logger.exception("Database error during registration: %s", error)
        return False, "Registration failed due to a database error.", None
    except Exception as error:
        logger.exception("Unexpected error during registration: %s", error)
        return False, "Registration failed due to an unexpected error.", None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def login_employee(phone: str, password: str) -> tuple[bool, str, Employee | None]:
    try:
        _ensure_database_ready()
    except Exception:
        return False, "Database is not accessible. Please check DB credentials.", None

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(queries.SELECT_EMPLOYEE_BY_PHONE, (phone,))
        row = cursor.fetchone()

        if not row:
            return False, "Employee not found.", None

        row_data: dict[str, Any] = dict(row)

        if not verify_password(password, str(row_data.get("password", ""))):
            return False, "Invalid credentials.", None

        employee = Employee.from_row(row_data)
        employee.password = None
        logger.info("Employee login successful: id=%s", employee.id)
        return True, "Login successful.", employee

    except mysql.connector.Error as error:
        logger.exception("Database error during login: %s", error)
        return False, "Login failed due to a database error.", None
    except Exception as error:
        logger.exception("Unexpected error during login: %s", error)
        return False, "Login failed due to an unexpected error.", None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_employee_by_phone(phone: str) -> Employee | None:
    try:
        _ensure_database_ready()
    except Exception:
        return None

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(queries.SELECT_EMPLOYEE_BY_PHONE, (phone,))
        row = cursor.fetchone()
        if not row:
            return None

        employee = Employee.from_row(dict(row))
        employee.password = None
        return employee
    except Exception as error:
        logger.exception("Failed to fetch employee by phone: %s", error)
        return None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
