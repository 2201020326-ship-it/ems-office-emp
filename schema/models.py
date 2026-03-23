"""Data models for EMS entities."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, time
from typing import Any


@dataclass
class Employee:
    id: int | None
    name: str
    phone: str
    role: str = "employee"
    password: str | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "Employee":
        return cls(
            id=row.get("id"),
            name=row.get("name", ""),
            phone=row.get("phone", ""),
            role=str(row.get("role") or "employee"),
            password=row.get("password"),
        )


@dataclass
class Timesheet:
    id: int | None
    employee_id: int
    work_date: str
    slot_number: int
    start_time: str
    end_time: str
    description: str

    @staticmethod
    def _date_to_str(value: Any) -> str:
        if isinstance(value, date):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _time_to_str(value: Any) -> str:
        if isinstance(value, time):
            return value.strftime("%H:%M:%S")
        return str(value)

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "Timesheet":
        return cls(
            id=row.get("id"),
            employee_id=int(row.get("employee_id") or 0),
            work_date=cls._date_to_str(row.get("work_date")),
            slot_number=int(row.get("slot_number") or 1),
            start_time=cls._time_to_str(row.get("start_time")),
            end_time=cls._time_to_str(row.get("end_time")),
            description=row.get("description", ""),
        )
