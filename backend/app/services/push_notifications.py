"""
Push Notification Service using Ntfy
Self-hosted push notifications - no signup required.

Supports:
- Real-time alerts
- Task notifications
- Deadline reminders
- Incident alerts
- Mobile push via Ntfy app
"""

import os
import httpx
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
import asyncio
import json

# Ntfy Configuration
NTFY_URL = os.getenv("NTFY_URL", "http://localhost:8090")
NTFY_DEFAULT_TOPIC = os.getenv("NTFY_TOPIC", "cortex-alerts")


class Priority(str, Enum):
    MIN = "min"        # No sound, no vibration
    LOW = "low"        # No sound
    DEFAULT = "default"
    HIGH = "high"      # Sound + vibration
    URGENT = "urgent"  # Sound + vibration + bypass DND


class NotificationAction(BaseModel):
    action: str = "view"  # view, http, broadcast
    label: str
    url: Optional[str] = None
    method: Optional[str] = None  # GET, POST, etc.
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None


class PushNotification(BaseModel):
    topic: str = NTFY_DEFAULT_TOPIC
    title: str
    message: str
    priority: Priority = Priority.DEFAULT
    tags: List[str] = []
    click: Optional[str] = None  # URL to open on click
    actions: List[NotificationAction] = []
    attach: Optional[str] = None  # Attachment URL
    filename: Optional[str] = None
    delay: Optional[str] = None  # e.g., "30min", "9am"
    email: Optional[str] = None  # Also send via email


class PushNotificationService:
    """
    Push notification service using Ntfy.

    Ntfy is a simple, self-hosted notification service that supports:
    - Web push notifications
    - Mobile apps (iOS, Android)
    - Desktop notifications
    - Email delivery
    """

    def __init__(self, base_url: str = NTFY_URL):
        self.base_url = base_url.rstrip("/")
        self.default_topic = NTFY_DEFAULT_TOPIC

    async def send(self, notification: PushNotification) -> bool:
        """Send a push notification."""
        try:
            headers = {
                "Title": notification.title,
                "Priority": notification.priority.value,
            }

            # Add tags (emojis and labels)
            if notification.tags:
                headers["Tags"] = ",".join(notification.tags)

            # Click action
            if notification.click:
                headers["Click"] = notification.click

            # Actions (buttons)
            if notification.actions:
                actions_str = "; ".join([
                    self._format_action(a) for a in notification.actions
                ])
                headers["Actions"] = actions_str

            # Attachment
            if notification.attach:
                headers["Attach"] = notification.attach
                if notification.filename:
                    headers["Filename"] = notification.filename

            # Delayed delivery
            if notification.delay:
                headers["Delay"] = notification.delay

            # Email delivery
            if notification.email:
                headers["Email"] = notification.email

            url = f"{self.base_url}/{notification.topic}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    content=notification.message,
                    headers=headers,
                    timeout=10.0
                )
                return response.status_code == 200

        except Exception as e:
            print(f"Failed to send push notification: {e}")
            return False

    def _format_action(self, action: NotificationAction) -> str:
        """Format action for Ntfy header."""
        parts = [action.action, action.label]
        if action.url:
            parts.append(action.url)
        return ", ".join(parts)

    async def send_simple(
        self,
        title: str,
        message: str,
        priority: Priority = Priority.DEFAULT,
        tags: List[str] = [],
        topic: Optional[str] = None
    ) -> bool:
        """Send a simple notification."""
        notification = PushNotification(
            topic=topic or self.default_topic,
            title=title,
            message=message,
            priority=priority,
            tags=tags
        )
        return await self.send(notification)

    # ==========================================================================
    # Pre-built notification types for GRC
    # ==========================================================================

    async def notify_task_assigned(
        self,
        task_title: str,
        assigned_to: str,
        due_date: str,
        task_url: str,
        topic: Optional[str] = None
    ) -> bool:
        """Notify user of task assignment."""
        notification = PushNotification(
            topic=topic or self.default_topic,
            title="Новая задача",
            message=f"{task_title}\nСрок: {due_date}",
            priority=Priority.DEFAULT,
            tags=["clipboard", "task"],
            click=task_url,
            actions=[
                NotificationAction(
                    action="view",
                    label="Открыть",
                    url=task_url
                )
            ]
        )
        return await self.send(notification)

    async def notify_deadline_reminder(
        self,
        task_title: str,
        days_remaining: int,
        task_url: str,
        topic: Optional[str] = None
    ) -> bool:
        """Send deadline reminder."""
        if days_remaining <= 1:
            priority = Priority.URGENT
            tags = ["warning", "deadline", "urgent"]
        elif days_remaining <= 3:
            priority = Priority.HIGH
            tags = ["warning", "deadline"]
        else:
            priority = Priority.DEFAULT
            tags = ["calendar", "reminder"]

        notification = PushNotification(
            topic=topic or self.default_topic,
            title=f"Срок через {days_remaining} дн.",
            message=task_title,
            priority=priority,
            tags=tags,
            click=task_url
        )
        return await self.send(notification)

    async def notify_document_approval(
        self,
        document_title: str,
        prepared_by: str,
        document_url: str,
        approve_url: str,
        topic: Optional[str] = None
    ) -> bool:
        """Request document approval."""
        notification = PushNotification(
            topic=topic or self.default_topic,
            title="Требуется утверждение",
            message=f"{document_title}\nПодготовил: {prepared_by}",
            priority=Priority.HIGH,
            tags=["page_facing_up", "approval"],
            click=document_url,
            actions=[
                NotificationAction(
                    action="view",
                    label="Утвердить",
                    url=approve_url
                ),
                NotificationAction(
                    action="view",
                    label="Просмотреть",
                    url=document_url
                )
            ]
        )
        return await self.send(notification)

    async def notify_incident(
        self,
        incident_type: str,
        severity: str,
        description: str,
        incident_url: str,
        topic: Optional[str] = None
    ) -> bool:
        """Alert about security incident."""
        priority_map = {
            "critical": Priority.URGENT,
            "high": Priority.HIGH,
            "medium": Priority.DEFAULT,
            "low": Priority.LOW
        }

        tag_map = {
            "critical": ["rotating_light", "incident", "critical"],
            "high": ["warning", "incident", "high"],
            "medium": ["exclamation", "incident"],
            "low": ["information_source", "incident"]
        }

        notification = PushNotification(
            topic=topic or self.default_topic,
            title=f"🚨 {severity.upper()}: {incident_type}",
            message=description[:200],
            priority=priority_map.get(severity.lower(), Priority.HIGH),
            tags=tag_map.get(severity.lower(), ["warning"]),
            click=incident_url
        )
        return await self.send(notification)

    async def notify_compliance_status(
        self,
        framework: str,
        score: float,
        change: float,
        dashboard_url: str,
        topic: Optional[str] = None
    ) -> bool:
        """Notify about compliance status change."""
        if change > 0:
            message = f"Соответствие улучшилось на {change:.1f}%"
            tags = ["chart_with_upwards_trend", "compliance"]
        else:
            message = f"Соответствие снизилось на {abs(change):.1f}%"
            tags = ["chart_with_downwards_trend", "compliance", "warning"]

        notification = PushNotification(
            topic=topic or self.default_topic,
            title=f"{framework}: {score:.1f}%",
            message=message,
            priority=Priority.DEFAULT if change > 0 else Priority.HIGH,
            tags=tags,
            click=dashboard_url
        )
        return await self.send(notification)

    async def notify_audit_scheduled(
        self,
        audit_type: str,
        audit_date: str,
        auditor: str,
        audit_url: str,
        topic: Optional[str] = None
    ) -> bool:
        """Notify about scheduled audit."""
        notification = PushNotification(
            topic=topic or self.default_topic,
            title="Запланирован аудит",
            message=f"{audit_type}\nДата: {audit_date}\nАудитор: {auditor}",
            priority=Priority.HIGH,
            tags=["mag", "audit", "calendar"],
            click=audit_url
        )
        return await self.send(notification)


