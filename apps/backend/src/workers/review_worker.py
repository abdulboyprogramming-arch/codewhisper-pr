# ============================================================
# CodeWhisper PR - Review Worker (Celery)
# ============================================================

from loguru import logger
import asyncio

from src.workers.celery_app import celery_app


class ReviewWorker:
    """Worker for processing reviews asynchronously."""

    @staticmethod
    @celery_app.task(name="process_review")
    def process_review(review_id: str, repository_url: str, pr_number: int, branch: str = None):
        """Process a review task."""
        logger.info(f"Processing review {review_id} for PR #{pr_number}")
        asyncio.run(ReviewWorker._process_review_async(review_id, repository_url, pr_number, branch))

    @staticmethod
    async def _process_review_async(review_id: str, repository_url: str, pr_number: int, branch: str = None):
        from src.core.database import async_session_factory
        from src.services.review_service import ReviewService

        async with async_session_factory() as db:
            try:
                review_service = ReviewService(db)
                await review_service._process_review(review_id, repository_url, pr_number, branch)
                logger.info(f"Review {review_id} processed successfully")
            except Exception as e:
                logger.error(f"Review {review_id} processing failed: {str(e)}")
                raise
