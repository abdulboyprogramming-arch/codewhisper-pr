# ============================================================
# CodeWhisper PR - User Model
# ============================================================

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.core.database import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)

    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    paritok_api_key = Column(String(255), nullable=True)

    total_tokens_saved = Column(Integer, default=0)
    total_reviews_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    current_organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)

    reviews = relationship("Review", back_populates="user", lazy="dynamic")
    token_usage = relationship("TokenUsage", back_populates="user", lazy="dynamic")
    repositories = relationship("Repository", back_populates="user", lazy="dynamic")
    analytics = relationship("Analytics", back_populates="user", lazy="dynamic")

    organization_memberships = relationship(
        "OrganizationMembership",
        back_populates="user",
        foreign_keys="OrganizationMembership.user_id",
        cascade="all, delete-orphan",
    )
    team_memberships = relationship(
        "TeamMembership",
        back_populates="user",
        foreign_keys="TeamMembership.user_id",
        cascade="all, delete-orphan",
    )
    notifications = relationship("Notification", back_populates="user")
    webhook_endpoints = relationship("WebhookEndpoint", back_populates="creator")

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"
