"""Database connection and schema setup for EMS."""

import os
from pathlib import Path
from typing import Any

import mysql.connector

from logs.logger import get_logger
from sql import queries

logger = get_logger(__name__)


def _load_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        logger.warning(".env file not found at %s", env_path)
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env()


def _db_config(include_database: bool = True) -> dict:
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
    }
    if include_database:
        config["database"] = os.getenv("DB_NAME", "ems_db")
    return config


def get_connection() -> Any:
    try:
        return mysql.connector.connect(**_db_config(include_database=True))
    except mysql.connector.Error as error:
        logger.exception("Failed to connect to database: %s", error)
        raise


def initialize_database() -> None:
    db_name = os.getenv("DB_NAME", "ems_db")
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**_db_config(include_database=False))
        cursor = connection.cursor(dictionary=True)

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")

        cursor.execute(queries.CREATE_EMPLOYEES_TABLE)
        cursor.execute(queries.CREATE_TIMESHEETS_TABLE)
        cursor.execute(queries.CREATE_ATTENDANCE_TABLE)
        cursor.execute(queries.CREATE_PAYROLL_TABLE)

        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = 'employees'
              AND column_name = 'role'
            LIMIT 1
            """,
            (db_name,),
        )
        has_role = cursor.fetchone()
        if not has_role:
            cursor.execute(
                """
                ALTER TABLE employees
                ADD COLUMN role ENUM('admin', 'employee') NOT NULL DEFAULT 'employee'
                """
            )

        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = 'employees'
              AND column_name = 'created_at'
            LIMIT 1
            """,
            (db_name,),
        )
        has_created_at = cursor.fetchone()
        if not has_created_at:
            cursor.execute(
                """
                ALTER TABLE employees
                ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                """
            )

        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = 'timesheets'
              AND column_name = 'slot_number'
            LIMIT 1
            """,
            (db_name,),
        )
        has_slot_number = cursor.fetchone()
        if not has_slot_number:
            cursor.execute(queries.ALTER_TIMESHEETS_ADD_SLOT_NUMBER)

        connection.commit()
        logger.info("Database initialized successfully.")

    except mysql.connector.Error as error:
        logger.exception("Database initialization failed: %s", error)
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
