"""Authentication and registration logic."""

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import TypedDict

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.validation import validate_name, validate_password, validate_phone


ITERATIONS = 100_000
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "2"))
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-in-production")


class TokenPayload(TypedDict):
    user_id: int
    phone: str
    role: str


bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Create a salted hash in the format: salt$hash."""
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS,
    ).hex()
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify PBKDF2 hash. Supports legacy plain text fallback."""
    if "$" not in (stored_password or ""):
        return hmac.compare_digest(plain_password, stored_password or "")

    salt, saved_hash = stored_password.split("$", 1)
    check_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS,
    ).hex()
    return hmac.compare_digest(check_hash, saved_hash)


def validate_registration_input(name: str, phone: str, password: str) -> tuple[bool, str]:
    validators = (
        validate_name(name),
        validate_phone(phone),
        validate_password(password),
    )
    for valid, message in validators:
        if not valid:
            return False, message
    return True, ""


def create_access_token(user_id: int, phone: str, role: str = "employee") -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {
        "user_id": user_id,
        "phone": phone,
        "role": role,
        "exp": expire_at,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

    user_id = payload.get("user_id")
    phone = payload.get("phone")
    role = payload.get("role")
    if user_id is None or phone is None or role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return {
        "user_id": int(user_id),
        "phone": str(phone),
        "role": str(role),
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> TokenPayload:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    return decode_access_token(credentials.credentials)
