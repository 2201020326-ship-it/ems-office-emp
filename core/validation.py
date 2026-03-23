"""Input validation helpers for EMS."""

import re
from datetime import datetime

PHONE_REGEX = re.compile(r"^[0-9]{10}$")


def validate_name(name: str) -> tuple[bool, str]:
    if not name or not name.strip():
        return False, "Name cannot be empty."
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long."
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    if not PHONE_REGEX.match(phone or ""):
        return False, "Phone number must be exactly 10 digits."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


def validate_date(work_date: str) -> tuple[bool, str]:
    try:
        datetime.strptime(work_date, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD."


def validate_time(value: str) -> tuple[bool, str]:
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            datetime.strptime(value, fmt)
            return True, ""
        except ValueError:
            continue
    return False, "Invalid time format. Use HH:MM or HH:MM:SS (24-hour)."


def normalize_time(value: str) -> str:
    """Normalize user input into HH:MM:SS format."""
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.strftime("%H:%M:%S")
        except ValueError:
            continue
    return value
