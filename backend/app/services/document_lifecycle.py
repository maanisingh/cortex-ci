"""
Document Lifecycle Management Service
Complete paperwork management: Save, Share, Submit, Archive, Record

Features:
- Document generation from templates
- Digital signatures (DocuSeal integration)
- Secure sharing with access controls
- Government portal submissions
- Long-term archival with retention policies
- Full audit trail and versioning
"""

import os
import json
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
import asyncio


class DocumentStatus(str, Enum):
    DRAFT = "draft"                    # Черновик
    PENDING_REVIEW = "pending_review"  # На рассмотрении
    PENDING_SIGNATURE = "pending_signature"  # Ожидает подписи
    SIGNED = "signed"                  # Подписан
    SUBMITTED = "submitted"            # Отправлен
    ACCEPTED = "accepted"              # Принят
    REJECTED = "rejected"              # Отклонен
    ARCHIVED = "archived"              # В архиве
    EXPIRED = "expired"                # Истек срок


class SharePermission(str, Enum):
    VIEW = "view"
    DOWNLOAD = "download"
    EDIT = "edit"
    SIGN = "sign"
    FULL = "full"


class SubmissionTarget(str, Enum):
    FNS = "fns"           # Федеральная налоговая служба
    PFR = "pfr"           # Пенсионный фонд
    FSS = "fss"           # Фонд соцстрахования
    ROSSTAT = "rosstat"   # Росстат
    ROSKOMNADZOR = "rkn"  # Роскомнадзор
    FSTEC = "fstec"       # ФСТЭК
    NOTARY = "notary"     # Нотариус
    COURT = "court"       # Суд
    CUSTOM = "custom"     # Произвольный адресат


