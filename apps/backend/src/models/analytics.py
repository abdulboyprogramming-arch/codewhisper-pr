# ============================================================
# CodeWhisper PR - Analytics Model
# ============================================================

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class Analytics(Base):
    """Analytics model for aggregated metrics."""

    __tablename__ = "analytics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)

    period = Column(String(20), nullable=False, index=True)
    total_reviews = Column(Integer, nullable=False)
    total_tokens_saved = Column(Integer, nullable=False)
    total_original_tokens = Column(Integer, nullable=False)
    total_optimized_tokens = Column(Integer, nullable=False)
    average_savings_percentage = Column(Float, nullable=False)
    total_cost_saved = Column(Float, nullable=True)

    date_range = Column(JSON, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="analytics")

    def __repr__(self):
        return f"<Analytics {self.period} - {self.total_reviews} reviews>"
