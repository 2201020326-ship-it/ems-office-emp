"""Compatibility employee service for FastAPI layer."""

from schema.models import Employee
from schemas.employee_schema import UserDetails
from service.employee_service import (
    get_employee_by_phone as service_get_employee_by_phone,
    login_employee as service_login_employee,
    register_employee,
)


def create_employee(employee: UserDetails) -> int:
    success, message, created = register_employee(employee.name, employee.phone, employee.password, employee.role)
    if not success or not created or created.id is None:
        raise ValueError(message)
    return int(created.id)


def authenticate_employee(phone: str, password: str) -> tuple[bool, str, Employee | None]:
    return service_login_employee(phone, password)


def get_employee_by_phone(phone: str) -> Employee | None:
    return service_get_employee_by_phone(phone)
