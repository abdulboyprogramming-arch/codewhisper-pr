# ============================================================
# CodeWhisper PR - Organization Model
# ============================================================

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship

from src.core.database import Base


class Organization(Base):
    """Organization model supporting multi-tenant isolation."""

    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    domain = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    memberships = relationship("OrganizationMembership", back_populates="organization", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="organization")
    repositories = relationship("Repository", back_populates="organization")

    def __repr__(self):
        return f"<Organization {self.name} ({self.slug})>"
