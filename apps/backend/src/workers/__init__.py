# ============================================================
# CodeWhisper PR - Workers Package
# ============================================================

from src.workers.review_worker import celery_app

__all__ = ["celery_app"]
