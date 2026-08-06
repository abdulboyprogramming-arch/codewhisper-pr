# ============================================================
# CodeWhisper PR - Security Routes
# ============================================================

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.database import get_db
from src.services.auth_service import AuthService
from src.services.security_service import SecurityService

router = APIRouter()
security = HTTPBearer()


@router.post("/audit")
async def run_audit(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        auth = AuthService(db)
        user = await auth.verify_token(credentials.credentials)

        svc = SecurityService(db)

        # Run in background
        background_tasks.add_task(svc.run_dependency_audit, user.id)

        return {"status": "scheduled"}

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Failed to schedule security audit")
