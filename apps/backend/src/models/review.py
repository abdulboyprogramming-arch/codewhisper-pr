# ============================================================
# CodeWhisper PR - Review Model
# ============================================================

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class ReviewStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Review(Base):
    """Review model."""

    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=True, index=True)
    repository_id = Column(String(36), ForeignKey("repositories.id"), nullable=True, index=True)

    repository_url = Column(String(500), nullable=False)
    repository_name = Column(String(200), nullable=False)
    pr_number = Column(Integer, nullable=False, index=True)
    pr_title = Column(String(500), nullable=True)
    pr_description = Column(Text, nullable=True)

    status = Column(String(20), default=ReviewStatus.PENDING, index=True)
    diff_content = Column(Text, nullable=True)
    affected_files = Column(JSON, nullable=True)

    original_tokens = Column(Integer, nullable=True)
    optimized_tokens = Column(Integer, nullable=True)
    tokens_saved_percentage = Column(Float, nullable=True)
    optimization_time_ms = Column(Integer, nullable=True)

    review_output = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    issues_found = Column(JSON, nullable=True)

    model_used = Column(String(100), nullable=True)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4000)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="reviews")
    organization = relationship("Organization", back_populates="reviews")
    team = relationship("Team")
    repository = relationship("Repository", back_populates="reviews")
    token_usage = relationship("TokenUsage", back_populates="review", uselist=False)
    notifications = relationship("Notification", back_populates="review", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Review {self.repository_name}#{self.pr_number} ({self.status})>"
