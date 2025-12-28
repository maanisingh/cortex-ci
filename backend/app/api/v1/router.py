from fastapi import APIRouter

# Phase 2 endpoints
# Phase 4-5 endpoints
from app.api.v1.endpoints import (
    admin,
    ai_analysis,
    audit,
    auth,
    constraints,
    dashboard,
    dependencies,
    entities,
    history,
    monitoring,
    risk_justification,
    risks,
    scenario_chains,
    scenarios,
    simulations,
    websocket,
)

# Compliance Platform endpoints
from app.api.v1.endpoints.compliance import (
    audits,
    cases,
    controls,
    customers,
    evidence,
    frameworks,
    incidents,
    policies,
    russian,
    scoring,
    screening,
    training,
    transactions,
    vendors,
)
from app.api.v1.endpoints.compliance import onboarding as ru_onboarding
from app.api.v1.endpoints.compliance import workflow as ru_workflow
from app.services import reporting as ru_reporting
from app.services import evidence as ru_evidence
from app.services import notifications as ru_notifications

api_router = APIRouter()

# Core endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(entities.router, prefix="/entities", tags=["Entities"])
api_router.include_router(constraints.router, prefix="/constraints", tags=["Constraints"])
api_router.include_router(dependencies.router, prefix="/dependencies", tags=["Dependencies"])
# Risk justification must be registered BEFORE risks to avoid route conflict
api_router.include_router(
    risk_justification.router,
    prefix="/risks/justification",
    tags=["Phase 2 - Risk Justification"],
)
api_router.include_router(risks.router, prefix="/risks", tags=["Risks"])
# Scenario chains must be registered BEFORE scenarios to avoid route conflict
api_router.include_router(
    scenario_chains.router,
    prefix="/scenarios/chains",
    tags=["Phase 2 - Scenario Chains"],
)
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])

# Phase 2: Additional Features (scenario_chains and risk_justification registered above)
api_router.include_router(
    history.router, prefix="/history", tags=["Phase 2 - Institutional Memory"]
)
api_router.include_router(ai_analysis.router, prefix="/ai", tags=["Phase 2 - AI Analysis"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring & Alerts"])

# Phase 4-5: WebSocket and Advanced Features
api_router.include_router(websocket.router, prefix="", tags=["Phase 4 - WebSocket"])
api_router.include_router(simulations.router, prefix="/simulations", tags=["Phase 5 - Simulations"])

# Compliance Platform Endpoints
api_router.include_router(
    frameworks.router, prefix="/compliance/frameworks", tags=["Compliance - Frameworks"]
)
api_router.include_router(
    controls.router, prefix="/compliance/controls", tags=["Compliance - Controls"]
)
api_router.include_router(
    customers.router, prefix="/compliance/customers", tags=["Compliance - KYC/AML"]
)
api_router.include_router(
    screening.router, prefix="/compliance/screening", tags=["Compliance - Screening"]
)
api_router.include_router(
    transactions.router, prefix="/compliance/transactions", tags=["Compliance - Transactions"]
)
api_router.include_router(
    cases.router, prefix="/compliance/cases", tags=["Compliance - Case Management"]
)
api_router.include_router(
    policies.router, prefix="/compliance/policies", tags=["Compliance - Policies"]
)
api_router.include_router(
    evidence.router, prefix="/compliance/evidence", tags=["Compliance - Evidence"]
)
api_router.include_router(audits.router, prefix="/compliance/audits", tags=["Compliance - Audits"])
api_router.include_router(
    vendors.router, prefix="/compliance/vendors", tags=["Compliance - Vendor Risk"]
)
api_router.include_router(
    incidents.router, prefix="/compliance/incidents", tags=["Compliance - Incidents"]
)
api_router.include_router(
    training.router, prefix="/compliance/training", tags=["Compliance - Training"]
)
api_router.include_router(
    scoring.router, prefix="/compliance/scoring", tags=["Compliance - Scoring"]
)

# Russian Compliance (152-ФЗ, 187-ФЗ, ГОСТ 57580, ФСТЭК)
api_router.include_router(
    russian.router, prefix="/compliance/russian", tags=["Russian Compliance"]
)
api_router.include_router(
    ru_onboarding.router, prefix="/compliance/russian", tags=["Russian Compliance Onboarding"]
)
api_router.include_router(
    ru_workflow.router, prefix="/compliance/russian/workflow", tags=["Russian Compliance Workflow"]
)
api_router.include_router(
    ru_reporting.router, prefix="/compliance/russian/reports", tags=["Russian Compliance Reports"]
)
api_router.include_router(
    ru_evidence.router, prefix="/compliance/russian/evidence", tags=["Russian Compliance Evidence"]
)
api_router.include_router(
    ru_notifications.router, prefix="/compliance/russian/notifications", tags=["Russian Compliance Notifications"]
)
