# ============================================================
# CodeWhisper PR - Health Check Routes
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from loguru import logger
import time
import redis
from datetime import datetime

from src.core.database import get_db
from src.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {},
    }

    try:
        start = time.time()
        await db.execute(text("SELECT 1"))
        db_latency = (time.time() - start) * 1000
        status["checks"]["database"] = {
            "status": "healthy",
            "latency_ms": round(db_latency, 2),
        }
    except Exception as e:
        status["status"] = "unhealthy"
        status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}

    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL)
        start = time.time()
        redis_client.ping()
        redis_latency = (time.time() - start) * 1000
        status["checks"]["redis"] = {
            "status": "healthy",
            "latency_ms": round(redis_latency, 2),
        }
    except Exception as e:
        status["status"] = "unhealthy"
        status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}

    status["checks"]["paritok"] = {
        "status": "unknown",
        "endpoint": settings.PARITOK_BASE_URL,
    }

    return status


@router.get("/ready")
async def readiness_check():
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    return {"status": "alive"}
