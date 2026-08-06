# ============================================================
# CodeWhisper PR - Analytics Routes
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.database import get_db
from src.schemas.analytics import (
    AnalyticsResponse,
    DashboardStats,
    TokenSavingsTrend,
    ReviewDistribution,
)
from src.services.analytics_service import AnalyticsService
from src.services.auth_service import AuthService
from src.core.exceptions import AuthenticationError
from src.services.architecture_service import ArchitectureService

router = APIRouter()
security = HTTPBearer()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        analytics_service = AnalyticsService(db)
        stats = await analytics_service.get_dashboard_stats(user.id)
        return stats

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Get dashboard stats failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")


@router.get("/token-savings", response_model=TokenSavingsTrend)
async def get_token_savings_trend(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        analytics_service = AnalyticsService(db)
        trend = await analytics_service.get_token_savings_trend(user.id, days)
        return trend

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Get token savings trend failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get token savings trend")


@router.get("/review-distribution", response_model=ReviewDistribution)
async def get_review_distribution(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        analytics_service = AnalyticsService(db)
        distribution = await analytics_service.get_review_distribution(user.id)
        return distribution

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Get review distribution failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get review distribution")


@router.get("/overview", response_model=AnalyticsResponse)
async def get_analytics_overview(
    period: str = Query("weekly", pattern="^(daily|weekly|monthly)$"),
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_analytics_overview(user.id, period)
        return analytics

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Get analytics overview failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics overview")


@router.post("/architecture")
async def analyze_architecture(
    repository_url: str,
    branch: str = "main",
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        arch = ArchitectureService()
        result = arch.analyze_repository(repository_url, branch)
        return result

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Failed to analyze architecture")
