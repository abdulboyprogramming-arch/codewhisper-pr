# ============================================================
# CodeWhisper PR - Auth API Integration Tests
# ============================================================

import pytest
from src.main import app


@pytest.mark.integration
class TestAuthAPI:

    async def test_register(self, db_session, client):
        response = await client.post("/api/v1/auth/register", json={
            "email": "apiuser@example.com",
            "username": "apiuser",
            "password": "password123",
            "full_name": "API User",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "apiuser@example.com"
        assert data["username"] == "apiuser"

    async def test_login(self, db_session, client):
        await client.post("/api/v1/auth/register", json={
            "email": "loginuser@example.com",
            "username": "loginuser",
            "password": "password123",
        })

        response = await client.post("/api/v1/auth/login", json={
            "email": "loginuser@example.com",
            "password": "password123",
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, db_session, client):
        await client.post("/api/v1/auth/register", json={
            "email": "wrongpass@example.com",
            "username": "wrongpass",
            "password": "password123",
        })

        response = await client.post("/api/v1/auth/login", json={
            "email": "wrongpass@example.com",
            "password": "wrongpassword",
        })

        assert response.status_code == 401

    async def test_get_current_user(self, db_session, client):
        await client.post("/api/v1/auth/register", json={
            "email": "current@example.com",
            "username": "currentuser",
            "password": "password123",
        })

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "current@example.com",
            "password": "password123",
        })

        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "current@example.com"

    async def test_unauthorized_access(self, db_session, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
