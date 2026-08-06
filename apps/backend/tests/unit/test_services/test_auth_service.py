# ============================================================
# CodeWhisper PR - Auth Service Tests
# ============================================================

import pytest
from src.core.exceptions import AuthenticationError


@pytest.mark.unit
class TestAuthService:

    async def test_register_user(self, db_session):
        from src.services.auth_service import AuthService

        service = AuthService(db_session)
        user = await service.register_user(
            email="newuser@example.com",
            username="newuser",
            password="password123",
            full_name="New User",
        )

        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.is_active is True
        assert user.hashed_password != "password123"

    async def test_register_duplicate_email(self, db_session):
        from src.services.auth_service import AuthService

        service = AuthService(db_session)
        await service.register_user(
            email="dup@example.com",
            username="user1",
            password="password123",
        )

        with pytest.raises(ValueError, match="already exists"):
            await service.register_user(
                email="dup@example.com",
                username="user2",
                password="password123",
            )

    async def test_authenticate_user(self, db_session):
        from src.services.auth_service import AuthService

        service = AuthService(db_session)
        await service.register_user(
            email="auth@example.com",
            username="authuser",
            password="password123",
        )

        user = await service.authenticate_user(
            email="auth@example.com",
            password="password123",
        )

        assert user.email == "auth@example.com"

    async def test_authenticate_wrong_password(self, db_session):
        from src.services.auth_service import AuthService

        service = AuthService(db_session)
        await service.register_user(
            email="wrong@example.com",
            username="wronguser",
            password="password123",
        )

        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            await service.authenticate_user(
                email="wrong@example.com",
                password="wrongpassword",
            )

    async def test_authenticate_inactive_user(self, db_session):
        from src.services.auth_service import AuthService
        from src.models.user import User

        service = AuthService(db_session)

        user = User(
            id="test-inactive-uuid",
            email="inactive@example.com",
            username="inactive",
            hashed_password=service.pwd_context.hash("password123"),
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()

        with pytest.raises(AuthenticationError, match="disabled"):
            await service.authenticate_user(
                email="inactive@example.com",
                password="password123",
            )

    async def test_create_tokens(self, db_session, test_user):
        from src.services.auth_service import AuthService

        service = AuthService(db_session)
        tokens = await service.create_tokens(test_user)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["expires_in"] > 0

    async def test_verify_token(self, db_session, test_user):
        from src.services.auth_service import AuthService

        service = AuthService(db_session)
        tokens = await service.create_tokens(test_user)

        user = await service.verify_token(tokens["access_token"])
        assert user.email == test_user.email

    async def test_verify_invalid_token(self, db_session):
        from src.services.auth_service import AuthService

        service = AuthService(db_session)

        with pytest.raises(AuthenticationError):
            await service.verify_token("invalid-token")

    async def test_refresh_tokens_invalid(self, db_session):
        from src.services.auth_service import AuthService

        service = AuthService(db_session)

        with pytest.raises(AuthenticationError):
            await service.refresh_tokens("invalid")

    async def test_get_user_from_token(self, db_session, test_user):
        from src.services.auth_service import AuthService

        service = AuthService(db_session)
        tokens = await service.create_tokens(test_user)

        user = await service.get_user_from_token(tokens["access_token"])
        assert user is not None
        assert user.email == test_user.email
