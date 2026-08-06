# ============================================================
# CodeWhisper PR - Review Service Tests
# ============================================================

import pytest
from src.models.review import Review, ReviewStatus


@pytest.mark.unit
class TestReviewService:

    async def test_list_reviews(self, db_session, test_user, test_review):
        from src.services.review_service import ReviewService

        service = ReviewService(db_session)
        reviews, total = await service.list_reviews(
            user_id=test_user.id,
            limit=50,
            offset=0,
        )

        assert total >= 1
        assert len(reviews) >= 1
        assert reviews[0].user_id == test_user.id

    async def test_list_reviews_with_status_filter(self, db_session, test_user, test_review):
        from src.services.review_service import ReviewService

        service = ReviewService(db_session)
        reviews, total = await service.list_reviews(
            user_id=test_user.id,
            limit=50,
            offset=0,
            status="completed",
        )

        assert total >= 1
        for review in reviews:
            assert review.status == "completed"

    async def test_get_review(self, db_session, test_user, test_review):
        from src.services.review_service import ReviewService

        service = ReviewService(db_session)
        review = await service.get_review(test_review.id, test_user.id)

        assert review is not None
        assert review.id == test_review.id
        assert review.pr_number == 1

    async def test_get_review_not_found(self, db_session, test_user):
        from src.services.review_service import ReviewService

        service = ReviewService(db_session)
        review = await service.get_review("non-existent-id", test_user.id)

        assert review is None

    async def test_get_review_status(self, db_session, test_user, test_review):
        from src.services.review_service import ReviewService

        service = ReviewService(db_session)
        status_result = await service.get_review_status(test_review.id, test_user.id)

        assert status_result is not None
        assert status_result["status"] == "completed"
        assert status_result["progress"] == 100

    async def test_get_review_status_not_found(self, db_session, test_user):
        from src.services.review_service import ReviewService

        service = ReviewService(db_session)
        status_result = await service.get_review_status("non-existent-id", test_user.id)

        assert status_result is None

    async def test_calculate_cost_saved(self, db_session):
        from src.services.review_service import ReviewService

        service = ReviewService(db_session)
        cost = service._calculate_cost_saved(15000, 3900)

        assert cost > 0
        assert cost < (15000 / 1_000_000) * 3.0
