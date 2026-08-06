# ============================================================
# CodeWhisper PR - RBAC Management Routes
# ============================================================

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.database import get_db
from src.services.auth_service import AuthService
from src.services.rbac_service import RBACService
from src.api.deps import require_permission

router = APIRouter()
security = HTTPBearer()


@router.get("/permissions")
async def list_permissions(db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        auth = AuthService(db)
        await auth.verify_token(credentials.credentials)

        res = await db.execute("SELECT id, code, name, category FROM permissions")
        rows = res.fetchall()
        return [{"id": r[0], "code": r[1], "name": r[2], "category": r[3]} for r in rows]
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Failed to list permissions")


@router.post("/permissions")
async def create_permission(payload: Dict[str, Any], db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security), _perm: bool = Depends(require_permission("rbac.manage"))):
    try:
        svc = RBACService(db)
        perm = await svc.ensure_permission(code=payload.get("code"), name=payload.get("name"), category=payload.get("category", "general"))
        return {"id": perm.id, "code": perm.code}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Failed to create permission")


@router.post("/roles")
async def create_role(payload: Dict[str, Any], db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security), _perm: bool = Depends(require_permission("rbac.manage"))):
    try:
        svc = RBACService(db)
        role = await svc.ensure_role(name=payload.get("name"), is_system=payload.get("is_system", False), organization_id=payload.get("organization_id"))
        return {"id": role.id, "name": role.name}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Failed to create role")


@router.post("/roles/{role_id}/permissions")
async def add_permission_to_role(role_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security), _perm: bool = Depends(require_permission("rbac.manage"))):
    try:
        svc = RBACService(db)
        await svc.ensure_role_has_permission(role_id, payload.get("permission_code"))
        return {"role_id": role_id, "permission_code": payload.get("permission_code")}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Failed to add permission to role")


@router.post("/roles/{role_id}/assign")
async def assign_role(role_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security), _perm: bool = Depends(require_permission("rbac.manage"))):
    try:
        svc = RBACService(db)
        ur = await svc.assign_role_to_user(user_id=payload.get("user_id"), role_id=role_id, organization_id=payload.get("organization_id"))
        return {"id": ur.id, "user_id": ur.user_id, "role_id": ur.role_id}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Failed to assign role to user")
