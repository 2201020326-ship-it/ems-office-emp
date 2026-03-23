"""Pydantic schemas for attendance endpoints."""

from datetime import date

from pydantic import BaseModel, Field


class LeaveRequest(BaseModel):
    date: date


class LeaveResponse(BaseModel):
    message: str
    date: date
    status: str


class AttendanceReportResponse(BaseModel):
    total_work_days: int
    total_leaves: int
