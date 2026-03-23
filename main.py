from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.auth import TokenPayload, create_access_token, get_current_user
from core.roles import authorize_employee_access, require_role
from database.db import initialize_database
from routes.attendance import router as attendance_router
from routes.chatbot import router as chatbot_router
from routes.payroll import router as payroll_router
from schemas.employee_schema import (
    LoginRequest,
    TimesheetResponse,
    UserDetails,
    WorkDetailCreate,
    WorkDetailResponse,
    Worktime,
    WorkSlot,
    WorkDetailCreatee,
)
from services.employee_service import authenticate_employee, create_employee
from services.attendance_service import mark_present_on_login
from services.timesheet_service import create_work_detail, delete_work_detail, get_timesheets

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(attendance_router)
app.include_router(payroll_router)
app.include_router(chatbot_router)


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()


@app.get("/")
def root():
    return {"message": "EMS API is running"}


@app.get("/home")
def read_root():
    return {"message": "Welcome"}


@app.post("/register")
def register_employee(
    employee: UserDetails,
    _: TokenPayload = Depends(require_role("admin")),
):
    try:
        employee_id = create_employee(employee)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to register employee") from exc

    return {
        "message": "Employee registered successfully",
        "employee_id": employee_id,
    }


@app.post("/login")
def login(payload: LoginRequest):
    try:
        success, message, employee = authenticate_employee(payload.phone, payload.password)

        if not success:
            if message == "Employee not found.":
                raise HTTPException(status_code=404, detail="User not found")
            if message == "Invalid credentials.":
                raise HTTPException(status_code=401, detail="Invalid password")
            raise HTTPException(status_code=500, detail=message)

        if not employee or employee.id is None:
            raise HTTPException(status_code=500, detail="Unable to login")

        mark_present_on_login(int(employee.id))
        token = create_access_token(user_id=int(employee.id), phone=employee.phone, role=employee.role)
        return {
            "message": "Login successful",
            "token": token,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to login") from exc


@app.post("/work-details", response_model=WorkDetailResponse)
def add_work_detail(
    work_detail: WorkDetailCreate,
    current_user: TokenPayload = Depends(get_current_user),
):
    try:
        authorize_employee_access(current_user, work_detail.employee_id)
        return create_work_detail(work_detail)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to save work detail") from exc


@app.get("/timesheets/{employee_id}", response_model=list[TimesheetResponse])
def get_employee_timesheets(
    employee_id: int,
    current_user: TokenPayload = Depends(get_current_user),
):
    try:
        authorize_employee_access(current_user, employee_id)
        return get_timesheets(employee_id)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to fetch timesheets") from exc


@app.delete("/work-details/{employee_id}/{work_date}")
def remove_work_detail(
    employee_id: int,
    work_date: str,
    _: TokenPayload = Depends(require_role("admin")),
):
    try:
        return delete_work_detail(employee_id, work_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to delete work detail") from exc
