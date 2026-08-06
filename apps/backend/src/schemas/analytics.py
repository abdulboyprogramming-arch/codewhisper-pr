# ============================================================
# CodeWhisper PR - Analytics Schemas
# ============================================================

from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class DashboardStats(BaseModel):
    total_reviews: int
    total_tokens_saved: int
    average_savings_percentage: float
    total_cost_saved: float
    recent_reviews: List[Dict[str, Any]]
    daily_stats: List[Dict[str, Any]]
    top_categories: List[Dict[str, Any]]


class TokenSavingsTrend(BaseModel):
    labels: List[str]
    values: List[float]
    period: str


class ReviewDistribution(BaseModel):
    labels: List[str]
    values: List[int]
    percentages: List[float]


class AnalyticsResponse(BaseModel):
    user_id: str
    period: str
    total_reviews: int
    total_tokens_saved: int
    total_original_tokens: int
    total_optimized_tokens: int
    average_savings_percentage: float
    total_cost_saved: float
    date_range: Dict[str, datetime]
    generated_at: datetime
