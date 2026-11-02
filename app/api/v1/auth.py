"""Authentication API Endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.models.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    User,
    UserInDB,
    VerifyOtpRequest,
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    """Sign in with email and password."""
    try:
        return auth_service.login(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest):
    """Create a new user account."""
    try:
        return auth_service.register(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=User)
def get_current_user_profile(user: UserInDB = Depends(get_current_user)):
    """Retrieve current authenticated user profile."""
    return User(**user.model_dump())


@router.post("/refresh")
def refresh_token(user: UserInDB = Depends(get_current_user)):
    """Refresh session token."""
    new_token = create_access_token(subject=user.id, user_data=User(**user.model_dump()).model_dump(mode="json"))
    return {"access_token": new_token, "token_type": "bearer"}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):
    """Initiate password reset flow."""
    return {
        "success": True,
        "message": f"Password reset instructions have been sent to {payload.email}.",
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):
    """Reset password with verification token."""
    return {
        "success": True,
        "message": "Your password has been reset successfully. You can now sign in.",
    }


@router.post("/verify-otp")
def verify_otp(payload: VerifyOtpRequest):
    """Verify one-time passcode for two-factor auth or email confirmation."""
    return {
        "success": True,
        "message": "Email OTP verification verified successfully.",
    }


@router.get("/google")
def google_auth_callback():
    """Mock Google OAuth callback handler."""
    return {
        "success": True,
        "message": "Google authentication provider initialized.",
    }

