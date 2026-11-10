"""
FraudShield Celery Application.
Configures Redis broker, serialization, task routing, and execution options.
"""

from celery import Celery
from backend.app.core.config import settings

celery_app = Celery(
    "fraudshield_tasks",
    broker=settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "backend.app.tasks.retraining",
        "backend.app.tasks.batch_prediction",
        "backend.app.tasks.drift_monitor",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max for retraining tasks
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)

