# ============================================================
# CodeWhisper PR - Review Model Tests
# ============================================================

import pytest
from src.models.review import Review, ReviewStatus


@pytest.mark.unit
class TestReviewModel:

    def test_review_creation(self):
        review = Review(
            user_id="test-user-id",
            repository_url="https://github.com/test/repo",
            repository_name="test-repo",
            pr_number=1,
            pr_title="Test PR",
            status=ReviewStatus.PENDING,
        )

        assert review.user_id == "test-user-id"
        assert review.repository_url == "https://github.com/test/repo"
        assert review.repository_name == "test-repo"
        assert review.pr_number == 1
        assert review.pr_title == "Test PR"
        assert review.status == ReviewStatus.PENDING

    def test_review_repr(self):
        review = Review(
            user_id="test-user-id",
            repository_url="https://github.com/test/repo",
            repository_name="test-repo",
            pr_number=1,
            status=ReviewStatus.COMPLETED,
        )
        assert repr(review) == "<Review test-repo#1 (completed)>"

    def test_review_status_constants(self):
        assert ReviewStatus.PENDING == "pending"
        assert ReviewStatus.PROCESSING == "processing"
        assert ReviewStatus.COMPLETED == "completed"
        assert ReviewStatus.FAILED == "failed"
