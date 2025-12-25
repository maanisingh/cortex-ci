"""
Bulk Operations Service (Phase 4.2)
Handles batch import, update, and delete operations with progress tracking.
"""

import csv
import io
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
import structlog

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Entity, EntityType, AuditLog, AuditAction
from app.core.websocket import ws_manager, Alert, AlertType, AlertPriority

logger = structlog.get_logger()


class BulkOperationType(str, Enum):
    """Types of bulk operations."""
    IMPORT = "import"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"


class BulkOperationStatus(str, Enum):
    """Status of bulk operations."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BulkOperationProgress:
    """Progress tracking for bulk operations."""
    operation_id: str
    operation_type: BulkOperationType
    status: BulkOperationStatus
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_file: Optional[str] = None

    @property
    def progress_percentage(self) -> float:
        if self.total_items == 0:
            return 0
        return (self.processed_items / self.total_items) * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type.value,
            "status": self.status.value,
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "successful_items": self.successful_items,
            "failed_items": self.failed_items,
            "progress_percentage": round(self.progress_percentage, 2),
            "errors": self.errors[:10],  # Only first 10 errors
            "error_count": len(self.errors),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": (
                (self.completed_at - self.started_at).total_seconds()
                if self.completed_at and self.started_at
                else None
            ),
        }


class BulkOperationsService:
    """
    Service for handling bulk operations on entities and constraints.
    """

    def __init__(self):
        self._operations: Dict[str, BulkOperationProgress] = {}
        self._batch_size = 100

    async def import_entities(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        data: List[Dict[str, Any]],
        skip_duplicates: bool = True,
        update_existing: bool = False,
    ) -> BulkOperationProgress:
        """
        Bulk import entities from a list of dictionaries.

        Args:
            db: Database session
            tenant_id: Tenant ID
            user_id: User performing the operation
            data: List of entity data
            skip_duplicates: Skip entities that already exist
            update_existing: Update existing entities instead of skipping

        Returns:
            Operation progress
        """
        operation_id = str(uuid4())
        progress = BulkOperationProgress(
            operation_id=operation_id,
            operation_type=BulkOperationType.IMPORT,
            status=BulkOperationStatus.PROCESSING,
            total_items=len(data),
            started_at=datetime.utcnow(),
        )
        self._operations[operation_id] = progress

        try:
            for i, item in enumerate(data):
                try:
                    # Validate required fields
                    if "name" not in item:
                        raise ValueError("Missing required field: name")
                    if "type" not in item:
                        raise ValueError("Missing required field: type")

                    # Check for existing entity
                    existing = await db.execute(
                        select(Entity).where(
                            Entity.tenant_id == tenant_id,
                            Entity.name == item["name"],
                        )
                    )
                    existing_entity = existing.scalar_one_or_none()

                    if existing_entity:
                        if update_existing:
                            # Update existing entity
                            for key, value in item.items():
                                if key not in ["id", "tenant_id", "created_at"]:
                                    setattr(existing_entity, key, value)
                            progress.successful_items += 1
                        elif skip_duplicates:
                            progress.processed_items += 1
                            continue
                        else:
                            raise ValueError(f"Entity '{item['name']}' already exists")
                    else:
                        # Create new entity
                        entity = Entity(
                            tenant_id=tenant_id,
                            name=item["name"],
                            type=EntityType(item["type"]) if isinstance(item["type"], str) else item["type"],
                            country=item.get("country"),
                            description=item.get("description"),
                            aliases=item.get("aliases", []),
                            identifiers=item.get("identifiers", {}),
                            metadata=item.get("metadata", {}),
                        )
                        db.add(entity)
                        progress.successful_items += 1

                    progress.processed_items += 1

                    # Commit in batches
                    if progress.processed_items % self._batch_size == 0:
                        await db.commit()
                        # Broadcast progress
                        await self._broadcast_progress(tenant_id, progress)

                except Exception as e:
                    progress.failed_items += 1
                    progress.processed_items += 1
                    progress.errors.append({
                        "row": i + 1,
                        "item": item.get("name", "Unknown"),
                        "error": str(e),
                    })

            # Final commit
            await db.commit()

            progress.status = BulkOperationStatus.COMPLETED
            progress.completed_at = datetime.utcnow()

            # Create audit log
            audit = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action=AuditAction.BULK_CREATE,
                resource_type="entity",
                description=f"Bulk import: {progress.successful_items} created, {progress.failed_items} failed",
                success=progress.failed_items == 0,
            )
            db.add(audit)
            await db.commit()

            # Broadcast completion
            await self._broadcast_completion(tenant_id, progress)

        except Exception as e:
            logger.error("Bulk import failed", error=str(e), operation_id=operation_id)
            progress.status = BulkOperationStatus.FAILED
            progress.completed_at = datetime.utcnow()
            progress.errors.append({"error": str(e), "type": "system"})

        return progress

    async def bulk_update_entities(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        entity_ids: List[UUID],
        updates: Dict[str, Any],
    ) -> BulkOperationProgress:
        """
        Bulk update multiple entities with the same changes.

        Args:
            db: Database session
            tenant_id: Tenant ID
            user_id: User performing the operation
            entity_ids: List of entity IDs to update
            updates: Dictionary of field updates

        Returns:
            Operation progress
        """
        operation_id = str(uuid4())
        progress = BulkOperationProgress(
            operation_id=operation_id,
            operation_type=BulkOperationType.UPDATE,
            status=BulkOperationStatus.PROCESSING,
            total_items=len(entity_ids),
            started_at=datetime.utcnow(),
        )
        self._operations[operation_id] = progress

        try:
            # Validate entity IDs belong to tenant
            result = await db.execute(
                select(Entity.id).where(
                    Entity.id.in_(entity_ids),
                    Entity.tenant_id == tenant_id,
                )
            )
            valid_ids = {row[0] for row in result}

            for entity_id in entity_ids:
                try:
                    if entity_id not in valid_ids:
                        raise ValueError(f"Entity {entity_id} not found or access denied")

                    # Update entity
                    await db.execute(
                        update(Entity)
                        .where(Entity.id == entity_id)
                        .values(**updates, updated_at=datetime.utcnow())
                    )
                    progress.successful_items += 1
                    progress.processed_items += 1

                except Exception as e:
                    progress.failed_items += 1
                    progress.processed_items += 1
                    progress.errors.append({
                        "entity_id": str(entity_id),
                        "error": str(e),
                    })

                # Commit in batches
                if progress.processed_items % self._batch_size == 0:
                    await db.commit()
                    await self._broadcast_progress(tenant_id, progress)

            await db.commit()
            progress.status = BulkOperationStatus.COMPLETED
            progress.completed_at = datetime.utcnow()

            # Audit log
            audit = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action=AuditAction.BULK_UPDATE,
                resource_type="entity",
                description=f"Bulk update: {progress.successful_items} updated",
                changes={"updates": updates, "entity_count": len(entity_ids)},
                success=True,
            )
            db.add(audit)
            await db.commit()

            await self._broadcast_completion(tenant_id, progress)

        except Exception as e:
            logger.error("Bulk update failed", error=str(e))
            progress.status = BulkOperationStatus.FAILED
            progress.completed_at = datetime.utcnow()

        return progress

    async def bulk_delete_entities(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        entity_ids: List[UUID],
        soft_delete: bool = True,
    ) -> BulkOperationProgress:
        """
        Bulk delete multiple entities.

        Args:
            db: Database session
            tenant_id: Tenant ID
            user_id: User performing the operation
            entity_ids: List of entity IDs to delete
            soft_delete: If True, mark as inactive; if False, hard delete

        Returns:
            Operation progress
        """
        operation_id = str(uuid4())
        progress = BulkOperationProgress(
            operation_id=operation_id,
            operation_type=BulkOperationType.DELETE,
            status=BulkOperationStatus.PROCESSING,
            total_items=len(entity_ids),
            started_at=datetime.utcnow(),
        )
        self._operations[operation_id] = progress

        try:
            if soft_delete:
                # Soft delete - mark as inactive
                await db.execute(
                    update(Entity)
                    .where(
                        Entity.id.in_(entity_ids),
                        Entity.tenant_id == tenant_id,
                    )
                    .values(is_active=False, updated_at=datetime.utcnow())
                )
            else:
                # Hard delete
                await db.execute(
                    delete(Entity).where(
                        Entity.id.in_(entity_ids),
                        Entity.tenant_id == tenant_id,
                    )
                )

            await db.commit()

            progress.successful_items = len(entity_ids)
            progress.processed_items = len(entity_ids)
            progress.status = BulkOperationStatus.COMPLETED
            progress.completed_at = datetime.utcnow()

            # Audit log
            audit = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action=AuditAction.BULK_DELETE,
                resource_type="entity",
                description=f"Bulk {'soft ' if soft_delete else ''}delete: {len(entity_ids)} entities",
                success=True,
            )
            db.add(audit)
            await db.commit()

            await self._broadcast_completion(tenant_id, progress)

        except Exception as e:
            logger.error("Bulk delete failed", error=str(e))
            progress.status = BulkOperationStatus.FAILED
            progress.failed_items = len(entity_ids)
            progress.completed_at = datetime.utcnow()

        return progress

    async def parse_csv(self, csv_content: str) -> List[Dict[str, Any]]:
        """
        Parse CSV content into a list of dictionaries.

        Args:
            csv_content: CSV file content as string

        Returns:
            List of parsed rows as dictionaries
        """
        reader = csv.DictReader(io.StringIO(csv_content))
        return list(reader)

    async def parse_json(self, json_content: str) -> List[Dict[str, Any]]:
        """
        Parse JSON content into a list of dictionaries.

        Args:
            json_content: JSON file content as string

        Returns:
            List of parsed items
        """
        data = json.loads(json_content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "items" in data:
            return data["items"]
        else:
            raise ValueError("Invalid JSON format. Expected array or {items: [...]}}")

    def get_operation_status(self, operation_id: str) -> Optional[BulkOperationProgress]:
        """Get the status of a bulk operation."""
        return self._operations.get(operation_id)

    def list_operations(
        self,
        tenant_id: Optional[UUID] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """List recent bulk operations."""
        operations = list(self._operations.values())
        operations.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
        return [op.to_dict() for op in operations[:limit]]

    async def _broadcast_progress(self, tenant_id: UUID, progress: BulkOperationProgress):
        """Broadcast operation progress via WebSocket."""
        await ws_manager.broadcast_to_tenant(
            tenant_id,
            {
                "type": "bulk_operation_progress",
                "operation": progress.to_dict(),
            },
        )

    async def _broadcast_completion(self, tenant_id: UUID, progress: BulkOperationProgress):
        """Broadcast operation completion alert."""
        status_text = "completed" if progress.status == BulkOperationStatus.COMPLETED else "failed"
        priority = AlertPriority.MEDIUM if progress.status == BulkOperationStatus.COMPLETED else AlertPriority.HIGH

        alert = Alert(
            type=AlertType.BATCH_COMPLETE,
            priority=priority,
            title=f"Bulk {progress.operation_type.value} {status_text}",
            message=f"Processed {progress.processed_items} items: {progress.successful_items} successful, {progress.failed_items} failed",
            data=progress.to_dict(),
            tenant_id=tenant_id,
        )
        await ws_manager.broadcast_alert(alert)


# Global instance
bulk_operations = BulkOperationsService()
