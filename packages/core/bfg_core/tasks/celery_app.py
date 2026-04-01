"""Celery application configuration for BFG Platform.

Ported from cNode celery_app.py. Uses Redis as broker and result backend.
Task routing sends different task types to dedicated queues.

Usage:
    # Start worker:
    celery -A bfg_core.tasks.celery_app worker --loglevel=info

    # Start beat scheduler:
    celery -A bfg_core.tasks.celery_app beat --loglevel=info
"""

from celery import Celery
from celery.schedules import crontab

from bfg_core.config import CoreSettings

settings = CoreSettings()

celery_app = Celery(
    "bfg",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="Europe/Berlin",
    enable_utc=True,

    # Task behavior
    task_track_started=True,
    task_time_limit=600,          # 10 minutes max per task
    task_soft_time_limit=540,     # Soft limit at 9 minutes
    worker_prefetch_multiplier=1,  # One task at a time per worker
    result_expires=86400,          # Results expire after 24 hours

    # Task routing — dedicated queues prevent slow external API calls
    # from blocking other task types
    task_routes={
        "bfg_core.tasks.diagnostics.*": {"queue": "diagnostics"},
        "bfg_core.tasks.notifications.*": {"queue": "notifications"},
        "bfg_core.tasks.data_retention.*": {"queue": "data_retention"},
    },

    # Default queue for unrouted tasks
    task_default_queue="default",

    # Beat schedule — periodic tasks
    beat_schedule={
        "expire-tokens-daily": {
            "task": "bfg_core.tasks.data_retention.expire_tokens",
            "schedule": crontab(hour=2, minute=0),  # 2:00 AM daily
        },
        "retention-cleanup-weekly": {
            "task": "bfg_core.tasks.data_retention.retention_cleanup",
            "schedule": crontab(hour=3, minute=0, day_of_week="sunday"),  # Sunday 3 AM
        },
    },
)

# Auto-discover tasks in these modules
# Note: actual task functions are stubs for S1, full implementation in S2+
celery_app.autodiscover_tasks([
    "bfg_core.tasks",
])
