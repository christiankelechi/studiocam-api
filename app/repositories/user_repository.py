"""User Repository implementing User Data Access."""

from typing import List, Optional
from app.core.security import hash_password
from app.models.auth import User, UserInDB
from app.repositories.base import ThreadSafeInMemoryRepository


class UserRepository(ThreadSafeInMemoryRepository[UserInDB]):
    """Thread-safe Repository for Users."""

    def __init__(self):
        super().__init__()
        # Seed default test user matching frontend session
        seed_user = UserInDB(
            id="usr_christian_001",
            email="christian@studiocam.ai",
            name="Christian Eze",
            role="creator",
            credits=450,
            plan="Pro Studio",
            avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80",
            hashed_password=hash_password("password123"),
            is_active=True,
        )
        self.create(seed_user)

    def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Find user by email address."""
        with self._lock:
            for user in self._storage.values():
                if user.email.lower() == email.lower():
                    return user
            return None

    def deduct_credits(self, user_id: str, amount: int) -> int:
        """Deduct credits from user account, returning remaining balance."""
        with self._lock:
            user = self.get(user_id)
            if not user:
                return 0
            user.credits = max(0, user.credits - amount)
            return user.credits

    def add_credits(self, user_id: str, amount: int) -> int:
        """Add credits to user account, returning new balance."""
        with self._lock:
            user = self.get(user_id)
            if not user:
                return 0
            user.credits += amount
            return user.credits


# Global singleton instance
user_repository = UserRepository()

