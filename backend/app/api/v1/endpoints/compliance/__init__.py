# Compliance Platform API Endpoints
from app.api.v1.endpoints.compliance.audits import router as audits_router
from app.api.v1.endpoints.compliance.cases import router as cases_router
from app.api.v1.endpoints.compliance.controls import router as controls_router
from app.api.v1.endpoints.compliance.customers import router as customers_router
from app.api.v1.endpoints.compliance.evidence import router as evidence_router
from app.api.v1.endpoints.compliance.frameworks import router as frameworks_router
from app.api.v1.endpoints.compliance.incidents import router as incidents_router
from app.api.v1.endpoints.compliance.policies import router as policies_router
from app.api.v1.endpoints.compliance.russian import router as russian_router
from app.api.v1.endpoints.compliance.scoring import router as scoring_router
from app.api.v1.endpoints.compliance.screening import router as screening_router
from app.api.v1.endpoints.compliance.training import router as training_router
from app.api.v1.endpoints.compliance.transactions import router as transactions_router
from app.api.v1.endpoints.compliance.vendors import router as vendors_router

__all__ = [
    "frameworks_router",
    "controls_router",
    "customers_router",
    "screening_router",
    "transactions_router",
    "policies_router",
    "evidence_router",
    "audits_router",
    "vendors_router",
    "incidents_router",
    "training_router",
    "cases_router",
    "scoring_router",
    "russian_router",
]
