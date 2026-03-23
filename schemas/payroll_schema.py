"""Pydantic schemas for payroll endpoints."""

from pydantic import BaseModel, Field


class PayrollGenerateRequest(BaseModel):
    employee_id: int = Field(gt=0)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)
    base_salary: float = Field(gt=0)


class PayrollGenerateResponse(BaseModel):
    message: str
    employee_id: int
    month: int
    year: int
    base_salary: float
    total_work_days: int
    total_leaves: int
    total_work_hours: float
    salary_paid: float


class PayrollHistoryItem(BaseModel):
    employee_id: int
    month: int
    year: int
    base_salary: float
    total_work_days: int
    total_leaves: int
    salary_paid: float
