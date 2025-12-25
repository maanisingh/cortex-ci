"""
WebSocket Manager (Phase 4.1)
Implements real-time communication for alerts and notifications.
"""

import asyncio
from typing import Dict, Set, Optional, Any, List
from datetime import datetime
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum
import structlog

from fastapi import WebSocket
from starlette.websockets import WebSocketState

logger = structlog.get_logger()


class AlertType(str, Enum):
    """Types of real-time alerts."""
    RISK_CHANGE = "risk_change"
    CONSTRAINT_UPDATE = "constraint_update"
    ENTITY_MATCH = "entity_match"
    SCENARIO_COMPLETE = "scenario_complete"
    SYSTEM_ALERT = "system_alert"
    USER_NOTIFICATION = "user_notification"
    BATCH_COMPLETE = "batch_complete"
    APPROVAL_REQUIRED = "approval_required"


class AlertPriority(str, Enum):
    """Alert priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection."""
    websocket: WebSocket
    user_id: UUID
    tenant_id: UUID
    subscriptions: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Alert:
    """Real-time alert message."""
    type: AlertType
    priority: AlertPriority
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    tenant_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    entity_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "created_at": self.created_at.isoformat(),
        }


class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts.
    Supports per-tenant and per-user messaging.
    """

    def __init__(self):
        # Active connections by user ID
        self._connections: Dict[str, WebSocketConnection] = {}
        # Tenant -> user IDs mapping
        self._tenant_users: Dict[str, Set[str]] = {}
        # Alert history (for reconnection)
        self._alert_history: List[Alert] = []
        self._max_history = 100
        # Background tasks
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def connect(
        self,
        websocket: WebSocket,
        user_id: UUID,
        tenant_id: UUID,
    ) -> str:
        """
        Accept and register a WebSocket connection.

        Args:
            websocket: The WebSocket connection
            user_id: User's ID
            tenant_id: Tenant's ID

        Returns:
            Connection ID
        """
        await websocket.accept()

        connection_id = str(user_id)
        connection = WebSocketConnection(
            websocket=websocket,
            user_id=user_id,
            tenant_id=tenant_id,
        )

        self._connections[connection_id] = connection

        # Track tenant users
        tenant_key = str(tenant_id)
        if tenant_key not in self._tenant_users:
            self._tenant_users[tenant_key] = set()
        self._tenant_users[tenant_key].add(connection_id)

        logger.info(
            "WebSocket connected",
            user_id=str(user_id),
            tenant_id=str(tenant_id),
            total_connections=len(self._connections),
        )

        # Send connection confirmation
        await self._send_to_connection(connection_id, {
            "type": "connected",
            "message": "WebSocket connection established",
            "connection_id": connection_id,
        })

        # Send recent alerts
        await self._send_recent_alerts(connection_id, tenant_id)

        return connection_id

    async def disconnect(self, connection_id: str):
        """
        Remove a WebSocket connection.

        Args:
            connection_id: The connection ID to remove
        """
        if connection_id in self._connections:
            connection = self._connections[connection_id]
            tenant_key = str(connection.tenant_id)

            # Remove from tenant tracking
            if tenant_key in self._tenant_users:
                self._tenant_users[tenant_key].discard(connection_id)
                if not self._tenant_users[tenant_key]:
                    del self._tenant_users[tenant_key]

            del self._connections[connection_id]

            logger.info(
                "WebSocket disconnected",
                user_id=str(connection.user_id),
                total_connections=len(self._connections),
            )

    async def subscribe(self, connection_id: str, channel: str):
        """
        Subscribe a connection to a channel.

        Args:
            connection_id: The connection ID
            channel: Channel to subscribe to
        """
        if connection_id in self._connections:
            self._connections[connection_id].subscriptions.add(channel)
            await self._send_to_connection(connection_id, {
                "type": "subscribed",
                "channel": channel,
            })

    async def unsubscribe(self, connection_id: str, channel: str):
        """
        Unsubscribe a connection from a channel.

        Args:
            connection_id: The connection ID
            channel: Channel to unsubscribe from
        """
        if connection_id in self._connections:
            self._connections[connection_id].subscriptions.discard(channel)
            await self._send_to_connection(connection_id, {
                "type": "unsubscribed",
                "channel": channel,
            })

    async def broadcast_alert(self, alert: Alert):
        """
        Broadcast an alert to relevant connections.

        Args:
            alert: The alert to broadcast
        """
        # Store in history
        self._alert_history.append(alert)
        if len(self._alert_history) > self._max_history:
            self._alert_history = self._alert_history[-self._max_history:]

        message = {
            "type": "alert",
            "alert": alert.to_dict(),
        }

        sent_count = 0

        # If user-specific, send only to that user
        if alert.user_id:
            connection_id = str(alert.user_id)
            if connection_id in self._connections:
                await self._send_to_connection(connection_id, message)
                sent_count = 1
        # If tenant-specific, broadcast to tenant
        elif alert.tenant_id:
            tenant_key = str(alert.tenant_id)
            if tenant_key in self._tenant_users:
                for connection_id in self._tenant_users[tenant_key]:
                    await self._send_to_connection(connection_id, message)
                    sent_count += 1
        # Global broadcast
        else:
            for connection_id in self._connections:
                await self._send_to_connection(connection_id, message)
                sent_count += 1

        logger.info(
            "Alert broadcast",
            alert_type=alert.type.value,
            priority=alert.priority.value,
            recipients=sent_count,
        )

    async def send_to_user(self, user_id: UUID, message: Dict[str, Any]):
        """
        Send a message to a specific user.

        Args:
            user_id: User's ID
            message: Message to send
        """
        connection_id = str(user_id)
        if connection_id in self._connections:
            await self._send_to_connection(connection_id, message)

    async def broadcast_to_tenant(self, tenant_id: UUID, message: Dict[str, Any]):
        """
        Broadcast a message to all users in a tenant.

        Args:
            tenant_id: Tenant's ID
            message: Message to broadcast
        """
        tenant_key = str(tenant_id)
        if tenant_key in self._tenant_users:
            for connection_id in self._tenant_users[tenant_key]:
                await self._send_to_connection(connection_id, message)

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """
        Broadcast a message to all subscribers of a channel.

        Args:
            channel: Channel name
            message: Message to broadcast
        """
        for connection_id, connection in self._connections.items():
            if channel in connection.subscriptions:
                await self._send_to_connection(connection_id, message)

    async def _send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send a message to a specific connection."""
        if connection_id not in self._connections:
            return

        connection = self._connections[connection_id]
        try:
            if connection.websocket.client_state == WebSocketState.CONNECTED:
                await connection.websocket.send_json(message)
        except Exception as e:
            logger.error(
                "Failed to send WebSocket message",
                connection_id=connection_id,
                error=str(e),
            )
            await self.disconnect(connection_id)

    async def _send_recent_alerts(self, connection_id: str, tenant_id: UUID):
        """Send recent alerts to a newly connected client."""
        tenant_alerts = [
            alert for alert in self._alert_history
            if alert.tenant_id == tenant_id or alert.tenant_id is None
        ][-10:]  # Last 10 alerts

        if tenant_alerts:
            await self._send_to_connection(connection_id, {
                "type": "recent_alerts",
                "alerts": [alert.to_dict() for alert in tenant_alerts],
            })

    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self._connections)

    def get_tenant_connection_count(self, tenant_id: UUID) -> int:
        """Get number of connections for a tenant."""
        tenant_key = str(tenant_id)
        return len(self._tenant_users.get(tenant_key, set()))

    async def start_heartbeat(self, interval: int = 30):
        """Start heartbeat task to keep connections alive."""
        async def heartbeat():
            while True:
                await asyncio.sleep(interval)
                message = {"type": "heartbeat", "timestamp": datetime.utcnow().isoformat()}
                for connection_id in list(self._connections.keys()):
                    await self._send_to_connection(connection_id, message)

        self._heartbeat_task = asyncio.create_task(heartbeat())

    async def stop_heartbeat(self):
        """Stop the heartbeat task."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None


# Global WebSocket manager instance
ws_manager = WebSocketManager()


# Helper functions for common alerts
async def send_risk_alert(
    tenant_id: UUID,
    entity_id: UUID,
    entity_name: str,
    old_score: float,
    new_score: float,
):
    """Send a risk change alert."""
    priority = AlertPriority.HIGH if new_score >= 75 else AlertPriority.MEDIUM
    change = "increased" if new_score > old_score else "decreased"

    alert = Alert(
        type=AlertType.RISK_CHANGE,
        priority=priority,
        title=f"Risk Score {change.title()}",
        message=f"{entity_name} risk score {change} from {old_score:.1f} to {new_score:.1f}",
        data={
            "entity_id": str(entity_id),
            "entity_name": entity_name,
            "old_score": old_score,
            "new_score": new_score,
            "change": new_score - old_score,
        },
        tenant_id=tenant_id,
        entity_id=entity_id,
    )
    await ws_manager.broadcast_alert(alert)


async def send_constraint_alert(
    tenant_id: UUID,
    constraint_name: str,
    action: str,
    affected_entities: int,
):
    """Send a constraint update alert."""
    alert = Alert(
        type=AlertType.CONSTRAINT_UPDATE,
        priority=AlertPriority.HIGH,
        title=f"Constraint {action.title()}",
        message=f"{constraint_name} has been {action}. {affected_entities} entities affected.",
        data={
            "constraint_name": constraint_name,
            "action": action,
            "affected_entities": affected_entities,
        },
        tenant_id=tenant_id,
    )
    await ws_manager.broadcast_alert(alert)


async def send_system_alert(
    message: str,
    priority: AlertPriority = AlertPriority.MEDIUM,
    tenant_id: Optional[UUID] = None,
):
    """Send a system-wide alert."""
    alert = Alert(
        type=AlertType.SYSTEM_ALERT,
        priority=priority,
        title="System Alert",
        message=message,
        tenant_id=tenant_id,
    )
    await ws_manager.broadcast_alert(alert)


async def send_approval_alert(
    tenant_id: UUID,
    user_id: UUID,
    item_type: str,
    item_name: str,
    action_required: str,
):
    """Send an approval required alert."""
    alert = Alert(
        type=AlertType.APPROVAL_REQUIRED,
        priority=AlertPriority.HIGH,
        title="Approval Required",
        message=f"{item_type} '{item_name}' requires your {action_required}.",
        data={
            "item_type": item_type,
            "item_name": item_name,
            "action_required": action_required,
        },
        tenant_id=tenant_id,
        user_id=user_id,
    )
    await ws_manager.broadcast_alert(alert)
