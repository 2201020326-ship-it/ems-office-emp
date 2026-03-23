"""Attendance API routes."""

from fastapi import APIRouter, Depends, HTTPException

from core.auth import TokenPayload, get_current_user
from core.roles import authorize_employee_access
from schemas.attendance_schema import (
    AttendanceReportResponse,
    LeaveRequest,
    LeaveResponse,
)
from services.attendance_service import (
    apply_leave,
    get_attendance_report,
)

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/leave", response_model=LeaveResponse)
def attendance_leave(
    payload: LeaveRequest,
    current_user: TokenPayload = Depends(get_current_user),
):
    try:
        employee_id = int(current_user["user_id"])
        return apply_leave(employee_id, payload.date)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to apply leave") from exc


@router.get("/report/{employee_id}", response_model=AttendanceReportResponse)
def attendance_report(
    employee_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    try:
        authorize_employee_access(current_user, employee_id)
        return get_attendance_report(employee_id)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to fetch attendance report") from exc
