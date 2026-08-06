# ============================================================
# CodeWhisper PR - API Dependencies
# ============================================================

from typing import Callable
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.core.database import get_db
from src.services.auth_service import AuthService
from src.services.rbac_service import RBACService
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()


def require_permission(permission_code: str):
    async def _dep(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)):
        auth = AuthService(db)
        user = await auth.verify_token(credentials.credentials)
        rbac = RBACService(db)
        ok = await rbac.user_has_permission(user.id, permission_code, organization_id=user.organization_id)
        if not ok:
            raise HTTPException(status_code=403, detail="Forbidden")
        return True

    return _dep
