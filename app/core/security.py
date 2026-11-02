"""Security, password hashing, and JWT token management."""

import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError


def hash_password(password: str) -> str:
    """Hash a password securely with salt using SHA-256 (portable across systems)."""
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}:{pwd_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored salt:hash string."""
    try:
        if ":" not in hashed_password:
            # Fallback legacy match
            return plain_password == hashed_password
        salt, expected_hash = hashed_password.split(":", 1)
        calc_hash = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
        return calc_hash == expected_hash
    except Exception:
        return False


def create_access_token(subject: str, user_data: Optional[Dict[str, Any]] = None, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token for authentication."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "user": user_data or {}
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Session token has expired. Please sign in again.")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid authentication token.")

