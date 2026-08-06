# ============================================================
# CodeWhisper PR - Review Service
# ============================================================

from typing import Dict, Any, Optional, List, Tuple
import time
import uuid
from datetime import datetime
from fastapi import BackgroundTasks

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.services.git_service import GitService
from src.services.paritok_service import ParitokService
from src.services.llm_service import LLMService
from src.services.token_optimizer import TokenOptimizer
from src.services.ast_analyzer import ASTAnalyzer
from src.models.review import Review
from src.models.token_usage import TokenUsage
from src.models.user import User
from src.core.exceptions import ReviewError
from src.core.config import settings
from src.services.notification_service import NotificationService
from src.core.cache import get_redis


class ReviewService:
    """Service for orchestrating code reviews."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.git_service = GitService()
        self.paritok_service = ParitokService()
        self.llm_service = LLMService()
        self.token_optimizer = TokenOptimizer(self.paritok_service)
        self.ast_analyzer = ASTAnalyzer()

    async def create_review(
        self,
        user_id: str,
        repository_url: str,
        pr_number: int,
        branch: Optional[str] = None,
        review_settings: Optional[Dict[str, Any]] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> Review:
        """Create and process a new review."""
        try:
            review = Review(
                user_id=user_id,
                repository_url=repository_url,
                pr_number=pr_number,
                repository_name=repository_url.split('/')[-1].replace('.git', ''),
                status="pending",
                temperature=review_settings.get("temperature", 0.7) if review_settings else 0.7,
                max_tokens=review_settings.get("max_tokens", 4000) if review_settings else 4000,
            )

            self.db.add(review)
            await self.db.commit()
            await self.db.refresh(review)

            if background_tasks:
                background_tasks.add_task(
                    self._process_review, review.id, repository_url, pr_number, branch, review_settings
                )
            else:
                await self._process_review(review.id, repository_url, pr_number, branch, review_settings)

            return review

        except Exception as e:
            await self.db.rollback()
            raise ReviewError(f"Review creation failed: {str(e)}")

    async def _process_review(
        self, review_id: str, repository_url: str, pr_number: int,
        branch: Optional[str] = None, review_settings: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Process a review."""
        try:
            await self._update_review_status(review_id, "processing")

            review = await self.get_review_by_id(review_id)
            if not review:
                raise ReviewError("Review not found")

            repo_path = self.git_service.clone_repository(repository_url, branch or "main")
            diff_content, affected_files = self.git_service.get_pull_request_diff(repo_path, pr_number)

            review.diff_content = diff_content
            review.affected_files = affected_files

            ast_analysis = await self.ast_analyzer.analyze_changes(affected_files, diff_content)

            optimized_context, optimization_metrics = await self.token_optimizer.optimize_diff(
                diff_content, affected_files, ast_analysis
            )

            review.original_tokens = optimization_metrics.get("original_tokens")
            review.optimized_tokens = optimization_metrics.get("optimized_tokens")
            review.tokens_saved_percentage = optimization_metrics.get("savings_percentage")
            review.optimization_time_ms = optimization_metrics.get("optimization_time_ms")

            review_output = await self.llm_service.generate_review(optimized_context, review_settings)

            review.review_output = review_output
            review.summary = review_output.get("summary")
            review.issues_found = review_output.get("issues", [])
            review.model_used = settings.LLM_MODEL
            review.status = "completed"
            review.completed_at = datetime.utcnow()

            # Create a notification for the user about review completion
            try:
                notif_service = NotificationService(self.db)
                await notif_service.create_user_notification(
                    user_id=review.user_id,
                    notif_type="review_completed",
                    payload={"review_id": review.id, "summary": review.summary},
                )
            except Exception:
                pass

            token_usage = TokenUsage(
                id=str(uuid.uuid4()),
                user_id=review.user_id,
                review_id=review.id,
                original_tokens=review.original_tokens or 0,
                optimized_tokens=review.optimized_tokens or 0,
                tokens_saved=(review.original_tokens or 0) - (review.optimized_tokens or 0),
                savings_percentage=review.tokens_saved_percentage or 0,
                model_used=review.model_used,
                cost_saved=self._calculate_cost_saved(
                    review.original_tokens or 0, review.optimized_tokens or 0
                ),
            )
            self.db.add(token_usage)

            await self._update_user_stats(review.user_id, review.tokens_saved_percentage or 0, review.original_tokens or 0, review.optimized_tokens or 0)

            await self.db.commit()

            # Invalidate cache for this review
            try:
                if settings.ENABLE_CACHING:
                    redis = get_redis()
                    await redis.delete(f"review:{review.id}")
            except Exception:
                pass


        except Exception as e:
            from loguru import logger
            logger.error(f"Review processing failed for {review_id}: {str(e)}")
            await self._update_review_status(review_id, "failed")
            await self.db.rollback()

    async def get_review(self, review_id: str, user_id: str) -> Optional[Review]:
        """Get a review by ID for a specific user."""
        result = await self.db.execute(
            select(Review).where(Review.id == review_id, Review.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_review_by_id(self, review_id: str) -> Optional[Review]:
        """Get a review by ID."""
        result = await self.db.execute(select(Review).where(Review.id == review_id))
        return result.scalar_one_or_none()

    async def list_reviews(
        self, user_id: str, limit: int = 50, offset: int = 0, status: Optional[str] = None,
    ) -> Tuple[List[Review], int]:
        """List reviews for a user."""
        query = select(Review).where(Review.user_id == user_id)

        if status:
            query = query.where(Review.status == status)

        count_query = select(func.count()).select_from(Review).where(Review.user_id == user_id)
        if status:
            count_query = count_query.where(Review.status == status)

        total = await self.db.scalar(count_query) or 0

        query = query.order_by(Review.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        reviews = result.scalars().all()

        return reviews, total

    async def get_review_status(self, review_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get review processing status."""
        result = await self.db.execute(
            select(Review).where(Review.id == review_id, Review.user_id == user_id)
        )
        review = result.scalar_one_or_none()

        if not review:
            return None

        progress = 100 if review.status == "completed" else 50 if review.status == "processing" else 0

        return {
            "status": review.status,
            "progress": progress,
            "estimated_time_remaining": None,
            "error": None if review.status != "failed" else "Review processing failed",
        }

    async def _update_review_status(self, review_id: str, status: str) -> None:
        """Update review status."""
        review = await self.get_review_by_id(review_id)
        if review:
            review.status = status
            await self.db.commit()

    async def _update_user_stats(self, user_id: str, savings_percentage: float, original_tokens: int, optimized_tokens: int) -> None:
        """Update user statistics."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user:
            user.total_reviews_count += 1
            user.total_tokens_saved += (original_tokens - optimized_tokens)
            await self.db.commit()

    def _calculate_cost_saved(self, original_tokens: int, optimized_tokens: int) -> float:
        """Calculate cost saved using approximate pricing."""
        cost_per_million = 3.0
        original_cost = (original_tokens / 1_000_000) * cost_per_million
        optimized_cost = (optimized_tokens / 1_000_000) * cost_per_million
        return max(0, original_cost - optimized_cost)

