"""Authentication and User Data Models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """Domain model representing an authenticated user."""
    id: str
    email: str
    name: str
    role: str = "creator"  # creator, pro, enterprise, admin
    credits: int = 450
    plan: str = "Pro Studio"
    avatar: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class UserInDB(User):
    """User representation stored internally with password hash."""
    hashed_password: str


class LoginRequest(BaseModel):
    """Login payload."""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """Registration payload."""
    email: str
    password: str
    name: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request payload."""
    email: str


class ResetPasswordRequest(BaseModel):
    """Reset password payload with token."""
    email: str
    token: str
    new_password: str


class VerifyOtpRequest(BaseModel):
    """Email or login OTP verification."""
    email: str
    otp: str


class AuthResponse(BaseModel):
    """Response returned upon successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: User
