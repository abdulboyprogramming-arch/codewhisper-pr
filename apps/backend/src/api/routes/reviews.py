# ============================================================
# CodeWhisper PR - Review Routes
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from typing import Optional
from loguru import logger

from src.core.database import get_db
from src.schemas.review import (
    ReviewCreateRequest,
    ReviewResponse,
    ReviewListResponse,
    ReviewStatusResponse,
)
from src.services.review_service import ReviewService
from src.services.auth_service import AuthService
from src.core.exceptions import ReviewError, AuthenticationError
from sqlalchemy import select, or_, text
from fastapi.responses import StreamingResponse
import io
try:
    from reportlab.pdfgen import canvas
except Exception:
    canvas = None
from src.core.cache import get_redis
from src.core.config import settings
import orjson

router = APIRouter()
security = HTTPBearer()


@router.post("/create", response_model=ReviewResponse)
async def create_review(
    request: ReviewCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        review_service = ReviewService(db)
        review = await review_service.create_review(
            user_id=user.id,
            repository_url=request.repository_url,
            pr_number=request.pr_number,
            branch=request.branch,
            settings=request.settings.model_dump() if request.settings else None,
            background_tasks=background_tasks,
        )

        return ReviewResponse.model_validate(review)

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ReviewError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Review creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Review creation failed")


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        review_service = ReviewService(db)

        # Try cache
        redis = None
        key = f"review:{review_id}"
        if settings.ENABLE_CACHING:
            try:
                redis = get_redis()
                cached = await redis.get(key)
                if cached:
                    data = orjson.loads(cached)
                    return data
            except Exception:
                pass

        review = await review_service.get_review(review_id, user.id)

        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        return ReviewResponse.model_validate(review)

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get review failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get review")


@router.get("/", response_model=ReviewListResponse)
async def list_reviews(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        review_service = ReviewService(db)
        reviews, total = await review_service.list_reviews(
            user_id=user.id,
            limit=limit,
            offset=offset,
            status=status,
        )

        return ReviewListResponse(
            items=[ReviewResponse.model_validate(r) for r in reviews],
            total=total,
            page=offset // limit + 1,
            limit=limit,
            total_pages=(total + limit - 1) // limit,
        )

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"List reviews failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list reviews")


@router.get("/{review_id}/status", response_model=ReviewStatusResponse)
async def get_review_status(
    review_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        review_service = ReviewService(db)
        status_result = await review_service.get_review_status(review_id, user.id)

        if not status_result:
            raise HTTPException(status_code=404, detail="Review not found")

        return ReviewStatusResponse(
            review_id=review_id,
            status=status_result["status"],
            progress=status_result.get("progress", 0),
            estimated_time_remaining=status_result.get("estimated_time_remaining"),
            error=status_result.get("error"),
        )

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get review status failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get review status")



@router.get("/{review_id}/export")
async def export_review(
    review_id: str,
    format: str = Query("json", regex="^(json|pdf)$"),
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        review_service = ReviewService(db)
        review = await review_service.get_review(review_id, user.id)

        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        if format == "json":
            resp = ReviewResponse.model_validate(review).model_dump()
            # set cache
            if settings.ENABLE_CACHING and redis is not None:
                try:
                    await redis.set(key, orjson.dumps(resp), ex=settings.REDIS_CACHE_TTL)
                except Exception:
                    pass
            return resp

        # PDF
        if format == "pdf":
            if canvas is None:
                raise HTTPException(status_code=500, detail="PDF generation dependency not available")

            buf = io.BytesIO()
            c = canvas.Canvas(buf)
            c.setFont("Helvetica", 12)
            c.drawString(40, 800, f"Review: {review.repository_name} #{review.pr_number}")
            c.drawString(40, 785, f"Status: {review.status}")
            c.drawString(40, 770, f"Completed: {str(review.completed_at)}")

            y = 740
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y, "Summary:")
            y -= 16
            c.setFont("Helvetica", 10)
            summary = (review.summary or "")
            for line in summary.splitlines():
                c.drawString(40, y, line[:100])
                y -= 14
                if y < 60:
                    c.showPage()
                    y = 800

            c.showPage()
            c.save()
            buf.seek(0)
            return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=review_{review.id}.pdf"})

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export review")


@router.get("/search")
async def search_reviews(
    q: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        pattern = f"%{q}%"
        stmt = select(type(ReviewService)).limit(0)  # placeholder

        # simple search using SQL text to avoid complex ORM import cycles
        sql = text(
            "SELECT * FROM reviews WHERE user_id = :user_id AND (summary ILIKE :pat OR repository_name ILIKE :pat OR pr_title ILIKE :pat) ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        )
        res = await db.execute(sql, {"user_id": user.id, "pat": pattern, "limit": limit, "offset": offset})
        rows = res.fetchall()

        # Map rows to dicts
        items = []
        cols = res.keys()
        for r in rows:
            items.append({cols[i]: r[i] for i in range(len(cols))})

        return {"items": items, "total": len(items), "page": offset // limit + 1, "limit": limit}

    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Search failed")
