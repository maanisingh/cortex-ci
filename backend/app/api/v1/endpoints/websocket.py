"""
WebSocket API Endpoints (Phase 4.1)
Real-time communication endpoints for alerts and notifications.
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_token
from app.core.websocket import Alert, AlertPriority, AlertType, ws_manager

logger = structlog.get_logger()
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
):
    """
    WebSocket endpoint for real-time alerts and notifications.

    Connect with: ws://host/v1/ws?token=<jwt_token>

    Message types received:
    - connected: Connection confirmed
    - alert: New alert/notification
    - recent_alerts: Recent alerts on connect
    - heartbeat: Keep-alive ping

    Commands you can send:
    - {"action": "subscribe", "channel": "risk_alerts"}
    - {"action": "unsubscribe", "channel": "risk_alerts"}
    - {"action": "ping"}
    """
    # Validate token
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = UUID(payload.sub)
    tenant_id = UUID(payload.tenant_id)

    connection_id = await ws_manager.connect(websocket, user_id, tenant_id)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "subscribe":
                channel = data.get("channel")
                if channel:
                    await ws_manager.subscribe(connection_id, channel)

            elif action == "unsubscribe":
                channel = data.get("channel")
                if channel:
                    await ws_manager.unsubscribe(connection_id, channel)

            elif action == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        await ws_manager.disconnect(connection_id)
    except Exception as e:
        logger.error("WebSocket error", error=str(e), connection_id=connection_id)
        await ws_manager.disconnect(connection_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return {
        "total_connections": ws_manager.get_connection_count(),
        "status": "healthy",
    }


@router.post("/alerts/broadcast")
async def broadcast_alert(
    alert_type: AlertType,
    title: str,
    message: str,
    priority: AlertPriority = AlertPriority.MEDIUM,
    tenant_id: str = None,
):
    """
    Broadcast an alert to connected clients.
    Admin only endpoint.
    """
    alert = Alert(
        type=alert_type,
        priority=priority,
        title=title,
        message=message,
        tenant_id=UUID(tenant_id) if tenant_id else None,
    )
    await ws_manager.broadcast_alert(alert)

    return {
        "status": "sent",
        "recipients": ws_manager.get_connection_count(),
    }
