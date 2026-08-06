# ============================================================
# CodeWhisper PR - Token Usage Model
# ============================================================

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class TokenUsage(Base):
    """Token usage model for tracking optimization savings."""

    __tablename__ = "token_usage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    review_id = Column(String(36), ForeignKey("reviews.id"), nullable=False, unique=True)

    original_tokens = Column(Integer, nullable=False)
    optimized_tokens = Column(Integer, nullable=False)
    tokens_saved = Column(Integer, nullable=False)
    savings_percentage = Column(Float, nullable=False)

    model_used = Column(String(100), nullable=True)
    cost_saved = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="token_usage")
    review = relationship("Review", back_populates="token_usage")

    def __repr__(self):
        return f"<TokenUsage {self.tokens_saved} tokens saved ({self.savings_percentage:.1f}%)>"
