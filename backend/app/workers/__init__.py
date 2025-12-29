"""
Celery Worker Configuration for CORTEX-CI
"""

from celery import Celery
import os

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
app = Celery(
    "cortex",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.tasks"],
)

# Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Daily sync of sanctions data
    "sync-sanctions-daily": {
        "task": "app.workers.tasks.sync_sanctions",
        "schedule": 86400.0,  # Every 24 hours
    },
    # Hourly risk recalculation for high-priority entities
    "recalculate-risks-hourly": {
        "task": "app.workers.tasks.recalculate_risks",
        "schedule": 3600.0,  # Every hour
    },
    # Daily compliance reminders
    "send-compliance-reminders-daily": {
        "task": "app.workers.tasks.send_compliance_reminders",
        "schedule": 86400.0,  # Every 24 hours
    },
}
