"""
Celery Application Configuration for Background Task Processing.
"""
from celery import Celery
from config import config
import logging

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    'file_integrity_workers',
    broker=config.RABBITMQ_URL,
    backend='rpc://',
    include=['workers.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

logger.info("Celery app initialized")