class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    company_id: UUID
    template_id: Optional[str] = None

    # Basic info
    title: str
    title_en: Optional[str] = None
    description: Optional[str] = None
    category: str
    subcategory: Optional[str] = None

    # Content
    content: Optional[str] = None  # Rendered content
    content_hash: Optional[str] = None  # SHA-256 hash for integrity
    file_path: Optional[str] = None
    file_format: str = "docx"
    file_size_bytes: Optional[int] = None

    # Status
    status: DocumentStatus = DocumentStatus.DRAFT
    version: int = 1

    # Dates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None

    # Ownership
    created_by: str
    owner_id: str

    # Signatures
    requires_signature: bool = False
    signature_count_required: int = 0
    signatures: List[Dict[str, Any]] = []

    # Submission
    submitted_to: Optional[SubmissionTarget] = None
    submission_date: Optional[datetime] = None
    submission_reference: Optional[str] = None
    submission_response: Optional[Dict[str, Any]] = None

    # Archive
    archived_at: Optional[datetime] = None
    retention_years: int = 5
    archive_location: Optional[str] = None

    # Metadata
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class DocumentVersion(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    version: int
    content_hash: str
    file_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    change_description: Optional[str] = None


class DocumentShare(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    shared_with: str  # user_id or email
    shared_by: str
    permission: SharePermission
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    access_link: Optional[str] = None
    accessed_at: Optional[datetime] = None
    access_count: int = 0


class DocumentAuditLog(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    action: str
    actor_id: str
    actor_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None


class DocumentLifecycleService:
    """
    Complete document lifecycle management.
    """

    def __init__(self):
        self.documents: Dict[UUID, Document] = {}
        self.versions: Dict[UUID, List[DocumentVersion]] = {}
        self.shares: Dict[UUID, List[DocumentShare]] = {}
        self.audit_logs: Dict[UUID, List[DocumentAuditLog]] = {}

    # =========================================================================
    # SAVE - Document Creation and Updates
    # =========================================================================

    async def create_document(
        self,
        company_id: UUID,
        title: str,
        category: str,
        content: str,
        created_by: str,
        template_id: Optional[str] = None,
        **kwargs
    ) -> Document:
        """Create a new document."""
        content_hash = self._hash_content(content)

        doc = Document(
            company_id=company_id,
            template_id=template_id,
            title=title,
            category=category,
            content=content,
            content_hash=content_hash,
            created_by=created_by,
            owner_id=created_by,
            **kwargs
        )

        self.documents[doc.id] = doc

        # Create initial version
        await self._create_version(doc, created_by, "Initial creation")

        # Audit log
        await self._log_action(doc.id, "create", created_by, {"title": title})

        return doc

    async def update_document(
        self,
        document_id: UUID,
        content: str,
        updated_by: str,
        change_description: Optional[str] = None
    ) -> Document:
        """Update document content and create new version."""
        doc = self.documents.get(document_id)
        if not doc:
            raise ValueError("Document not found")

        # Update content
        old_hash = doc.content_hash
        doc.content = content
        doc.content_hash = self._hash_content(content)
        doc.version += 1
        doc.updated_at = datetime.utcnow()

        # Create version
        await self._create_version(doc, updated_by, change_description)

        # Audit log
        await self._log_action(
            document_id, "update", updated_by,
            {"version": doc.version, "old_hash": old_hash, "new_hash": doc.content_hash}
        )

        return doc

    async def save_as_file(
        self,
        document_id: UUID,
        file_format: str = "docx"
    ) -> str:
        """Save document to file system."""
        doc = self.documents.get(document_id)
        if not doc:
            raise ValueError("Document not found")

        # Generate file path
        file_name = f"{doc.id}_{doc.version}.{file_format}"
        file_path = f"/documents/{doc.company_id}/{doc.category}/{file_name}"

        # In production, this would actually write the file
        doc.file_path = file_path
        doc.file_format = file_format

        await self._log_action(doc.id, "save_file", doc.owner_id, {"path": file_path})

        return file_path

    # =========================================================================
    # SHARE - Secure Document Sharing
    # =========================================================================

    async def share_document(
        self,
        document_id: UUID,
        shared_with: str,
        shared_by: str,
        permission: SharePermission,
        expires_in_days: Optional[int] = None
    ) -> DocumentShare:
        """Share document with another user."""
        doc = self.documents.get(document_id)
        if not doc:
            raise ValueError("Document not found")

        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Generate secure access link
        access_link = self._generate_access_link(document_id, shared_with)

        share = DocumentShare(
            document_id=document_id,
            shared_with=shared_with,
            shared_by=shared_by,
            permission=permission,
            expires_at=expires_at,
            access_link=access_link
        )

        if document_id not in self.shares:
            self.shares[document_id] = []
        self.shares[document_id].append(share)

        await self._log_action(
            document_id, "share", shared_by,
            {"shared_with": shared_with, "permission": permission.value}
        )

        return share

    async def revoke_share(
        self,
        document_id: UUID,
        share_id: UUID,
        revoked_by: str
    ) -> bool:
        """Revoke document share."""
        if document_id in self.shares:
            self.shares[document_id] = [
                s for s in self.shares[document_id] if s.id != share_id
            ]
            await self._log_action(document_id, "revoke_share", revoked_by, {"share_id": str(share_id)})
            return True
        return False

    async def get_shared_documents(self, user_id: str) -> List[Document]:
        """Get all documents shared with a user."""
        shared_docs = []
        for doc_id, shares in self.shares.items():
            for share in shares:
                if share.shared_with == user_id:
                    if share.expires_at is None or share.expires_at > datetime.utcnow():
                        doc = self.documents.get(doc_id)
                        if doc:
                            shared_docs.append(doc)
                        break
        return shared_docs

    async def record_access(
        self,
        document_id: UUID,
        user_id: str,
        ip_address: Optional[str] = None
    ):
        """Record document access."""
        if document_id in self.shares:
            for share in self.shares[document_id]:
                if share.shared_with == user_id:
                    share.accessed_at = datetime.utcnow()
                    share.access_count += 1

        await self._log_action(
            document_id, "access", user_id,
            {"ip_address": ip_address}
        )

    # =========================================================================
    # SUBMIT - Government Portal Submissions
    # =========================================================================

    async def submit_to_authority(
        self,
        document_id: UUID,
        target: SubmissionTarget,
        submitted_by: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Submit document to government authority."""
        doc = self.documents.get(document_id)
        if not doc:
            raise ValueError("Document not found")

        # Generate submission reference
        submission_ref = f"{target.value.upper()}-{datetime.now().strftime('%Y%m%d')}-{str(doc.id)[:8]}"

        # In production, this would integrate with actual government APIs
        submission_result = await self._submit_to_portal(doc, target, additional_data)

        # Update document
        doc.status = DocumentStatus.SUBMITTED
        doc.submitted_to = target
        doc.submission_date = datetime.utcnow()
        doc.submission_reference = submission_ref
        doc.submission_response = submission_result

        await self._log_action(
            document_id, "submit", submitted_by,
            {"target": target.value, "reference": submission_ref}
        )

        return {
            "reference": submission_ref,
            "status": "submitted",
            "submitted_to": target.value,
            "submission_date": doc.submission_date.isoformat(),
            "response": submission_result
        }

    async def _submit_to_portal(
        self,
        doc: Document,
        target: SubmissionTarget,
        additional_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Submit to specific portal (mock implementation)."""

        # Portal-specific submission logic would go here
        portal_configs = {
            SubmissionTarget.FNS: {
                "endpoint": "https://service.nalog.ru/",
                "format": "xml",
                "requires_signature": True
            },
            SubmissionTarget.PFR: {
                "endpoint": "https://es.pfrf.ru/",
                "format": "xml",
                "requires_signature": True
            },
            SubmissionTarget.ROSKOMNADZOR: {
                "endpoint": "https://rkn.gov.ru/",
                "format": "pdf",
                "requires_signature": True
            },
            SubmissionTarget.ROSSTAT: {
                "endpoint": "https://websbor.gks.ru/",
                "format": "xml",
                "requires_signature": True
            }
        }

        config = portal_configs.get(target, {"endpoint": "custom", "format": "pdf"})

        # Mock successful submission
        return {
            "success": True,
            "portal": target.value,
            "timestamp": datetime.utcnow().isoformat(),
            "confirmation_number": f"CONF-{uuid4().hex[:12].upper()}",
            "message": f"Document submitted to {target.value} successfully"
        }

    async def check_submission_status(
        self,
        document_id: UUID
    ) -> Dict[str, Any]:
        """Check status of submitted document."""
        doc = self.documents.get(document_id)
        if not doc:
            raise ValueError("Document not found")

        if not doc.submitted_to:
            return {"status": "not_submitted"}

        # In production, would query the actual portal
        return {
            "status": doc.status.value,
            "submitted_to": doc.submitted_to.value,
            "submission_date": doc.submission_date.isoformat() if doc.submission_date else None,
            "reference": doc.submission_reference,
            "response": doc.submission_response
        }

    # =========================================================================
    # ARCHIVE - Long-term Storage
    # =========================================================================

    async def archive_document(
        self,
        document_id: UUID,
        archived_by: str,
        retention_years: Optional[int] = None
    ) -> Document:
        """Archive document for long-term storage."""
        doc = self.documents.get(document_id)
        if not doc:
            raise ValueError("Document not found")

        doc.status = DocumentStatus.ARCHIVED
        doc.archived_at = datetime.utcnow()
        if retention_years:
            doc.retention_years = retention_years

        # Calculate retention end date
        retention_end = doc.archived_at + timedelta(days=doc.retention_years * 365)

        # Generate archive location
        archive_path = f"/archive/{doc.company_id}/{doc.archived_at.year}/{doc.id}"
        doc.archive_location = archive_path

        await self._log_action(
            document_id, "archive", archived_by,
            {"retention_years": doc.retention_years, "archive_path": archive_path}
        )

        return doc

    async def restore_from_archive(
        self,
        document_id: UUID,
        restored_by: str
    ) -> Document:
        """Restore document from archive."""
        doc = self.documents.get(document_id)
        if not doc:
            raise ValueError("Document not found")

        if doc.status != DocumentStatus.ARCHIVED:
            raise ValueError("Document is not archived")

        doc.status = DocumentStatus.SIGNED if doc.signatures else DocumentStatus.DRAFT
        doc.archived_at = None
        doc.archive_location = None

        await self._log_action(document_id, "restore", restored_by, {})

        return doc

    async def get_documents_for_disposal(self) -> List[Document]:
        """Get documents past retention period for disposal."""
        now = datetime.utcnow()
        disposal_list = []

        for doc in self.documents.values():
            if doc.archived_at:
                retention_end = doc.archived_at + timedelta(days=doc.retention_years * 365)
                if now > retention_end:
                    disposal_list.append(doc)

        return disposal_list

    async def dispose_document(
        self,
        document_id: UUID,
        disposed_by: str,
        disposal_reason: str
    ) -> bool:
        """Permanently dispose of document (with audit trail)."""
        doc = self.documents.get(document_id)
        if not doc:
            raise ValueError("Document not found")

        # Create disposal record before deletion
        disposal_record = {
            "document_id": str(document_id),
            "title": doc.title,
            "category": doc.category,
            "created_at": doc.created_at.isoformat(),
            "archived_at": doc.archived_at.isoformat() if doc.archived_at else None,
            "disposed_at": datetime.utcnow().isoformat(),
            "disposed_by": disposed_by,
            "reason": disposal_reason
        }

        await self._log_action(
            document_id, "dispose", disposed_by,
            disposal_record
        )

        # Remove document (in production, would move to disposal storage)
        del self.documents[document_id]

        return True

    # =========================================================================
    # RECORD - Audit Trail and History
    # =========================================================================

    async def get_document_history(
        self,
        document_id: UUID
    ) -> List[DocumentAuditLog]:
        """Get complete audit trail for document."""
        return self.audit_logs.get(document_id, [])

    async def get_document_versions(
        self,
        document_id: UUID
    ) -> List[DocumentVersion]:
        """Get all versions of a document."""
        return self.versions.get(document_id, [])

    async def get_version_content(
        self,
        document_id: UUID,
        version: int
    ) -> Optional[str]:
        """Get content of a specific version."""
        versions = self.versions.get(document_id, [])
        for v in versions:
            if v.version == version:
                # In production, would read from storage
                return f"Content of version {version}"
        return None

    async def compare_versions(
        self,
        document_id: UUID,
        version_a: int,
        version_b: int
    ) -> Dict[str, Any]:
        """Compare two versions of a document."""
        # In production, would do actual diff
        return {
            "document_id": str(document_id),
            "version_a": version_a,
            "version_b": version_b,
            "differences": ["Placeholder for actual diff"]
        }

    async def generate_audit_report(
        self,
        company_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate audit report for company documents."""
        actions = {}
        documents_affected = set()

        for doc_id, logs in self.audit_logs.items():
            doc = self.documents.get(doc_id)
            if doc and doc.company_id == company_id:
                for log in logs:
                    if start_date <= log.timestamp <= end_date:
                        documents_affected.add(doc_id)
                        action = log.action
                        if action not in actions:
                            actions[action] = 0
                        actions[action] += 1

        return {
            "company_id": str(company_id),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_actions": sum(actions.values()),
            "actions_by_type": actions,
            "documents_affected": len(documents_affected)
        }

    # =========================================================================
    # SIGNATURES
    # =========================================================================

    async def request_signature(
        self,
        document_id: UUID,
        signer_email: str,
        signer_name: str,
        requested_by: str
    ) -> Dict[str, Any]:
        """Request digital signature on document."""
        doc = self.documents.get(document_id)
        if not doc:
            raise ValueError("Document not found")

        doc.status = DocumentStatus.PENDING_SIGNATURE
        doc.requires_signature = True

        signature_request = {
            "id": str(uuid4()),
            "signer_email": signer_email,
            "signer_name": signer_name,
            "requested_at": datetime.utcnow().isoformat(),
            "requested_by": requested_by,
            "status": "pending"
        }

        doc.signatures.append(signature_request)

        await self._log_action(
            document_id, "request_signature", requested_by,
            {"signer": signer_email}
        )

        # In production, would send email and integrate with DocuSeal
        return signature_request

    async def record_signature(
        self,
        document_id: UUID,
        signer_email: str,
        signature_data: Dict[str, Any]
    ) -> Document:
        """Record completed signature."""
        doc = self.documents.get(document_id)
        if not doc:
            raise ValueError("Document not found")

        for sig in doc.signatures:
            if sig.get("signer_email") == signer_email:
                sig["status"] = "signed"
                sig["signed_at"] = datetime.utcnow().isoformat()
                sig["signature_data"] = signature_data
                break

        # Check if all required signatures are complete
        pending = [s for s in doc.signatures if s.get("status") == "pending"]
        if not pending:
            doc.status = DocumentStatus.SIGNED

        await self._log_action(document_id, "sign", signer_email, {})

        return doc

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _hash_content(self, content: str) -> str:
        """Generate SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def _generate_access_link(self, document_id: UUID, user_id: str) -> str:
        """Generate secure access link."""
        token = hashlib.sha256(f"{document_id}{user_id}{datetime.utcnow()}".encode()).hexdigest()[:32]
        return f"/documents/shared/{token}"

    async def _create_version(
        self,
        doc: Document,
        created_by: str,
        description: Optional[str]
    ):
        """Create a new version record."""
        version = DocumentVersion(
            document_id=doc.id,
            version=doc.version,
            content_hash=doc.content_hash,
            file_path=doc.file_path or f"/temp/{doc.id}",
            created_by=created_by,
            change_description=description
        )

        if doc.id not in self.versions:
            self.versions[doc.id] = []
        self.versions[doc.id].append(version)

    async def _log_action(
        self,
        document_id: UUID,
        action: str,
        actor_id: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """Log an action in the audit trail."""
        log = DocumentAuditLog(
            document_id=document_id,
            action=action,
            actor_id=actor_id,
            details=details,
            ip_address=ip_address
        )

        if document_id not in self.audit_logs:
            self.audit_logs[document_id] = []
        self.audit_logs[document_id].append(log)


# Singleton instance
document_service = DocumentLifecycleService()


# FastAPI Router
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


@router.post("/documents")
async def create_document(data: Dict[str, Any]):
    """Create a new document."""
    doc = await document_service.create_document(**data)
    return doc.model_dump()


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get document by ID."""
    doc = document_service.documents.get(UUID(document_id))
    if doc:
        return doc.model_dump()
    raise HTTPException(status_code=404, detail="Document not found")


@router.put("/documents/{document_id}")
async def update_document(document_id: str, data: Dict[str, Any]):
    """Update document."""
    doc = await document_service.update_document(
        UUID(document_id),
        data["content"],
        data["updated_by"],
        data.get("change_description")
    )
    return doc.model_dump()


@router.post("/documents/{document_id}/share")
async def share_document(document_id: str, data: Dict[str, Any]):
    """Share document."""
    share = await document_service.share_document(
        UUID(document_id),
        data["shared_with"],
        data["shared_by"],
        SharePermission(data["permission"]),
        data.get("expires_in_days")
    )
    return share.model_dump()


@router.post("/documents/{document_id}/submit")
async def submit_document(document_id: str, data: Dict[str, Any]):
    """Submit document to authority."""
    result = await document_service.submit_to_authority(
        UUID(document_id),
        SubmissionTarget(data["target"]),
        data["submitted_by"],
        data.get("additional_data")
    )
    return result


@router.post("/documents/{document_id}/archive")
async def archive_document(document_id: str, data: Dict[str, Any]):
    """Archive document."""
    doc = await document_service.archive_document(
        UUID(document_id),
        data["archived_by"],
        data.get("retention_years")
    )
    return doc.model_dump()


@router.get("/documents/{document_id}/history")
async def get_document_history(document_id: str):
    """Get document audit trail."""
    history = await document_service.get_document_history(UUID(document_id))
    return {"history": [h.model_dump() for h in history]}


@router.get("/documents/{document_id}/versions")
async def get_document_versions(document_id: str):
    """Get document versions."""
    versions = await document_service.get_document_versions(UUID(document_id))
    return {"versions": [v.model_dump() for v in versions]}


@router.post("/documents/{document_id}/signature/request")
async def request_signature(document_id: str, data: Dict[str, Any]):
    """Request signature on document."""
    result = await document_service.request_signature(
        UUID(document_id),
        data["signer_email"],
        data["signer_name"],
        data["requested_by"]
    )
    return result
