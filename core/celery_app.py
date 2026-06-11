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
