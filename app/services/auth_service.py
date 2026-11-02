"""Authentication Business Logic Service."""

import uuid
from typing import Dict, Optional
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.auth import AuthResponse, LoginRequest, RegisterRequest, User, UserInDB
from app.repositories.user_repository import UserRepository, user_repository


class AuthService:
    """Handles user onboarding, credential validation, and JWT token issuance."""

    def __init__(self, repo: UserRepository = user_repository):
        self.repo = repo

    def register(self, req: RegisterRequest) -> AuthResponse:
        """Register a new user account with initial starter credits."""
        existing = self.repo.get_by_email(req.email)
        if existing:
            raise AuthenticationError("An account with this email address already exists.")

        user_id = f"usr_{uuid.uuid4().hex[:10]}"
        new_user = UserInDB(
            id=user_id,
            email=req.email,
            name=req.name,
            role="creator",
            credits=200,  # 200 free starter credits
            plan="Free Trial",
            hashed_password=hash_password(req.password),
            is_active=True,
        )
        self.repo.create(new_user)

        user_dto = User(**new_user.model_dump())
        token = create_access_token(subject=user_id, user_data=user_dto.model_dump(mode="json"))

        return AuthResponse(access_token=token, token_type="bearer", user=user_dto)

    def login(self, req: LoginRequest) -> AuthResponse:
        """Authenticate user credentials and issue an access token."""
        user = self.repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")

        user_dto = User(**user.model_dump())
        token = create_access_token(subject=user.id, user_data=user_dto.model_dump(mode="json"))

        return AuthResponse(access_token=token, token_type="bearer", user=user_dto)

    def get_current_user_profile(self, user_id: str) -> User:
        """Retrieve active user profile."""
        user = self.repo.get(user_id)
        if not user:
            raise AuthenticationError("User session not found.")
        return User(**user.model_dump())


# Singleton service instance
auth_service = AuthService()

