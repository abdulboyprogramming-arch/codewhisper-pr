# ============================================================
# CodeWhisper PR - Request Logging Middleware
# ============================================================

import time
import uuid
from typing import Awaitable, Callable
from fastapi import Request, Response
from loguru import logger


async def log_request_response(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    """Middleware to log incoming requests and outgoing responses."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    method = request.method
    path = request.url.path
    query_params = dict(request.query_params) if request.query_params else {}
    client_host = request.client.host if request.client else "unknown"

    logger.info(
        f"[{request_id}] Request: {method} {path} from {client_host}"
        + (f" params={query_params}" if query_params else "")
    )

    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    response.headers["X-Request-ID"] = request_id

    status_emoji = "✅" if response.status_code < 400 else "❌" if response.status_code < 500 else "💥"

    logger.info(
        f"[{request_id}] Response: {method} {path} "
        f"-> {response.status_code} ({duration_ms:.1f}ms) {status_emoji}"
    )

    return response


class ResponseTimeMiddleware:
    """Middleware to add response time header."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration_ms = (time.time() - start_time) * 1000
                headers = list(message.get("headers", []))
                headers.append((b"x-response-time", f"{duration_ms:.2f}".encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
