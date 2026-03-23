"""Pydantic schemas for EMS FastAPI endpoints."""

from typing import Any
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from datetime import date, time


class UserDetails(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=10, max_length=10)
    password: str = Field(min_length=6, max_length=128)
    role: Literal["admin", "employee"] = "employee"


class LoginRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=20)
    password: str = Field(min_length=6, max_length=128)


class WorkSlot(BaseModel):
    start_time: time
    end_time: time
    description: str = Field(min_length=1, max_length=255)


class Worktime(BaseModel):
    work_date: date | None = None
    slots: list[WorkSlot] = Field(min_length=1)

    @field_validator("slots", mode="before")
    @classmethod
    def normalize_slots(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return [value]
        return value


class WorkDetailCreate(BaseModel):
    employee_id: int
    work_date: date | None = None
    slots: list[WorkSlot] = Field(min_length=1)

    @field_validator("slots", mode="before")
    @classmethod
    def normalize_slots(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return [value]
        return value


class WorkDetailCreatee(WorkDetailCreate):
    """Backward compatible alias model."""


class WorkDetailResponse(BaseModel):
    success: bool
    message: str
    employee_id: int
    work_date: date
    slots_saved: int


class TimesheetResponse(BaseModel):
    id: int | None
    employee_id: int
    work_date: date
    slot_number: int
    start_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    description: str
