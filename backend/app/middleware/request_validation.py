"""
Request Validation Middleware (Phase 3)
Implements input sanitization and validation.
"""

import re
from typing import Callable
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


# Dangerous patterns for SQL injection, XSS, etc.
DANGEROUS_PATTERNS = [
    # SQL Injection
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE|ALTER|TRUNCATE|EXEC|EXECUTE)\b)",
    r"(--|#|\/\*|\*\/)",
    r"(\bOR\b\s+\d+\s*=\s*\d+)",
    r"(\bAND\b\s+\d+\s*=\s*\d+)",
    # XSS
    r"(<script[^>]*>.*?</script>)",
    r"(javascript\s*:)",
    r"(on\w+\s*=)",
    r"(<\s*img[^>]+onerror\s*=)",
    # Path traversal
    r"(\.\./)",
    r"(%2e%2e/)",
    r"(\.\.\\)",
]

# Compiled patterns for performance
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in DANGEROUS_PATTERNS]

# Maximum sizes
MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB
MAX_URL_LENGTH = 2048
MAX_HEADER_SIZE = 8192


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate and sanitize incoming requests.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request before processing."""
        # Check URL length
        if len(str(request.url)) > MAX_URL_LENGTH:
            logger.warning("URL too long", path=str(request.url)[:100])
            return Response(
                content='{"detail": "URL too long"}',
                status_code=status.HTTP_414_REQUEST_URI_TOO_LONG,
                media_type="application/json",
            )

        # Check for dangerous patterns in URL
        url_str = str(request.url)
        if self._contains_dangerous_pattern(url_str):
            logger.warning(
                "Dangerous pattern in URL",
                path=str(request.url.path),
                client=request.client.host if request.client else "unknown",
            )
            return Response(
                content='{"detail": "Invalid request"}',
                status_code=status.HTTP_400_BAD_REQUEST,
                media_type="application/json",
            )

        # Check query parameters
        for key, value in request.query_params.items():
            if self._contains_dangerous_pattern(f"{key}={value}"):
                logger.warning(
                    "Dangerous pattern in query params",
                    param=key,
                    client=request.client.host if request.client else "unknown",
                )
                return Response(
                    content='{"detail": "Invalid request parameters"}',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    media_type="application/json",
                )

        # Check Content-Length header
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > MAX_BODY_SIZE:
                    logger.warning(
                        "Request body too large",
                        size=content_length,
                        client=request.client.host if request.client else "unknown",
                    )
                    return Response(
                        content='{"detail": "Request body too large"}',
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        media_type="application/json",
                    )
            except ValueError:
                pass

        # Validate Content-Type for POST/PUT/PATCH
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("Content-Type", "")
            if content_type and not self._is_valid_content_type(content_type):
                logger.warning(
                    "Invalid content type",
                    content_type=content_type,
                    client=request.client.host if request.client else "unknown",
                )
                return Response(
                    content='{"detail": "Invalid content type"}',
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    media_type="application/json",
                )

        return await call_next(request)

    def _contains_dangerous_pattern(self, text: str) -> bool:
        """Check if text contains dangerous patterns."""
        for pattern in COMPILED_PATTERNS:
            if pattern.search(text):
                return True
        return False

    def _is_valid_content_type(self, content_type: str) -> bool:
        """Check if content type is valid."""
        valid_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
        ]
        for valid in valid_types:
            if valid in content_type.lower():
                return True
        return False


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize a string value.

    - Removes dangerous patterns
    - Limits length
    - Escapes HTML entities
    """
    if not value:
        return value

    # Truncate
    value = value[:max_length]

    # Remove null bytes
    value = value.replace("\x00", "")

    # Basic HTML entity escaping
    value = (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )

    return value


def sanitize_dict(data: dict, max_depth: int = 10) -> dict:
    """
    Recursively sanitize dictionary values.
    """
    if max_depth <= 0:
        return data

    sanitized = {}
    for key, value in data.items():
        # Sanitize key
        clean_key = sanitize_string(str(key), 100)

        # Sanitize value based on type
        if isinstance(value, str):
            sanitized[clean_key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[clean_key] = sanitize_dict(value, max_depth - 1)
        elif isinstance(value, list):
            sanitized[clean_key] = [
                sanitize_dict(v, max_depth - 1) if isinstance(v, dict)
                else sanitize_string(v) if isinstance(v, str)
                else v
                for v in value
            ]
        else:
            sanitized[clean_key] = value

    return sanitized
