"""Celery application configuration."""
from __future__ import annotations

import os

from celery import Celery

from ..config import DEBUG

# Redis broker URL — defaults to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "tiktok_suite",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=600,  # 10 min soft limit
    task_time_limit=900,  # 15 min hard limit
    task_default_queue="default",
    task_routes={
        "app.workers.video_tasks.*": {"queue": "video"},
        "app.workers.audio_tasks.*": {"queue": "audio"},
    },
    beat_schedule={
        "cleanup-temp-files": {
            "task": "app.workers.video_tasks.cleanup_temp_files",
            "schedule": 3600.0,  # every hour
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers.video_tasks", "app.workers.audio_tasks"])
