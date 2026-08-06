# ============================================================
# CodeWhisper PR - Webhook Routes
# ============================================================

from typing import Any, Dict, List, Optional
import json
from fastapi import APIRouter, Depends, Header, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.database import get_db
from src.services.webhook_service import WebhookService
from src.services.review_service import ReviewService
from src.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()


@router.post("/{provider}")
async def receive_webhook(
    provider: str,
    request: Request,
    x_hub_signature: Optional[str] = Header(None, convert_underscores=False),
    x_hub_signature_256: Optional[str] = Header(None, convert_underscores=False),
    x_gitlab_token: Optional[str] = Header(None, convert_underscores=False),
    x_event_key: Optional[str] = Header(None, convert_underscores=False),
    db: AsyncSession = Depends(get_db),
):
    """Public receiver for provider webhooks (github, gitlab, bitbucket).

    The endpoint will try to match registered active endpoints for the provider
    and validate signatures against their configured secret. Valid deliveries are
    recorded as WebhookEvent rows and may trigger a review when the payload
    indicates a pull/merge request event.
    """
    try:
        body = await request.body()
        headers = request.headers

        service = WebhookService(db)
        endpoints = await service.list_active_endpoints(provider)

        if not endpoints:
            # Still record a generic event with no matching endpoint
            await service.record_generic_event(provider, None, None, None, json.loads(body or b"{}"))
            return {"status": "no-endpoint"}

        matched = False
        for ep in endpoints:
            sig_valid = await service.verify_signature_for_endpoint(ep, headers, body)
            event_payload = json.loads(body or b"{}")

            event = await service.create_event_from_delivery(ep, provider, event_payload, sig_valid)

            if sig_valid:
                matched = True
                # If it's a pull request / merge request, trigger a review
                try:
                    pr_info = service.extract_pr_info(provider, event_payload)
                    if pr_info:
                        review_service = ReviewService(db)
                        # Use endpoint creator as initiating user if available
                        user_id = ep.created_by if getattr(ep, "created_by", None) else None
                        if user_id:
                            await review_service.create_review(
                                user_id=user_id,
                                repository_url=pr_info["repository_url"],
                                pr_number=pr_info["pr_number"],
                                branch=pr_info.get("branch"),
                                review_settings=None,
                            )
                        else:
                            logger.info("Webhook matched but no creator user to attribute review to; skipping review creation.")
                except Exception as e:
                    logger.error(f"Failed to trigger review from webhook: {e}")

        return {"status": "delivered", "matched": matched}

    except Exception as e:
        logger.exception(f"Webhook delivery processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.post("/register", response_model=Dict[str, Any])
async def register_endpoint(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Register a webhook endpoint for an organization/provider.

    Protected: requires a valid token. The registering user will be set as
    the `created_by` owner of the endpoint.
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_token(credentials.credentials)

        service = WebhookService(db)
        ep = await service.register_endpoint(
            creator_id=user.id,
            provider=payload.get("provider"),
            name=payload.get("name"),
            url=payload.get("url"),
            secret=payload.get("secret"),
            events=payload.get("events", []),
            organization_id=payload.get("organization_id"),
        )

        return {"id": ep.id, "provider": ep.provider, "url": ep.url}

    except Exception as e:
        logger.exception(f"Failed to register webhook endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to register webhook endpoint")
