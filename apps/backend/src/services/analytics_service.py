# ============================================================
# CodeWhisper PR - Analytics Service
# ============================================================

from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from src.models.review import Review
from src.models.token_usage import TokenUsage
from src.models.analytics import Analytics


class AnalyticsService:
    """Service for analytics operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self, user_id: str) -> Dict[str, Any]:
        """Get dashboard statistics for a user."""
        total_reviews = await self.db.scalar(
            select(func.count()).select_from(Review).where(Review.user_id == user_id)
        ) or 0

        total_saved = await self.db.scalar(
            select(func.sum(TokenUsage.tokens_saved))
            .join(Review)
            .where(Review.user_id == user_id)
        ) or 0

        avg_savings = await self.db.scalar(
            select(func.avg(TokenUsage.savings_percentage))
            .join(Review)
            .where(Review.user_id == user_id)
        ) or 0

        total_cost = await self.db.scalar(
            select(func.sum(TokenUsage.cost_saved))
            .join(Review)
            .where(Review.user_id == user_id)
        ) or 0

        recent_reviews_query = (
            select(Review)
            .where(Review.user_id == user_id)
            .order_by(Review.created_at.desc())
            .limit(5)
        )
        recent_reviews_result = await self.db.execute(recent_reviews_query)
        recent_reviews = recent_reviews_result.scalars().all()

        daily_stats = await self._get_daily_stats(user_id)
        top_categories = await self._get_top_categories(user_id)

        return {
            "total_reviews": total_reviews,
            "total_tokens_saved": int(total_saved),
            "average_savings_percentage": float(avg_savings or 0),
            "total_cost_saved": float(total_cost or 0),
            "recent_reviews": [
                {
                    "id": r.id,
                    "pr_number": r.pr_number,
                    "repository_name": r.repository_name,
                    "status": r.status,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "tokens_saved_percentage": r.tokens_saved_percentage,
                }
                for r in recent_reviews
            ],
            "daily_stats": daily_stats,
            "top_categories": top_categories,
        }

    async def _get_daily_stats(self, user_id: str) -> List[Dict[str, Any]]:
        """Get daily statistics for the last 7 days."""
        stats = []

        for i in range(6, -1, -1):
            date = datetime.utcnow().date() - timedelta(days=i)
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())

            reviews_result = await self.db.execute(
                select(func.count())
                .select_from(Review)
                .where(
                    and_(
                        Review.user_id == user_id,
                        Review.created_at >= start,
                        Review.created_at <= end,
                    )
                )
            )
            count = reviews_result.scalar() or 0

            tokens_result = await self.db.execute(
                select(func.sum(TokenUsage.tokens_saved))
                .join(Review)
                .where(
                    and_(
                        Review.user_id == user_id,
                        Review.created_at >= start,
                        Review.created_at <= end,
                    )
                )
            )
            tokens_saved = tokens_result.scalar() or 0

            stats.append({
                "date": date.isoformat(),
                "reviews_count": count,
                "tokens_saved": int(tokens_saved),
                "savings_percentage": 0 if count == 0 else round(float(tokens_saved / count), 2) if tokens_saved > 0 else 0,
            })

        return stats

    async def _get_top_categories(self, user_id: str) -> List[Dict[str, Any]]:
        """Get top review categories."""
        reviews_result = await self.db.execute(
            select(Review)
            .where(
                and_(
                    Review.user_id == user_id,
                    Review.status == "completed",
                    Review.issues_found.isnot(None),
                )
            )
        )
        reviews = reviews_result.scalars().all()

        category_counts = {}

        for review in reviews:
            if review.issues_found:
                for issue in review.issues_found:
                    category = issue.get("category", "other")
                    category_counts[category] = category_counts.get(category, 0) + 1

        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        total = sum(count for _, count in sorted_categories)

        return [
            {
                "category": cat,
                "count": count,
                "percentage": round((count / total) * 100, 1) if total > 0 else 0,
            }
            for cat, count in sorted_categories
        ]

    async def get_token_savings_trend(self, user_id: str, days: int) -> Dict[str, Any]:
        """Get token savings trend over time."""
        labels = []
        values = []

        for i in range(days - 1, -1, -1):
            date = datetime.utcnow().date() - timedelta(days=i)
            labels.append(date.strftime("%Y-%m-%d"))

            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())

            avg_result = await self.db.execute(
                select(func.avg(Review.tokens_saved_percentage))
                .where(
                    and_(
                        Review.user_id == user_id,
                        Review.created_at >= start,
                        Review.created_at <= end,
                        Review.status == "completed",
                    )
                )
            )
            avg = avg_result.scalar() or 0
            values.append(float(avg))

        return {"labels": labels, "values": values, "period": f"{days}d"}

    async def get_review_distribution(self, user_id: str) -> Dict[str, Any]:
        """Get review category distribution."""
        categories = await self._get_top_categories(user_id)

        return {
            "labels": [cat["category"] for cat in categories],
            "values": [cat["count"] for cat in categories],
            "percentages": [cat["percentage"] for cat in categories],
        }

    async def get_analytics_overview(
        self, user_id: str, period: str = "weekly"
    ) -> Dict[str, Any]:
        """Get comprehensive analytics overview."""
        days_map = {"daily": 1, "weekly": 7, "monthly": 30}
        days = days_map.get(period, 7)

        start_date = datetime.utcnow() - timedelta(days=days)

        stats_result = await self.db.execute(
            select(
                func.count(Review.id).label("total_reviews"),
                func.sum(TokenUsage.tokens_saved).label("tokens_saved"),
                func.sum(Review.original_tokens).label("original_tokens"),
                func.sum(Review.optimized_tokens).label("optimized_tokens"),
                func.avg(TokenUsage.savings_percentage).label("avg_savings"),
                func.sum(TokenUsage.cost_saved).label("cost_saved"),
            )
            .select_from(Review)
            .join(TokenUsage)
            .where(
                and_(
                    Review.user_id == user_id,
                    Review.created_at >= start_date,
                )
            )
        )
        stats = stats_result.first()

        return {
            "user_id": user_id,
            "period": period,
            "total_reviews": stats.total_reviews or 0,
            "total_tokens_saved": int(stats.tokens_saved or 0),
            "total_original_tokens": int(stats.original_tokens or 0),
            "total_optimized_tokens": int(stats.optimized_tokens or 0),
            "average_savings_percentage": float(stats.avg_savings or 0),
            "total_cost_saved": float(stats.cost_saved or 0),
            "date_range": {
                "start": start_date.isoformat(),
                "end": datetime.utcnow().isoformat(),
            },
            "generated_at": datetime.utcnow().isoformat(),
        }
