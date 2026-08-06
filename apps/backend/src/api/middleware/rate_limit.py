# ============================================================
# CodeWhisper PR - Rate Limiting Middleware
# ============================================================

import time
from collections import defaultdict, deque
from typing import Optional, Dict, Deque, Tuple
from fastapi import Request, HTTPException, status
from starlette.types import ASGIApp, Receive, Scope, Message
from loguru import logger


class RateLimitStore:
    """In-memory rate limit store (use Redis in production)."""

    def __init__(self):
        self._store: Dict[str, Deque[float]] = defaultdict(deque)
        self._locks: Dict[str, float] = {}

    def get_key(self, ip: str, endpoint: str) -> str:
        return f"{ip}:{endpoint}"

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        now = time.time()
        request_times = self._store[key]

        while request_times and request_times[0] < now - window:
            request_times.popleft()

        if len(request_times) >= limit:
            return False

        request_times.append(now)
        return True


class RateLimitMiddleware:
    """Rate limiting middleware using token bucket algorithm."""

    def __init__(
        self,
        app: ASGIApp,
        rate_limit: int = 100,
        window: int = 60,
        excluded_paths: Optional[list] = None,
    ):
        self.app = app
        self.rate_limit = rate_limit
        self.window = window
        self.excluded_paths = excluded_paths or ["/health", "/docs", "/openapi.json"]
        self.store = RateLimitStore()
        logger.info(f"RateLimitMiddleware initialized with {rate_limit} req/{window}s")

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        scope["rate_limit"] = {"limit": self.rate_limit, "window": self.window}

        request_path = scope.get("path", "")
        if request_path in self.excluded_paths:
            await self.app(scope, receive, send)
            return

        client_host = scope.get("client", ("", 0))[0]
        if not client_host:
            client_host = "unknown"

        key = self.store.get_key(client_host, request_path)
        if not self.store.is_allowed(key, self.rate_limit, self.window):
            logger.warning(f"Rate limit exceeded for {client_host} on {request_path}")
            await self._send_rate_limit_error(send)
            return

        await self.app(scope, receive, send)

    async def _send_rate_limit_error(self, send):
        await send({
            "type": "http.response.start",
            "status": status.HTTP_429_TOO_MANY_REQUESTS,
            "headers": [(b"content-type", b"application/json")],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"detail": "Rate limit exceeded. Please try again later."}',
        })


class IPFilterMiddleware:
    """IP-based access control middleware."""

    def __init__(
        self,
        app: ASGIApp,
        allowed_ips: Optional[list] = None,
        blocked_ips: Optional[list] = None,
    ):
        self.app = app
        self.allowed_ips = allowed_ips or []
        self.blocked_ips = blocked_ips or []

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            client_ip = scope.get("client", ("", 0))[0]
            if self.blocked_ips and client_ip in self.blocked_ips:
                await self._send_error(send, status.HTTP_403_FORBIDDEN, "Access denied")
                return

            if self.allowed_ips and client_ip not in self.allowed_ips:
                await self._send_error(send, status.HTTP_403_FORBIDDEN, "Access denied")
                return

        await self.app(scope, receive, send)

    async def _send_error(self, send, status_code: int, message: str):
        await send({
            "type": "http.response.start",
            "status": status_code,
            "headers": [(b"content-type", b"application/json")],
        })
        await send({
            "type": "http.response.body",
            "body": f'{{"detail": "{message}"}}'.encode(),
        })
