# ============================================================
# CodeWhisper PR - RBAC Service
# ============================================================

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.role import Permission, RolePermission, Role
from src.models.role import UserRole
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import uuid


async def seed_default_permissions(db: AsyncSession):
    """Ensure core permissions and an admin role exist."""
    svc = RBACService(db)
    # Define core permissions
    core_perms = [
        {"code": "org.manage", "name": "Manage Organization", "category": "org"},
        {"code": "rbac.manage", "name": "Manage Roles & Permissions", "category": "admin"},
        {"code": "reviews.create", "name": "Create Reviews", "category": "reviews"},
    ]

    for p in core_perms:
        await svc.ensure_permission(p["code"], p["name"], p.get("category", "general"))

    # Ensure admin role exists and has rbac.manage
    admin_role = await svc.ensure_role("Admin", is_system=True)
    await svc.ensure_role_has_permission(admin_role.id, "rbac.manage")



class RBACService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def user_has_permission(self, user_id: str, permission_code: str, organization_id: Optional[str] = None) -> bool:
        # Check direct user roles within scope
        # Find roles assigned to user in the organization or global
        q = select(UserRole).where(UserRole.user_id == user_id)
        if organization_id:
            q = q.where((UserRole.organization_id == organization_id) | (UserRole.organization_id == None))

        result = await self.db.execute(q)
        user_roles = result.scalars().all()

        if not user_roles:
            return False

        # For each role, check if the permission exists
        role_ids = [ur.role_id for ur in user_roles]
        if not role_ids:
            return False

        rp_q = select(RolePermission).where(RolePermission.role_id.in_(role_ids))
        rp_result = await self.db.execute(rp_q)
        role_perms = rp_result.scalars().all()

        perm_ids = [rp.permission_id for rp in role_perms]
        if not perm_ids:
            return False

        p_q = select(Permission).where(Permission.id.in_(perm_ids), Permission.code == permission_code)
        p_result = await self.db.execute(p_q)
        perm = p_result.scalar_one_or_none()
        return perm is not None

    async def ensure_permission(self, code: str, name: str, category: str = "general") -> Permission:
        result = await self.db.execute(select(Permission).where(Permission.code == code))
        p = result.scalar_one_or_none()
        if p:
            return p
        perm = Permission(id=str(uuid.uuid4()), code=code, name=name, category=category)
        self.db.add(perm)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
        await self.db.refresh(perm)
        return perm

    async def ensure_role(self, name: str, is_system: bool = False, organization_id: Optional[str] = None) -> Role:
        q = select(Role).where(Role.name == name)
        if organization_id:
            q = q.where(Role.organization_id == organization_id)
        result = await self.db.execute(q)
        r = result.scalar_one_or_none()
        if r:
            return r
        role = Role(id=str(uuid.uuid4()), name=name, is_system=is_system, organization_id=organization_id)
        self.db.add(role)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
        await self.db.refresh(role)
        return role

    async def ensure_role_has_permission(self, role_id: str, permission_code: str) -> None:
        # find permission
        p_res = await self.db.execute(select(Permission).where(Permission.code == permission_code))
        perm = p_res.scalar_one_or_none()
        if not perm:
            return
        # check existing RolePermission
        rp_res = await self.db.execute(select(RolePermission).where(RolePermission.role_id == role_id, RolePermission.permission_id == perm.id))
        rp = rp_res.scalar_one_or_none()
        if rp:
            return
        rp = RolePermission(id=str(uuid.uuid4()), role_id=role_id, permission_id=perm.id)
        self.db.add(rp)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
        return

    async def assign_role_to_user(self, user_id: str, role_id: str, organization_id: Optional[str] = None) -> UserRole:
        ur = UserRole(id=str(uuid.uuid4()), user_id=user_id, role_id=role_id, organization_id=organization_id)
        self.db.add(ur)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
        await self.db.refresh(ur)
        return ur
