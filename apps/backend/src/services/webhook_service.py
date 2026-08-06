# ============================================================
# CodeWhisper PR - Webhook Service
# ============================================================

from typing import Any, Dict, List, Optional
import hmac
import hashlib
import json
from loguru import logger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.webhook import WebhookEndpoint, WebhookEvent


class WebhookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_active_endpoints(self, provider: str) -> List[WebhookEndpoint]:
        result = await self.db.execute(select(WebhookEndpoint).where(WebhookEndpoint.provider == provider, WebhookEndpoint.is_active == True))
        return result.scalars().all()

    async def register_endpoint(self, creator_id: str, provider: str, name: str, url: str, secret: str, events: List[str], organization_id: Optional[str] = None) -> WebhookEndpoint:
        ep = WebhookEndpoint(
            provider=provider,
            name=name or f"{provider}-endpoint",
            url=url,
            secret=secret,
            events=events or [],
            created_by=creator_id,
            organization_id=organization_id,
        )
        self.db.add(ep)
        await self.db.commit()
        await self.db.refresh(ep)
        return ep

    async def record_generic_event(self, provider: str, endpoint_id: Optional[str], event_type: Optional[str], action: Optional[str], payload: Dict[str, Any]) -> WebhookEvent:
        ev = WebhookEvent(
            endpoint_id=endpoint_id,
            provider=provider,
            event_type=event_type or "unknown",
            action=action,
            payload=payload,
            signature_valid=False,
            processed=False,
        )
        self.db.add(ev)
        await self.db.commit()
        await self.db.refresh(ev)
        return ev

    async def create_event_from_delivery(self, endpoint: WebhookEndpoint, provider: str, payload: Dict[str, Any], signature_valid: bool) -> WebhookEvent:
        event_type = payload.get("action") or payload.get("hook", {}).get("type") or payload.get("event")
        action = payload.get("action")

        ev = WebhookEvent(
            endpoint_id=endpoint.id,
            provider=provider,
            event_type=event_type or "unknown",
            action=action,
            payload=payload,
            signature_valid=signature_valid,
            processed=False,
        )
        self.db.add(ev)
        await self.db.commit()
        await self.db.refresh(ev)
        return ev

    async def verify_signature_for_endpoint(self, endpoint: WebhookEndpoint, headers: Dict[str, str], body: bytes) -> bool:
        # Try GitHub style
        gh_sig = headers.get("x-hub-signature") or headers.get("X-Hub-Signature")
        gh_sig256 = headers.get("x-hub-signature-256") or headers.get("X-Hub-Signature-256")
        gitlab_token = headers.get("x-gitlab-token") or headers.get("X-Gitlab-Token")

        secret = (endpoint.secret or "").encode()

        try:
            if gh_sig256:
                # format: sha256=hex
                prefix, sig = gh_sig256.split("=", 1)
                mac = hmac.new(secret, body, hashlib.sha256)
                return hmac.compare_digest(mac.hexdigest(), sig)
            if gh_sig:
                prefix, sig = gh_sig.split("=", 1)
                mac = hmac.new(secret, body, hashlib.sha1)
                return hmac.compare_digest(mac.hexdigest(), sig)
            if gitlab_token:
                return hmac.compare_digest((endpoint.secret or ""), gitlab_token)

        except Exception as e:
            logger.error(f"Signature verification error: {e}")

        return False

    def extract_pr_info(self, provider: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # GitHub
        if provider.lower() == "github":
            pr = payload.get("pull_request")
            if pr:
                repo = payload.get("repository", {})
                return {
                    "repository_url": repo.get("clone_url") or repo.get("html_url"),
                    "pr_number": pr.get("number"),
                    "branch": pr.get("head", {}).get("ref"),
                }

        # GitLab
        if provider.lower() == "gitlab":
            object_kind = payload.get("object_kind")
            if object_kind == "merge_request":
                mr = payload.get("object_attributes", {})
                project = payload.get("project", {})
                return {
                    "repository_url": project.get("git_http_url") or project.get("web_url"),
                    "pr_number": mr.get("iid"),
                    "branch": mr.get("source_branch"),
                }

        # Bitbucket
        if provider.lower() == "bitbucket":
            pr = payload.get("pullrequest")
            if pr:
                repo = payload.get("repository", {})
                links = repo.get("links", {})
                clone_links = links.get("clone", [])
                clone_url = clone_links[0].get("href") if clone_links else repo.get("links", {}).get("html", {}).get("href")
                return {
                    "repository_url": clone_url,
                    "pr_number": pr.get("id"),
                    "branch": pr.get("source", {}).get("branch", {}).get("name"),
                }

        return None
