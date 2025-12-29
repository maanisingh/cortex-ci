"""
CORTEX-CI Main Application (Phase 3)
Government-grade Sanctions & Constraint Intelligence Platform
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import init_db
from app.middleware.rate_limit import RateLimitMiddleware, rate_limiter
from app.middleware.request_validation import RequestValidationMiddleware
from app.middleware.security import RequestLoggingMiddleware, SecurityHeadersMiddleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(
        "Starting CORTEX-CI",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down CORTEX-CI")
    await rate_limiter.close()
    logger.info("Rate limiter closed")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    redirect_slashes=True,  # Automatically redirect /path to /path/ for consistency
    description="""
    ## CORTEX-CI: Government-grade Constraint Intelligence Platform

    ### Features:
    - **Multi-Layer Dependency Modeling** (Phase 2.1)
    - **Scenario Chain Analysis** (Phase 2.2)
    - **Risk Justification Engine** (Phase 2.3)
    - **Institutional Memory** (Phase 2.4)
    - **Controlled AI Integration** (Phase 2.5)
    - **Security Hardening** (Phase 3)
    - **Real-Time Alerts** (Phase 4)
    - **Advanced Simulations** (Phase 5)

    ### Security:
    - Rate limiting enabled
    - MFA support
    - Encrypted sensitive data
    - Full audit logging
    """,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# ============================================
# SECURITY MIDDLEWARE STACK (Phase 3)
# Order matters: outermost middleware processes first
# ============================================

# 1. Trusted Host Middleware (prevent host header attacks)
if settings.is_production():
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.get_allowed_hosts_list() + ["*.cortex-ci.com"],
    )

# 2. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 3. Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# 4. Request Validation Middleware (input sanitization)
app.add_middleware(RequestValidationMiddleware)

# 5. Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# 6. CORS Middleware (FIXED - no more allow_origins=["*"])
cors_origins = settings.get_allowed_origins_list()
if settings.is_development():
    # Allow localhost in development
    cors_origins.extend(
        [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
    )
    cors_origins = list(set(cors_origins))  # Deduplicate

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Tenant-ID",
        "X-Request-ID",
        "X-CSRF-Token",
    ],
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "X-Request-ID",
    ],
    max_age=600,  # Cache preflight for 10 minutes
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "security": {
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "mfa_enabled": settings.MFA_ENABLED,
            "encryption": settings.ENCRYPT_SENSITIVE_FIELDS,
        },
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "redoc": f"{settings.API_V1_PREFIX}/redoc",
        "phases": {
            "phase_2_1": "Multi-Layer Dependency Modeling - Complete",
            "phase_2_2": "Scenario Chains - Complete",
            "phase_2_3": "Risk Justification - Complete",
            "phase_2_4": "Institutional Memory - Complete",
            "phase_2_5": "AI Integration - Complete",
            "phase_3": "Security Hardening - Active",
            "phase_4": "Real-Time Features - Planned",
            "phase_5": "Advanced Simulations - Planned",
            "phase_6": "Massive Data - Planned",
        },
    }
