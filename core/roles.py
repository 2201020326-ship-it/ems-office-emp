"""Role-based access control helpers."""

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from core.auth import TokenPayload, get_current_user


def is_admin(user: TokenPayload) -> bool:
    return str(user.get("role", "")).lower() == "admin"


def require_role(required_role: str) -> Callable[[TokenPayload], TokenPayload]:
    role_name = required_role.lower()

    def role_checker(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if str(current_user.get("role", "")).lower() != role_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role} role required",
            )
        return current_user

    return role_checker


def authorize_employee_access(current_user: TokenPayload, employee_id: int) -> None:
    if is_admin(current_user):
        return

    if int(current_user["user_id"]) != int(employee_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this employee data",
        )
