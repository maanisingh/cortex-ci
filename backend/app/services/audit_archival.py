"""
Audit Log Archival Service (Phase 3.7)
Implements audit log archival, retention, and export functionality.
"""

import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditAction, AuditLog

logger = structlog.get_logger()


class AuditArchivalService:
    """
    Service for archiving and managing audit logs.
    Implements retention policies and export functionality.
    """

    def __init__(
        self,
        archive_path: str | None = None,
        retention_days: int = 90,
        archive_after_days: int = 30,
    ):
        self.archive_path = Path(archive_path or "/var/cortex-ci/audit-archives")
        self.retention_days = retention_days
        self.archive_after_days = archive_after_days

    async def archive_old_logs(
        self,
        db: AsyncSession,
        tenant_id: UUID | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """
        Archive audit logs older than archive_after_days.

        Args:
            db: Database session
            tenant_id: Optional tenant ID to filter
            force: Force archive even if recently archived

        Returns:
            Archive summary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.archive_after_days)

        # Build query
        query = select(AuditLog).where(AuditLog.created_at < cutoff_date)
        if tenant_id:
            query = query.where(AuditLog.tenant_id == tenant_id)

        result = await db.execute(query)
        logs = result.scalars().all()

        if not logs:
            return {"archived": 0, "message": "No logs to archive"}

        # Group by date for daily archives
        daily_logs: dict[str, list[dict]] = {}
        for log in logs:
            date_key = log.created_at.strftime("%Y-%m-%d")
            if date_key not in daily_logs:
                daily_logs[date_key] = []
            daily_logs[date_key].append(self._serialize_log(log))

        # Create archive files
        self.archive_path.mkdir(parents=True, exist_ok=True)
        archived_count = 0
        archive_files = []

        for date_key, log_entries in daily_logs.items():
            tenant_suffix = f"_{tenant_id}" if tenant_id else ""
            archive_file = self.archive_path / f"audit_{date_key}{tenant_suffix}.json.gz"

            # Compress and write
            with gzip.open(archive_file, "wt", encoding="utf-8") as f:
                json.dump(log_entries, f, default=str)

            archived_count += len(log_entries)
            archive_files.append(str(archive_file))

        # Delete archived logs from database
        delete_stmt = delete(AuditLog).where(AuditLog.id.in_([log.id for log in logs]))
        await db.execute(delete_stmt)
        await db.commit()

        logger.info(
            "Audit logs archived",
            count=archived_count,
            files=len(archive_files),
            tenant_id=str(tenant_id) if tenant_id else "all",
        )

        return {
            "archived": archived_count,
            "files": archive_files,
            "date_range": {
                "from": min(daily_logs.keys()),
                "to": max(daily_logs.keys()),
            },
        }

    async def cleanup_old_archives(self) -> dict[str, Any]:
        """
        Delete archive files older than retention_days.

        Returns:
            Cleanup summary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        deleted_files = []

        if not self.archive_path.exists():
            return {"deleted": 0, "message": "No archive directory"}

        for archive_file in self.archive_path.glob("audit_*.json.gz"):
            # Extract date from filename
            try:
                date_str = archive_file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff_date:
                    archive_file.unlink()
                    deleted_files.append(str(archive_file))
            except (IndexError, ValueError):
                continue

        logger.info("Old archives cleaned up", count=len(deleted_files))

        return {
            "deleted": len(deleted_files),
            "files": deleted_files,
        }

    async def export_logs(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        actions: list[str] | None = None,
        user_id: UUID | None = None,
        format: str = "json",
    ) -> dict[str, Any]:
        """
        Export audit logs for compliance or analysis.

        Args:
            db: Database session
            tenant_id: Tenant ID
            start_date: Start of date range
            end_date: End of date range
            actions: Filter by action types
            user_id: Filter by user
            format: Export format (json, csv)

        Returns:
            Export data and metadata
        """
        query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)

        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
        if actions:
            action_enums = [AuditAction(a) for a in actions if a in AuditAction._value2member_map_]
            if action_enums:
                query = query.where(AuditLog.action.in_(action_enums))
        if user_id:
            query = query.where(AuditLog.user_id == user_id)

        query = query.order_by(AuditLog.created_at.desc())

        result = await db.execute(query)
        logs = result.scalars().all()

        serialized = [self._serialize_log(log) for log in logs]

        if format == "csv":
            return self._to_csv(serialized)

        return {
            "format": format,
            "count": len(serialized),
            "logs": serialized,
            "exported_at": datetime.utcnow().isoformat(),
        }

    async def get_statistics(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Get audit log statistics.

        Args:
            db: Database session
            tenant_id: Tenant ID
            days: Number of days to analyze

        Returns:
            Statistics summary
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Total count
        total_query = select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.tenant_id == tenant_id,
                AuditLog.created_at >= cutoff,
            )
        )
        total_result = await db.execute(total_query)
        total_count = total_result.scalar()

        # Count by action
        action_query = (
            select(
                AuditLog.action,
                func.count(AuditLog.id).label("count"),
            )
            .where(
                and_(
                    AuditLog.tenant_id == tenant_id,
                    AuditLog.created_at >= cutoff,
                )
            )
            .group_by(AuditLog.action)
        )

        action_result = await db.execute(action_query)
        by_action = {row.action.value: row.count for row in action_result}

        # Failed operations
        failed_query = select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.tenant_id == tenant_id,
                AuditLog.created_at >= cutoff,
                AuditLog.success == False,  # noqa: E712
            )
        )
        failed_result = await db.execute(failed_query)
        failed_count = failed_result.scalar()

        # Top users
        user_query = (
            select(
                AuditLog.user_email,
                func.count(AuditLog.id).label("count"),
            )
            .where(
                and_(
                    AuditLog.tenant_id == tenant_id,
                    AuditLog.created_at >= cutoff,
                    AuditLog.user_email.isnot(None),
                )
            )
            .group_by(AuditLog.user_email)
            .order_by(func.count(AuditLog.id).desc())
            .limit(10)
        )

        user_result = await db.execute(user_query)
        top_users = [{"email": row.user_email, "count": row.count} for row in user_result]

        return {
            "period_days": days,
            "total_events": total_count,
            "failed_events": failed_count,
            "success_rate": round((1 - failed_count / max(total_count, 1)) * 100, 2),
            "by_action": by_action,
            "top_users": top_users,
        }

    async def search_logs(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        query_text: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """
        Search audit logs with full-text search.

        Args:
            db: Database session
            tenant_id: Tenant ID
            query_text: Search query
            page: Page number
            page_size: Results per page

        Returns:
            Search results
        """
        base_query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)

        if query_text:
            search_pattern = f"%{query_text}%"
            base_query = base_query.where(
                (AuditLog.description.ilike(search_pattern))
                | (AuditLog.user_email.ilike(search_pattern))
                | (AuditLog.resource_name.ilike(search_pattern))
            )

        # Count total
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()

        # Get page
        offset = (page - 1) * page_size
        page_query = base_query.order_by(AuditLog.created_at.desc()).offset(offset).limit(page_size)
        result = await db.execute(page_query)
        logs = result.scalars().all()

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
            "results": [self._serialize_log(log) for log in logs],
        }

    def _serialize_log(self, log: AuditLog) -> dict[str, Any]:
        """Serialize audit log for export."""
        return {
            "id": str(log.id),
            "created_at": log.created_at.isoformat() if log.created_at else None,
            "tenant_id": str(log.tenant_id) if log.tenant_id else None,
            "user_id": str(log.user_id) if log.user_id else None,
            "user_email": log.user_email,
            "user_role": log.user_role,
            "action": log.action.value if log.action else None,
            "resource_type": log.resource_type,
            "resource_id": str(log.resource_id) if log.resource_id else None,
            "resource_name": log.resource_name,
            "description": log.description,
            "success": log.success,
            "error_message": log.error_message,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "changes": log.changes,
        }

    def _to_csv(self, logs: list[dict]) -> dict[str, Any]:
        """Convert logs to CSV format."""
        if not logs:
            return {"format": "csv", "count": 0, "data": ""}

        headers = list(logs[0].keys())
        lines = [",".join(headers)]

        for log in logs:
            row = []
            for h in headers:
                val = log.get(h, "")
                if isinstance(val, dict):
                    val = json.dumps(val)
                val = str(val).replace('"', '""')
                if "," in val or '"' in val:
                    val = f'"{val}"'
                row.append(val)
            lines.append(",".join(row))

        return {
            "format": "csv",
            "count": len(logs),
            "data": "\n".join(lines),
        }


# Global instance
audit_archival = AuditArchivalService()
