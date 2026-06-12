from celery import Celery

from core.config import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
)

celery = Celery(
    "evven",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

celery.conf.update(
    timezone="UTC",
    enable_utc=True,
)

celery.conf.imports = ("tasks.cleanup_task",)

celery.conf.beat_schedule = {
    "cleanup-password-reset-tokens": {
        "task": "tasks.cleanup_task.delete_expired_used_tokens",
        "schedule": 60.0,  # 24 hours
    }
}
