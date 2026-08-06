# ============================================================
# CodeWhisper PR - Database Integration Tests
# ============================================================

import pytest
from sqlalchemy import select
from src.models.user import User
from src.models.review import Review, ReviewStatus
from src.models.token_usage import TokenUsage


@pytest.mark.integration
class TestDatabase:

    async def test_create_user(self, db_session):
        user = User(
            id="test-db-id-123",
            email="db_test@example.com",
            username="db_test_user",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()

        result = await db_session.execute(
            select(User).where(User.email == "db_test@example.com")
        )
        db_user = result.scalar_one()

        assert db_user is not None
        assert db_user.email == "db_test@example.com"
        assert db_user.username == "db_test_user"

    async def test_create_review(self, db_session, test_user):
        review = Review(
            user_id=test_user.id,
            repository_url="https://github.com/test/repo",
            repository_name="test-repo",
            pr_number=1,
            status=ReviewStatus.PENDING,
        )
        db_session.add(review)
        await db_session.commit()

        result = await db_session.execute(
            select(Review).where(Review.pr_number == 1)
        )
        db_review = result.scalar_one()

        assert db_review is not None
        assert db_review.user_id == test_user.id
        assert db_review.pr_number == 1
        assert db_review.status == ReviewStatus.PENDING

    async def test_token_usage_relationship(self, db_session, test_user, test_review):
        token_usage = TokenUsage(
            user_id=test_user.id,
            review_id=test_review.id,
            original_tokens=15000,
            optimized_tokens=3900,
            tokens_saved=11100,
            savings_percentage=74.0,
        )
        db_session.add(token_usage)
        await db_session.commit()

        result = await db_session.execute(
            select(TokenUsage).where(TokenUsage.review_id == test_review.id)
        )
        db_usage = result.scalar_one()

        assert db_usage is not None
        assert db_usage.tokens_saved == 11100
        assert db_usage.savings_percentage == 74.0
