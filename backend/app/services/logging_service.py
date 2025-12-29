"""
Logging Service using Loki
Centralized log aggregation for audit trails and debugging.

Features:
- Structured JSON logging
- Log shipping to Loki
- Audit trail for compliance
- Query interface for log analysis
"""

import os
import json
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
import asyncio
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

# Loki Configuration
LOKI_URL = os.getenv("LOKI_URL", "http://localhost:3100")
LOG_DIR = os.getenv("LOG_DIR", "/app/logs")


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditAction(str, Enum):
    # User actions
    LOGIN = "user.login"
    LOGOUT = "user.logout"
    LOGIN_FAILED = "user.login_failed"

    # Document actions
    DOCUMENT_CREATE = "document.create"
    DOCUMENT_UPDATE = "document.update"
    DOCUMENT_DELETE = "document.delete"
    DOCUMENT_VIEW = "document.view"
    DOCUMENT_DOWNLOAD = "document.download"
    DOCUMENT_APPROVE = "document.approve"
    DOCUMENT_REJECT = "document.reject"

    # Task actions
    TASK_CREATE = "task.create"
    TASK_UPDATE = "task.update"
    TASK_COMPLETE = "task.complete"
    TASK_ASSIGN = "task.assign"

    # Compliance actions
    GAP_ANALYSIS_RUN = "compliance.gap_analysis"
    CONTROL_MAPPED = "compliance.control_mapped"
    EVIDENCE_UPLOAD = "compliance.evidence_upload"
    AUDIT_START = "compliance.audit_start"
    AUDIT_COMPLETE = "compliance.audit_complete"

    # Admin actions
    USER_CREATE = "admin.user_create"
    USER_UPDATE = "admin.user_update"
    USER_DELETE = "admin.user_delete"
    ROLE_CHANGE = "admin.role_change"
    SETTINGS_CHANGE = "admin.settings_change"

    # Security events
    INCIDENT_REPORT = "security.incident_report"
    ACCESS_DENIED = "security.access_denied"
    SUSPICIOUS_ACTIVITY = "security.suspicious_activity"


