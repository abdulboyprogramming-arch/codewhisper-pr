# ============================================================
# CodeWhisper PR - Repository Model
# ============================================================

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.core.database import Base


class Repository(Base):
    """Repository model."""

    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=True, index=True)

    url = Column(String(500), nullable=False)
    name = Column(String(200), nullable=False)
    full_name = Column(String(300), nullable=False)
    default_branch = Column(String(100), nullable=True)
    is_private = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="repositories")
    organization = relationship("Organization", back_populates="repositories")
    team = relationship("Team")
    reviews = relationship("Review", back_populates="repository")

    def __repr__(self):
        return f"<Repository {self.full_name}>"
