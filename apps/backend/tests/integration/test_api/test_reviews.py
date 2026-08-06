# ============================================================
# CodeWhisper PR - Reviews API Integration Tests
# ============================================================

import pytest


@pytest.mark.integration
class TestReviewsAPI:

    async def _get_auth_token(self, client):
        await client.post("/api/v1/auth/register", json={
            "email": "reviews_test@example.com",
            "username": "reviews_test",
            "password": "password123",
        })
        response = await client.post("/api/v1/auth/login", json={
            "email": "reviews_test@example.com",
            "password": "password123",
        })
        return response.json()["access_token"]

    async def test_create_review(self, db_session, client):
        token = await self._get_auth_token(client)

        response = await client.post(
            "/api/v1/reviews/create",
            json={
                "repository_url": "https://github.com/test/repo",
                "pr_number": 1,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["repository_url"] == "https://github.com/test/repo"
        assert data["pr_number"] == 1
        assert data["status"] == "pending"

    async def test_get_review(self, db_session, test_review, client):
        token = await self._get_auth_token(client)

        response = await client.get(
            f"/api/v1/reviews/{test_review.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    async def test_list_reviews(self, db_session, test_review, client):
        token = await self._get_auth_token(client)

        response = await client.get(
            "/api/v1/reviews/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    async def test_review_unauthorized(self, db_session, client):
        response = await client.post(
            "/api/v1/reviews/create",
            json={
                "repository_url": "https://github.com/test/repo",
                "pr_number": 1,
            },
        )

        assert response.status_code == 401
