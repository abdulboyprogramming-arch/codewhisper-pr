# ============================================================
# CodeWhisper PR - Authentication Service
# ============================================================

import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from src.models.user import User
from src.core.config import settings
from src.core.exceptions import AuthenticationError
from src.utils.security import PasswordHasher


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = PasswordHasher(rounds=settings.BCRYPT_ROUNDS)

    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        organization_id: Optional[str] = None,
        role: str = "user",
    ) -> User:
        existing = await self.db.execute(
            select(User).where((User.email == email) | (User.username == username))
        )
        if existing.scalar_one_or_none():
            raise ValueError("User with this email or username already exists")

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=self.pwd_context.hash(password),
            role=role,
            is_active=True,
            is_verified=False,
            organization_id=organization_id,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"User registered: {user.email}")
        return user

    async def authenticate_user(self, email: str, password: str) -> User:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            raise AuthenticationError("Invalid credentials")

        if not user.is_active:
            raise AuthenticationError("User account is disabled")

        if not self.pwd_context.verify(password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")

        user.last_login = datetime.utcnow()
        await self.db.commit()

        return user

    async def create_tokens(self, user: User, additional_claims: Optional[Dict[str, any]] = None) -> Dict[str, any]:
        access_token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "organization_id": user.organization_id,
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        if additional_claims:
            access_token_data.update(additional_claims)
        access_token = jwt.encode(
            access_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        refresh_token_data = {
            "sub": user.id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        }
        refresh_token = jwt.encode(
            refresh_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def verify_token(self, token: str) -> User:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")

            if not user_id:
                raise AuthenticationError("Invalid token")

            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                raise AuthenticationError("User not found")

            if not user.is_active:
                raise AuthenticationError("User account is disabled")

            return user

        except JWTError as e:
            raise AuthenticationError(f"Token verification failed: {str(e)}")

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, any]:
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid refresh token")

            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationError("Invalid token")

            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                raise AuthenticationError("User not found")

            return await self.create_tokens(user)

        except JWTError as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}")

    async def get_user_from_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")

            result = await self.db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

        except JWTError:
            return None

    async def revoke_token(self, token: str) -> None:
        logger.info(f"Token revoked (simulated): {token[:20]}...")
