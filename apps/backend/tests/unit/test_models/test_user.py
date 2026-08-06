# ============================================================
# CodeWhisper PR - User Model Tests
# ============================================================

import pytest
from src.models.user import User


@pytest.mark.unit
class TestUserModel:

    def test_user_creation(self):
        user = User(
            id="test-id",
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            role="user",
            is_active=True,
            is_verified=False,
        )

        assert user.id == "test-id"
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == "user"
        assert user.is_active is True
        assert user.is_verified is False

    def test_user_repr(self):
        user = User(
            id="test-id",
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
        )
        assert repr(user) == "<User testuser (test@example.com)>"

    async def test_user_default_values(self, db_session):
        user = User(
            id="test-defaults-id",
            email="defaults@example.com",
            username="defaultuser",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.role == "user"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.total_tokens_saved == 0
        assert user.total_reviews_count == 0
