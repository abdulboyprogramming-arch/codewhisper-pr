# ============================================================
# CodeWhisper PR - Analytics Worker (Celery)
# ============================================================

from loguru import logger
import asyncio

from src.workers.celery_app import celery_app


class AnalyticsWorker:
    """Worker for generating analytics."""

    @staticmethod
    @celery_app.task(name="generate_daily_analytics")
    def generate_daily_analytics():
        """Generate daily analytics."""
        logger.info("Generating daily analytics")
        asyncio.run(AnalyticsWorker._generate_analytics("daily"))

    @staticmethod
    @celery_app.task(name="generate_weekly_analytics")
    def generate_weekly_analytics():
        """Generate weekly analytics."""
        logger.info("Generating weekly analytics")
        asyncio.run(AnalyticsWorker._generate_analytics("weekly"))

    @staticmethod
    async def _generate_analytics(period: str):
        """Generate analytics for a specific period."""
        from datetime import datetime

        from sqlalchemy import select

        from src.core.database import async_session_factory
        from src.services.analytics_service import AnalyticsService
        from src.models.user import User
        from src.models.analytics import Analytics

        async with async_session_factory() as db:
            try:
                users_result = await db.execute(select(User))
                users = users_result.scalars().all()

                analytics_service = AnalyticsService(db)

                for user in users:
                    overview = await analytics_service.get_analytics_overview(user.id, period)

                    analytics = Analytics(
                        user_id=user.id,
                        period=period,
                        total_reviews=overview["total_reviews"],
                        total_tokens_saved=overview["total_tokens_saved"],
                        total_original_tokens=overview["total_original_tokens"],
                        total_optimized_tokens=overview["total_optimized_tokens"],
                        average_savings_percentage=overview["average_savings_percentage"],
                        total_cost_saved=overview["total_cost_saved"],
                        date_range=overview["date_range"],
                        generated_at=datetime.utcnow(),
                    )
                    db.add(analytics)

                await db.commit()
                logger.info(f"Generated {period} analytics for {len(users)} users")

            except Exception as e:
                logger.error(f"Analytics generation failed: {str(e)}")
                await db.rollback()
                raise
