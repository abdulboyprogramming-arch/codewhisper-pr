# ============================================================
# CodeWhisper PR - Team Model
# ============================================================

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.core.database import Base


class Team(Base):
    """Team model belonging to an organization."""

    __tablename__ = "teams"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    organization = relationship("Organization", back_populates="teams")
    memberships = relationship("TeamMembership", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team {self.name} ({self.slug})>"
