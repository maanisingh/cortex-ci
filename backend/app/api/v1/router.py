from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    entities,
    constraints,
    dependencies,
    risks,
    scenarios,
    audit,
    admin,
    dashboard,
)

# Phase 2 endpoints
from app.api.v1.endpoints import (
    scenario_chains,
    risk_justification,
    history,
    ai_analysis,
    monitoring,
)

# Phase 4-5 endpoints
from app.api.v1.endpoints import websocket, simulations

api_router = APIRouter()

# Core endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(entities.router, prefix="/entities", tags=["Entities"])
api_router.include_router(
    constraints.router, prefix="/constraints", tags=["Constraints"]
)
api_router.include_router(
    dependencies.router, prefix="/dependencies", tags=["Dependencies"]
)
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
api_router.include_router(
    ai_analysis.router, prefix="/ai", tags=["Phase 2 - AI Analysis"]
)
api_router.include_router(
    monitoring.router, prefix="/monitoring", tags=["Monitoring & Alerts"]
)

# Phase 4-5: WebSocket and Advanced Features
api_router.include_router(
    websocket.router, prefix="", tags=["Phase 4 - WebSocket"]
)
api_router.include_router(
    simulations.router, prefix="/simulations", tags=["Phase 5 - Simulations"]
)
