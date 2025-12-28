from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str
    tenant_id: str
    role: str
    exp: datetime
    iat: datetime
    type: str


class LoginRequest(BaseModel):
    """Login request."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    tenant_slug: str | None = None
    mfa_code: str | None = Field(None, min_length=6, max_length=6)


class LoginResponse(BaseModel):
    """Login response - may require MFA."""

    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    mfa_required: bool = False
    mfa_token: str | None = None


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    job_title: str | None = None
    department: str | None = None


class PasswordChangeRequest(BaseModel):
    """Password change request."""

    current_password: str
    new_password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    """Token refresh request."""

    refresh_token: str


# MFA/TOTP Schemas (Phase 3 Security)
class MFASetupResponse(BaseModel):
    """MFA setup response with secret and QR code."""

    secret: str
    provisioning_uri: str
    backup_codes: list[str]


class MFAVerifyRequest(BaseModel):
    """MFA verification request."""

    code: str = Field(..., min_length=6, max_length=6)


class MFAVerifyResponse(BaseModel):
    """MFA verification response."""

    verified: bool
    message: str


class MFALoginVerifyRequest(BaseModel):
    """MFA login verification (second step of MFA login)."""

    mfa_token: str
    code: str = Field(..., min_length=6, max_length=6)


class MFABackupCodeRequest(BaseModel):
    """Request to use a backup code."""

    mfa_token: str
    backup_code: str = Field(..., min_length=8, max_length=12)


class MFADisableRequest(BaseModel):
    """Request to disable MFA."""

    password: str
    code: str = Field(..., min_length=6, max_length=6)


class MFAStatusResponse(BaseModel):
    """MFA status for current user."""

    mfa_enabled: bool
    mfa_verified_at: datetime | None = None
    backup_codes_remaining: int = 0
