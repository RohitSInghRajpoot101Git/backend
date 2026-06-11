from core.celery_app import celery
from services.cleanup_service import cleanup_expired_token


@celery.task
def delete_expired_used_tokens():
    cleanup_expired_token()
