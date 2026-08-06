# ============================================================
# CodeWhisper PR - Celery Application
# ============================================================

from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "codewhisper",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.workers.review_worker", "src.workers.analytics_worker"],
)

celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    task_track_started=True,
    task_time_limit=600,
)


if __name__ == "__main__":
    celery_app.start()
