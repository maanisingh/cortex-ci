"""
Evidence Management System
Handles evidence collection, storage, and linking to controls.

Uses local filesystem for storage (no cloud services required).
"""

import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel


# Configuration
EVIDENCE_STORAGE_PATH = Path(os.getenv("EVIDENCE_STORAGE_PATH", "./data/evidence"))
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".xml", ".json",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp",
    ".zip", ".rar", ".7z",
    ".eml", ".msg",
}


class EvidenceMetadata(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_size: int
    file_hash: str
    mime_type: str
    uploaded_by: str
    uploaded_at: str
    description: str | None
    tags: list[str]
    linked_controls: list[str]
    linked_requirements: list[str]
    company_id: str
    framework: str | None
    status: str  # pending, reviewed, approved, rejected
    reviewed_by: str | None
    reviewed_at: str | None
    expiry_date: str | None


class EvidenceUploadRequest(BaseModel):
    description: str | None = None
    tags: list[str] = []
    linked_controls: list[str] = []
    linked_requirements: list[str] = []
    company_id: str
    framework: str | None = None
    expiry_date: str | None = None


class EvidenceManager:
    """Manages evidence files and metadata."""

    def __init__(self, storage_path: Path = EVIDENCE_STORAGE_PATH):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def upload_evidence(
        self,
        file: BinaryIO,
        filename: str,
        upload_request: EvidenceUploadRequest,
        uploaded_by: str,
    ) -> EvidenceMetadata:
        """Upload and store evidence file."""
        # Validate file extension
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type {ext} not allowed")

        # Read file content
        content = file.read()
        file_size = len(content)

        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum of {MAX_FILE_SIZE} bytes")

        # Calculate hash
        file_hash = hashlib.sha256(content).hexdigest()

        # Generate unique filename
        evidence_id = str(uuid4())
        stored_filename = f"{evidence_id}{ext}"

        # Create company directory
        company_dir = self.storage_path / upload_request.company_id
        company_dir.mkdir(exist_ok=True)

        # Store file
        file_path = company_dir / stored_filename
        with open(file_path, "wb") as f:
            f.write(content)

        # Create metadata
        metadata = EvidenceMetadata(
            id=evidence_id,
            filename=stored_filename,
            original_filename=filename,
            file_size=file_size,
            file_hash=file_hash,
            mime_type=self._get_mime_type(ext),
            uploaded_by=uploaded_by,
            uploaded_at=datetime.now().isoformat(),
            description=upload_request.description,
            tags=upload_request.tags,
            linked_controls=upload_request.linked_controls,
            linked_requirements=upload_request.linked_requirements,
            company_id=upload_request.company_id,
            framework=upload_request.framework,
            status="pending",
            reviewed_by=None,
            reviewed_at=None,
            expiry_date=upload_request.expiry_date,
        )

        # Store metadata (in production would use database)
        self._store_metadata(metadata)

        return metadata

    def get_evidence(self, evidence_id: str, company_id: str) -> tuple[bytes, EvidenceMetadata]:
        """Retrieve evidence file and metadata."""
        metadata = self._get_metadata(evidence_id)
        if not metadata or metadata.company_id != company_id:
            raise FileNotFoundError("Evidence not found")

        file_path = self.storage_path / company_id / metadata.filename
        if not file_path.exists():
            raise FileNotFoundError("Evidence file not found")

        with open(file_path, "rb") as f:
            content = f.read()

        return content, metadata

    def delete_evidence(self, evidence_id: str, company_id: str) -> bool:
        """Delete evidence file and metadata."""
        metadata = self._get_metadata(evidence_id)
        if not metadata or metadata.company_id != company_id:
            raise FileNotFoundError("Evidence not found")

        file_path = self.storage_path / company_id / metadata.filename
        if file_path.exists():
            file_path.unlink()

        self._delete_metadata(evidence_id)
        return True

    def list_evidence(
        self,
        company_id: str,
        framework: str | None = None,
        control_id: str | None = None,
        status: str | None = None,
    ) -> list[EvidenceMetadata]:
        """List evidence files with optional filters."""
        # In production would query database
        # For now, return mock data
        return []

    def link_to_control(self, evidence_id: str, control_id: str) -> EvidenceMetadata:
        """Link evidence to a control."""
        metadata = self._get_metadata(evidence_id)
        if control_id not in metadata.linked_controls:
            metadata.linked_controls.append(control_id)
            self._store_metadata(metadata)
        return metadata

    def link_to_requirement(self, evidence_id: str, requirement_id: str) -> EvidenceMetadata:
        """Link evidence to a requirement."""
        metadata = self._get_metadata(evidence_id)
        if requirement_id not in metadata.linked_requirements:
            metadata.linked_requirements.append(requirement_id)
            self._store_metadata(metadata)
        return metadata

    def review_evidence(
        self,
        evidence_id: str,
        reviewer: str,
        status: str,  # approved, rejected
        comment: str | None = None,
    ) -> EvidenceMetadata:
        """Review and approve/reject evidence."""
        metadata = self._get_metadata(evidence_id)
        metadata.status = status
        metadata.reviewed_by = reviewer
        metadata.reviewed_at = datetime.now().isoformat()
        self._store_metadata(metadata)
        return metadata

    def _get_mime_type(self, ext: str) -> str:
        """Get MIME type from extension."""
        mime_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".xml": "application/xml",
            ".json": "application/json",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".zip": "application/zip",
        }
        return mime_types.get(ext, "application/octet-stream")

    def _store_metadata(self, metadata: EvidenceMetadata):
        """Store metadata to file (in production would use database)."""
        import json
        metadata_dir = self.storage_path / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        with open(metadata_dir / f"{metadata.id}.json", "w") as f:
            json.dump(metadata.model_dump(), f, ensure_ascii=False, indent=2)

    def _get_metadata(self, evidence_id: str) -> EvidenceMetadata | None:
        """Get metadata from file (in production would use database)."""
        import json
        metadata_path = self.storage_path / "metadata" / f"{evidence_id}.json"
        if not metadata_path.exists():
            return None
        with open(metadata_path, "r") as f:
            data = json.load(f)
        return EvidenceMetadata(**data)

    def _delete_metadata(self, evidence_id: str):
        """Delete metadata file."""
        metadata_path = self.storage_path / "metadata" / f"{evidence_id}.json"
        if metadata_path.exists():
            metadata_path.unlink()


