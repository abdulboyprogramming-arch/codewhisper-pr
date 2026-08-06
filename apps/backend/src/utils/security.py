# ============================================================
# CodeWhisper PR - Security Utilities
# ============================================================

import bcrypt
from typing import Optional

from src.core.config import settings


class PasswordHasher:
    """Password hashing utility backed by bcrypt."""

    def __init__(self, rounds: Optional[int] = None):
        self.rounds = rounds or settings.BCRYPT_ROUNDS

    def hash(self, password: str) -> str:
        """Hash a password using bcrypt."""
        if not isinstance(password, str):
            raise TypeError("password must be a string")
        salt = bcrypt.gensalt(rounds=self.rounds)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against a bcrypt hash."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except (ValueError, TypeError):
            return False


pwd_context = PasswordHasher()
