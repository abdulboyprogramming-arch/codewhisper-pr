# ============================================================
# CodeWhisper PR - Error Handler Middleware
# ============================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from loguru import logger

from src.core.exceptions import CodeWhisperError


def register_error_handlers(app: FastAPI):
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(CodeWhisperError)
    async def codewhisper_error_handler(request: Request, exc: CodeWhisperError):
        logger.error(
            f"CodeWhisperError on {request.method} {request.url.path}: {exc.message}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "details": exc.details,
                "status": "error",
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(
            f"HTTPException on {request.method} {request.url.path}: {exc.detail}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.detail,
                "status": "error",
            },
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            f"Validation error on {request.method} {request.url.path}: {exc.errors()}",
        )
        return JSONResponse(
            status_code=422,
            content={
                "message": "Validation error",
                "details": exc.errors(),
                "status": "error",
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.error(
            f"Database integrity error on {request.method} {request.url.path}: {str(exc)}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=400,
            content={
                "message": "Data integrity violation",
                "details": str(exc.orig) if exc.orig else str(exc),
                "status": "error",
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        logger.error(
            f"Database error on {request.method} {request.url.path}: {str(exc)}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "message": "Database operation failed",
                "status": "error",
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "status": "error",
            },
        )