# API Router
router = APIRouter()
evidence_manager = EvidenceManager()


@router.post("/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    company_id: str = "",
    description: str = "",
    tags: str = "",  # comma-separated
    linked_controls: str = "",  # comma-separated
    framework: str = "",
):
    """Upload evidence file."""
    upload_request = EvidenceUploadRequest(
        description=description or None,
        tags=[t.strip() for t in tags.split(",") if t.strip()],
        linked_controls=[c.strip() for c in linked_controls.split(",") if c.strip()],
        company_id=company_id,
        framework=framework or None,
    )

    try:
        metadata = evidence_manager.upload_evidence(
            file=file.file,
            filename=file.filename or "unknown",
            upload_request=upload_request,
            uploaded_by="current_user",  # In production would get from auth
        )
        return {"success": True, "evidence": metadata.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list/{company_id}")
async def list_evidence(
    company_id: str,
    framework: str | None = None,
    control_id: str | None = None,
    status: str | None = None,
):
    """List evidence files."""
    evidence_list = evidence_manager.list_evidence(
        company_id=company_id,
        framework=framework,
        control_id=control_id,
        status=status,
    )
    return {"evidence": [e.model_dump() for e in evidence_list]}


@router.get("/download/{evidence_id}")
async def download_evidence(evidence_id: str, company_id: str):
    """Download evidence file."""
    from fastapi.responses import Response

    try:
        content, metadata = evidence_manager.get_evidence(evidence_id, company_id)
        return Response(
            content=content,
            media_type=metadata.mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={metadata.original_filename}"
            },
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Evidence not found")


@router.delete("/{evidence_id}")
async def delete_evidence(evidence_id: str, company_id: str):
    """Delete evidence file."""
    try:
        evidence_manager.delete_evidence(evidence_id, company_id)
        return {"success": True}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Evidence not found")


@router.post("/{evidence_id}/link-control")
async def link_evidence_to_control(evidence_id: str, control_id: str):
    """Link evidence to a control."""
    try:
        metadata = evidence_manager.link_to_control(evidence_id, control_id)
        return {"success": True, "evidence": metadata.model_dump()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Evidence not found")


@router.post("/{evidence_id}/review")
async def review_evidence(
    evidence_id: str,
    status: str,  # approved, rejected
    comment: str | None = None,
):
    """Review evidence (approve/reject)."""
    try:
        metadata = evidence_manager.review_evidence(
            evidence_id=evidence_id,
            reviewer="current_user",  # In production would get from auth
            status=status,
            comment=comment,
        )
        return {"success": True, "evidence": metadata.model_dump()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Evidence not found")


@router.get("/stats/{company_id}")
async def get_evidence_stats(company_id: str):
    """Get evidence statistics."""
    # In production would query database
    return {
        "company_id": company_id,
        "total_files": 45,
        "total_size_mb": 128.5,
        "by_status": {
            "pending": 10,
            "reviewed": 8,
            "approved": 25,
            "rejected": 2,
        },
        "by_framework": {
            "fz152": 20,
            "fz187": 15,
            "gost57580": 10,
        },
        "expiring_soon": 5,
        "linked_to_controls": 40,
        "unlinked": 5,
    }
