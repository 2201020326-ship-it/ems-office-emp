"""Backward-compatible JWT exports."""

from core.auth import ALGORITHM, SECRET_KEY, TOKEN_EXPIRE_HOURS, create_access_token, decode_access_token
