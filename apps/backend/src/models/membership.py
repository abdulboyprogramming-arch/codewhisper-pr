# ============================================================
# CodeWhisper PR - Membership Models
# ============================================================

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from src.core.database import Base


class OrganizationMembership(Base):
    """Many-to-many link between users and organizations with roles."""

    __tablename__ = "organization_memberships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(
        String(36), ForeignKey("organizations.id"), nullable=False, index=True
    )
    role = Column(String(20), nullable=False, default="member")

    status = Column(String(20), nullable=False, default="active")
    invited_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    joined_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", foreign_keys=[user_id], back_populates="organization_memberships")
    inviter = relationship("User", foreign_keys=[invited_by])

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_org_membership_user_org"),
    )

    def __repr__(self):
        return f"<OrganizationMembership user={self.user_id} org={self.organization_id} role={self.role}>"


class TeamMembership(Base):
    """Many-to-many link between users and teams with roles."""

    __tablename__ = "team_memberships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False, default="member")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    team = relationship("Team", back_populates="memberships")
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="uq_team_membership_user_team"),
    )

    def __repr__(self):
        return f"<TeamMembership user={self.user_id} team={self.team_id} role={self.role}>"
