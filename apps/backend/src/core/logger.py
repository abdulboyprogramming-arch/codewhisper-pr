# ============================================================
# CodeWhisper PR - Logging Configuration
# ============================================================

import sys
import os
from loguru import logger

from src.core.config import settings


def setup_logging():
    """Configure logging for the application."""

    logger.remove()

    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    logger.add(
        os.path.join(log_dir, "error.log"),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
    )

    logger.info(f"Logging configured with level: {settings.LOG_LEVEL}")
    return logger
