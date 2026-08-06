# ============================================================
# CodeWhisper PR - RBAC Models (Roles & Permissions)
# ============================================================

from datetime import datetime
import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.core.database import Base


class Permission(Base):
    """A granular permission code within the system."""

    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=False, default="general")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Permission {self.code}>"


class Role(Base):
    """A role that aggregates permissions. System roles are globally available."""

    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

    organization = relationship("Organization")

    def __repr__(self):
        return f"<Role {self.name} system={self.is_system}>"


class RolePermission(Base):
    """Assignment of a permission to a role."""

    __tablename__ = "role_permissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False, index=True)
    permission_id = Column(String(36), ForeignKey("permissions.id"), nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    def __repr__(self):
        return f"<RolePermission role={self.role_id} permission={self.permission_id}>"


class UserRole(Base):
    """Direct assignment of a role to a user within a scope."""

    __tablename__ = "user_roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    scope = Column(String(50), nullable=False, default="organization")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    role = relationship("Role")
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "scope", "organization_id",
                         name="uq_user_role_scope"),
    )

    def __repr__(self):
        return f"<UserRole user={self.user_id} role={self.role_id} scope={self.scope}>"