# Topic-based subscription for different user roles
class TopicManager:
    """Manage notification topics for different users/roles."""

    def __init__(self, service: PushNotificationService):
        self.service = service

    def get_user_topic(self, user_id: str) -> str:
        """Get personal topic for a user."""
        return f"cortex-user-{user_id}"

    def get_role_topic(self, role: str) -> str:
        """Get topic for a role (e.g., admins, dpo, security)."""
        return f"cortex-role-{role}"

    def get_company_topic(self, company_id: str) -> str:
        """Get topic for a company."""
        return f"cortex-company-{company_id}"

    async def notify_role(
        self,
        role: str,
        title: str,
        message: str,
        **kwargs
    ) -> bool:
        """Send notification to all users with a specific role."""
        topic = self.get_role_topic(role)
        return await self.service.send_simple(title, message, topic=topic, **kwargs)


# Singleton instance
push_service = PushNotificationService()
topic_manager = TopicManager(push_service)


# FastAPI Router
from fastapi import APIRouter, HTTPException, BackgroundTasks

router = APIRouter()


@router.post("/send")
async def send_push_notification(
    notification: PushNotification,
    background_tasks: BackgroundTasks
):
    """Send a push notification."""
    background_tasks.add_task(push_service.send, notification)
    return {"success": True, "message": "Notification queued"}


@router.post("/send-simple")
async def send_simple_notification(
    title: str,
    message: str,
    priority: str = "default",
    tags: str = "",
    topic: Optional[str] = None
):
    """Send a simple notification."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    success = await push_service.send_simple(
        title=title,
        message=message,
        priority=Priority(priority),
        tags=tag_list,
        topic=topic
    )
    if success:
        return {"success": True}
    raise HTTPException(status_code=500, detail="Failed to send notification")


@router.post("/test")
async def send_test_notification(topic: Optional[str] = None):
    """Send a test notification."""
    success = await push_service.send_simple(
        title="Тест уведомления",
        message="Если вы видите это сообщение, push-уведомления работают!",
        priority=Priority.DEFAULT,
        tags=["white_check_mark", "test"],
        topic=topic
    )
    if success:
        return {"success": True, "message": "Test notification sent"}
    raise HTTPException(status_code=500, detail="Failed to send test notification")


@router.get("/topics")
async def get_topics():
    """Get information about notification topics."""
    return {
        "default_topic": NTFY_DEFAULT_TOPIC,
        "ntfy_url": NTFY_URL,
        "subscribe_url": f"{NTFY_URL}/{NTFY_DEFAULT_TOPIC}",
        "instructions": {
            "web": f"Open {NTFY_URL}/{NTFY_DEFAULT_TOPIC} in browser",
            "android": "Install Ntfy app, subscribe to topic",
            "ios": "Install Ntfy app, subscribe to topic"
        }
    }