class AuditLogEntry(BaseModel):
    timestamp: datetime
    action: AuditAction
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    company_id: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class LoggingService:
    """
    Centralized logging service with Loki integration.
    """

    def __init__(self):
        self.loki_url = LOKI_URL
        self.log_dir = Path(LOG_DIR)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Set up file logging
        self._setup_file_logging()

    def _setup_file_logging(self):
        """Set up rotating file handlers."""
        # Application log
        self.app_logger = logging.getLogger("cortex.app")
        self.app_logger.setLevel(logging.DEBUG)

        app_handler = RotatingFileHandler(
            self.log_dir / "app.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        app_handler.setFormatter(logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"module": "%(module)s", "message": "%(message)s"}'
        ))
        self.app_logger.addHandler(app_handler)

        # Audit log
        self.audit_logger = logging.getLogger("cortex.audit")
        self.audit_logger.setLevel(logging.INFO)

        audit_handler = RotatingFileHandler(
            self.log_dir / "audit.log",
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        audit_handler.setFormatter(logging.Formatter('%(message)s'))
        self.audit_logger.addHandler(audit_handler)

        # Security log
        self.security_logger = logging.getLogger("cortex.security")
        self.security_logger.setLevel(logging.INFO)

        security_handler = RotatingFileHandler(
            self.log_dir / "security.log",
            maxBytes=50*1024*1024,
            backupCount=10
        )
        security_handler.setFormatter(logging.Formatter('%(message)s'))
        self.security_logger.addHandler(security_handler)

    def log(
        self,
        level: LogLevel,
        message: str,
        module: str = "app",
        **extra
    ):
        """Log a message with structured data."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.value,
            "module": module,
            "message": message,
            **extra
        }

        log_line = json.dumps(log_entry, ensure_ascii=False, default=str)

        level_map = {
            LogLevel.DEBUG: self.app_logger.debug,
            LogLevel.INFO: self.app_logger.info,
            LogLevel.WARNING: self.app_logger.warning,
            LogLevel.ERROR: self.app_logger.error,
            LogLevel.CRITICAL: self.app_logger.critical
        }

        level_map[level](log_line)

    def audit(self, entry: AuditLogEntry):
        """Record an audit log entry."""
        log_data = entry.model_dump()
        log_data["timestamp"] = entry.timestamp.isoformat()
        log_data["action"] = entry.action.value

        log_line = json.dumps(log_data, ensure_ascii=False, default=str)
        self.audit_logger.info(log_line)

        # Also log security events to security log
        if entry.action.value.startswith("security."):
            self.security_logger.info(log_line)

    def security_event(
        self,
        event_type: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        severity: str = "medium",
        **extra
    ):
        """Log a security event."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "description": description,
            "user_id": user_id,
            "ip_address": ip_address,
            "severity": severity,
            **extra
        }

        log_line = json.dumps(log_entry, ensure_ascii=False, default=str)
        self.security_logger.info(log_line)

    async def push_to_loki(self, log_entries: List[Dict[str, Any]]) -> bool:
        """Push log entries to Loki."""
        if not log_entries:
            return True

        try:
            streams = []
            for entry in log_entries:
                timestamp_ns = int(
                    datetime.fromisoformat(entry.get("timestamp", datetime.utcnow().isoformat()))
                    .timestamp() * 1e9
                )

                labels = {
                    "job": "cortex",
                    "level": entry.get("level", "info"),
                    "module": entry.get("module", "app")
                }

                streams.append({
                    "stream": labels,
                    "values": [[str(timestamp_ns), json.dumps(entry, default=str)]]
                })

            payload = {"streams": streams}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.loki_url}/loki/api/v1/push",
                    json=payload,
                    timeout=10.0
                )
                return response.status_code == 204

        except Exception as e:
            self.log(LogLevel.ERROR, f"Failed to push to Loki: {e}", module="logging")
            return False

    async def query_logs(
        self,
        query: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query logs from Loki."""
        if not start:
            start = datetime.utcnow() - timedelta(hours=24)
        if not end:
            end = datetime.utcnow()

        params = {
            "query": query,
            "start": int(start.timestamp() * 1e9),
            "end": int(end.timestamp() * 1e9),
            "limit": limit,
            "direction": "backward"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.loki_url}/loki/api/v1/query_range",
                    params=params,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    results = []

                    for stream in data.get("data", {}).get("result", []):
                        for value in stream.get("values", []):
                            try:
                                log_entry = json.loads(value[1])
                                log_entry["_timestamp_ns"] = value[0]
                                results.append(log_entry)
                            except json.JSONDecodeError:
                                results.append({"raw": value[1], "_timestamp_ns": value[0]})

                    return results

        except Exception as e:
            self.log(LogLevel.ERROR, f"Failed to query Loki: {e}", module="logging")

        return []

    async def get_audit_trail(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit trail with filters."""
        # Build Loki query
        query_parts = ['{job="cortex", module="audit"}']

        if user_id:
            query_parts.append(f'|= "user_id": "{user_id}"')
        if action:
            query_parts.append(f'|= "action": "{action}"')
        if resource_type:
            query_parts.append(f'|= "resource_type": "{resource_type}"')
        if resource_id:
            query_parts.append(f'|= "resource_id": "{resource_id}"')

        query = " ".join(query_parts)
        return await self.query_logs(query, start, end, limit)

    async def export_audit_logs(
        self,
        start: datetime,
        end: datetime,
        format: str = "json"
    ) -> str:
        """Export audit logs for regulatory compliance."""
        logs = await self.query_logs(
            '{job="cortex", module="audit"}',
            start=start,
            end=end,
            limit=10000
        )

        if format == "json":
            return json.dumps(logs, ensure_ascii=False, indent=2, default=str)
        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            if logs:
                writer = csv.DictWriter(output, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)

            return output.getvalue()

        return ""


# Singleton instance
logging_service = LoggingService()


# Convenience functions
def log_info(message: str, **kwargs):
    logging_service.log(LogLevel.INFO, message, **kwargs)

def log_warning(message: str, **kwargs):
    logging_service.log(LogLevel.WARNING, message, **kwargs)

def log_error(message: str, **kwargs):
    logging_service.log(LogLevel.ERROR, message, **kwargs)

def audit_log(action: AuditAction, **kwargs):
    entry = AuditLogEntry(
        timestamp=datetime.utcnow(),
        action=action,
        **kwargs
    )
    logging_service.audit(entry)


# FastAPI Router
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


@router.get("/query")
async def query_logs(
    query: str = Query(..., description="LogQL query"),
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 100
):
    """Query logs using LogQL."""
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None

    results = await logging_service.query_logs(query, start_dt, end_dt, limit)
    return {"count": len(results), "logs": results}


@router.get("/audit-trail")
async def get_audit_trail(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 100
):
    """Get audit trail with filters."""
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None

    results = await logging_service.get_audit_trail(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start=start_dt,
        end=end_dt,
        limit=limit
    )
    return {"count": len(results), "entries": results}


@router.post("/export")
async def export_audit_logs(
    start: str,
    end: str,
    format: str = "json"
):
    """Export audit logs for compliance."""
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)

    content = await logging_service.export_audit_logs(start_dt, end_dt, format)

    return {
        "format": format,
        "start": start,
        "end": end,
        "content": content
    }
