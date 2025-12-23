from fastapi import APIRouter

from app.api.v1.endpoints import auth, entities, constraints, dependencies, risks, scenarios, audit, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(entities.router, prefix="/entities", tags=["Entities"])
api_router.include_router(constraints.router, prefix="/constraints", tags=["Constraints"])
api_router.include_router(dependencies.router, prefix="/dependencies", tags=["Dependencies"])
api_router.include_router(risks.router, prefix="/risks", tags=["Risks"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])
