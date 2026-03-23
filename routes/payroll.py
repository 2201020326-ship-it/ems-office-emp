"""Payroll API routes."""

from fastapi import APIRouter, Depends, HTTPException

from core.auth import TokenPayload, get_current_user
from core.roles import authorize_employee_access, require_role
from schemas.payroll_schema import PayrollGenerateRequest, PayrollGenerateResponse, PayrollHistoryItem
from services.payroll_service import generate_payroll, get_payroll_history

router = APIRouter(prefix="/payroll", tags=["Payroll"])


@router.post("/generate/{employee_id}", response_model=PayrollGenerateResponse)
def payroll_generate(
    employee_id: int,
    payload: PayrollGenerateRequest,
    current_user: TokenPayload = Depends(require_role("admin")),
):
    try:
        if payload.employee_id != employee_id:
            raise HTTPException(status_code=400, detail="employee_id path and body must match")

        return generate_payroll(
            employee_id=employee_id,
            month=payload.month,
            year=payload.year,
            base_salary=float(payload.base_salary),
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to generate payroll") from exc


@router.get("/{employee_id}", response_model=list[PayrollHistoryItem])
def payroll_history(
    employee_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    try:
        authorize_employee_access(current_user, employee_id)
        return get_payroll_history(employee_id)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to fetch payroll history") from exc
