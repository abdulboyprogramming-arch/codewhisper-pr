# ============================================================
# CodeWhisper PR - Main Application Entry Point
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.routes import auth, reviews, analytics, health
from src.api.routes import webhooks
from src.api.routes import organizations
from src.api.routes import rbac
from src.services.rbac_service import seed_default_permissions
from src.core.database import async_session_factory
from src.api.routes import security
from src.core.config import settings
from src.core.database import engine, async_session_factory
from src.core.logger import setup_logging
from src.models import Base

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CodeWhisper PR Backend...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed core RBAC permissions and admin role
    async with async_session_factory() as session:
        await seed_default_permissions(session)

    logger.info("Database initialized")
    yield

    logger.info("Shutting down...")
    await engine.dispose()


app = FastAPI(
    title="CodeWhisper PR API",
    description="Token-efficient AI code review service powered by Paritok",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(organizations.router, prefix="/api/v1/orgs", tags=["organizations"])
app.include_router(rbac.router, prefix="/api/v1/rbac", tags=["rbac"])
app.include_router(security.router, prefix="/api/v1/security", tags=["security"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to CodeWhisper PR API",
        "docs": "/api/docs",
        "status": "operational",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
