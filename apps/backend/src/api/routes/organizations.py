# ============================================================
# CodeWhisper PR - Organization Routes
# ============================================================

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.database import get_db
from src.services.auth_service import AuthService
from src.services.organization_service import OrganizationService
from src.api.deps import require_permission

router = APIRouter()
security = HTTPBearer()


@router.post("/")
async def create_organization(payload: Dict[str, Any], db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        auth = AuthService(db)
        user = await auth.verify_token(credentials.credentials)

        svc = OrganizationService(db)
        org = await svc.create_organization(
            name=payload.get("name"),
            slug=payload.get("slug"),
            domain=payload.get("domain"),
            creator_id=user.id,
        )

        return {"id": org.id, "name": org.name, "slug": org.slug}

    except Exception as e:
        logger.exception(f"Failed to create organization: {e}")
        raise HTTPException(status_code=500, detail="Failed to create organization")


@router.get("/")
async def list_organizations(db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        auth = AuthService(db)
        user = await auth.verify_token(credentials.credentials)

        svc = OrganizationService(db)
        orgs = await svc.list_organizations_for_user(user.id)

        return [{"id": o.id, "name": o.name, "slug": o.slug} for o in orgs]

    except Exception as e:
        logger.exception(f"Failed to list organizations: {e}")
        raise HTTPException(status_code=500, detail="Failed to list organizations")


@router.post("/{org_id}/teams")
async def create_team(org_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security), _perm: bool = Depends(require_permission("org.manage"))):
    try:
        auth = AuthService(db)
        user = await auth.verify_token(credentials.credentials)

        svc = OrganizationService(db)
        org = await svc.get_organization(org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # TODO: check membership/role before allowing team creation (owner/admin only)

        team = await svc.create_team(organization_id=org.id, name=payload.get("name"), slug=payload.get("slug"), description=payload.get("description"))
        return {"id": team.id, "name": team.name}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to create team: {e}")
        raise HTTPException(status_code=500, detail="Failed to create team")


@router.post("/{org_id}/members")
async def add_member(org_id: str, payload: Dict[str, Any], db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security), _perm: bool = Depends(require_permission("org.manage"))):
    try:
        auth = AuthService(db)
        user = await auth.verify_token(credentials.credentials)

        # TODO: ensure user has permission to invite

        svc = OrganizationService(db)
        membership = await svc.add_member_to_org(organization_id=org_id, user_id=payload.get("user_id"), role=payload.get("role", "member"))
        return {"id": membership.id, "user_id": membership.user_id, "role": membership.role}

    except Exception as e:
        logger.exception(f"Failed to add member: {e}")
        raise HTTPException(status_code=500, detail="Failed to add member")
