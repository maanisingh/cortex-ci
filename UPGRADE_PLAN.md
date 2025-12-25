# CORTEX-CI Platform Upgrade Plan

## Executive Summary

Phase 2.1 (Multi-Layer Dependency Modeling) is now **100% COMPLETE**. This document outlines the roadmap to transform CORTEX-CI into a market-dominating sanctions compliance platform.

---

## Current State (Post Phase 2.1)

| Metric | Value |
|--------|-------|
| Backend Endpoints | 90+ |
| Frontend Pages | 26 (including new Phase 2.1 pages) |
| Database Models | 14 |
| Entities in System | 864+ |
| Test Coverage | ~15% (backend) |
| Phase 2.1 Status | 100% Complete |

---

## Phase 2.1 Completion Summary

### Completed Items:
- DependencyLayers.tsx page with layer summary dashboard
- CrossLayerAnalysis.tsx page with entity impact analysis
- Layer colors and constants (LAYER_COLORS)
- Routes in App.tsx and Layout.tsx navigation
- Backend tests for dependency layer endpoints
- Frontend tests for Phase 2.1 pages
- Phase 2.1 checklist verified at 100%

---

## Upgrade Roadmap

### Phase 3: Security Hardening (CRITICAL - Week 1-2)

| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| Fix CORS configuration (remove allow_origins=["*"]) | CRITICAL | 2h | Prevents XSS/CSRF |
| Implement API rate limiting | CRITICAL | 4h | Prevents brute force |
| Add MFA (TOTP) support | CRITICAL | 12h | Enterprise security |
| Rotate default secrets | CRITICAL | 2h | Prevents token forgery |
| Add data encryption at rest | CRITICAL | 8h | Compliance requirement |
| Implement audit log archival | CRITICAL | 6h | Regulatory compliance |
| Add input validation/sanitization | CRITICAL | 4h | Prevents SQL injection |

**Total Effort: 38 hours**

### Phase 4: Real-Time Features (HIGH - Week 3-4)

| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| WebSocket real-time alerts | HIGH | 16h | Live monitoring |
| Meilisearch UI integration | HIGH | 8h | Fast search UX |
| Bulk entity operations | HIGH | 6h | Productivity |
| Multi-format exports (CSV, Excel, PDF) | HIGH | 8h | Reporting |
| Scenario comparison view | HIGH | 10h | Analysis |
| Approval workflows | HIGH | 12h | Governance |
| Historical snapshots | HIGH | 8h | Audit trail |

**Total Effort: 68 hours**

### Phase 5: Performance & Quality (MEDIUM - Week 5-6)

| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| Query optimization | MEDIUM | 8h | 5x faster queries |
| Redis caching layer | MEDIUM | 6h | Reduced DB load |
| Database indexing | MEDIUM | 4h | Faster filtering |
| Test coverage to 60% | MEDIUM | 16h | Code quality |
| Mobile responsive design | MEDIUM | 8h | UX |
| Dark mode | MEDIUM | 4h | UX |
| Error boundaries | MEDIUM | 4h | Stability |

**Total Effort: 50 hours**

### Phase 6: Enterprise Integration (LOW - Week 7-8)

| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| OAuth2/OIDC SSO | LOW | 12h | Enterprise auth |
| Webhook system | LOW | 10h | Integration |
| Slack/Email notifications | LOW | 8h | Alerts |
| GraphQL endpoint | LOW | 16h | API flexibility |
| Advanced observability | LOW | 12h | Operations |

**Total Effort: 58 hours**

---

## Critical Security Fixes (Immediate)

### 1. CORS Configuration Fix
**File:** `/backend/app/main.py:60`

```python
# BEFORE (INSECURE)
allow_origins=["*"]

# AFTER (SECURE)
allow_origins=settings.ALLOWED_ORIGINS.split(",")  # e.g., "https://app.cortex-ci.com"
```

### 2. Rate Limiting
**New file:** `/backend/app/middleware/rate_limit.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to auth endpoint
@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
```

### 3. Secrets Management
**File:** `/backend/app/core/config.py`

```python
# Add to config
class Settings:
    SECRET_KEY: str = Field(..., env="SECRET_KEY")  # REQUIRED, no default
```

---

## Performance Improvements

### Query Optimization Example

```python
# BEFORE: N+1 queries
dependencies = await db.execute(select(Dependency))
for dep in dependencies:
    source = await db.get(Entity, dep.source_entity_id)

# AFTER: Single query with joins
query = select(Dependency).options(
    joinedload(Dependency.source_entity),
    joinedload(Dependency.target_entity)
)
```

### Caching Strategy

| Endpoint | TTL | Strategy |
|----------|-----|----------|
| /risks/summary | 5 min | Redis cache |
| /entities?type=X | 10 min | Redis cache |
| /monitoring/dashboard | 1 min | Redis cache |
| /dependencies/graph | 15 min | Redis cache |

---

## Testing Strategy

### Target Coverage by Component

| Component | Current | Target |
|-----------|---------|--------|
| Backend API | 15% | 70% |
| Backend Services | 10% | 60% |
| Frontend Pages | 8% | 50% |
| Frontend Components | 5% | 40% |
| Integration Tests | 0% | 30% |

### Test Files to Add

```
backend/tests/
├── test_auth.py
├── test_entities.py
├── test_constraints.py
├── test_risks.py
├── test_scenarios.py
├── test_ai.py
└── test_security.py

frontend/src/
├── pages/*.test.tsx (for all pages)
├── components/*.test.tsx (for all components)
└── services/api.test.ts
```

---

## Competitive Features Matrix

| Feature | Current | After Phase 3 | After Phase 4 | Market Leader |
|---------|---------|---------------|---------------|---------------|
| Multi-layer dependencies | YES | YES | YES | YES |
| Real-time alerts | NO | NO | YES | YES |
| Scenario cascades | YES | YES | YES | YES |
| Approval workflows | NO | NO | YES | YES |
| SSO/MFA | NO | YES | YES | YES |
| Advanced search | PARTIAL | PARTIAL | YES | YES |
| Export formats | JSON only | JSON only | CSV/Excel/PDF | YES |
| Mobile support | NO | NO | YES | YES |
| GraphQL API | NO | NO | NO | YES |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Security vulnerability discovered | Security audit before each phase release |
| Performance regression | Automated load testing in CI |
| Breaking API changes | API versioning (v1, v2) |
| Data loss | Automated backups + point-in-time recovery |
| Downtime during upgrade | Blue-green deployment strategy |

---

## Resource Requirements

| Phase | Duration | Engineers | Effort |
|-------|----------|-----------|--------|
| Phase 3 (Security) | 2 weeks | 2 | 38h |
| Phase 4 (Real-Time) | 2 weeks | 3 | 68h |
| Phase 5 (Quality) | 2 weeks | 2 | 50h |
| Phase 6 (Enterprise) | 2 weeks | 2 | 58h |
| **Total** | **8 weeks** | **3 avg** | **214h** |

---

## Success Metrics

### Phase 3 Success Criteria
- [ ] Zero OWASP Top 10 vulnerabilities
- [ ] MFA enabled for all admin accounts
- [ ] Rate limiting active on all endpoints
- [ ] 100% of secrets managed externally

### Phase 4 Success Criteria
- [ ] Real-time alerts delivered < 2 seconds
- [ ] Search results < 100ms
- [ ] Bulk operations support 1000+ entities
- [ ] Approval workflow adoption > 80%

### Phase 5 Success Criteria
- [ ] API response time < 200ms (95th percentile)
- [ ] Test coverage > 60%
- [ ] Mobile usability score > 90

### Phase 6 Success Criteria
- [ ] SSO integration with major providers
- [ ] Webhook delivery rate > 99.9%
- [ ] GraphQL adoption > 30% of API calls

---

## Next Immediate Steps

1. **Create Phase 3 branch:** `git checkout -b phase-3-security`
2. **Fix CORS immediately** (highest risk)
3. **Add rate limiting middleware**
4. **Implement MFA**
5. **Run security audit**

---

## Files Modified in Phase 2.1

```
CREATED:
- frontend/src/pages/DependencyLayers.tsx
- frontend/src/pages/CrossLayerAnalysis.tsx
- frontend/src/pages/DependencyLayers.test.tsx
- frontend/src/pages/CrossLayerAnalysis.test.tsx
- frontend/src/test/setup.ts
- frontend/vitest.config.ts
- backend/tests/__init__.py
- backend/tests/conftest.py
- backend/tests/test_dependencies.py

MODIFIED:
- frontend/src/App.tsx (added routes)
- frontend/src/components/common/Layout.tsx (added navigation)
- frontend/package.json (added test dependencies)
- scripts/phase21-checklist.sh (fixed grep)
```

---

## Conclusion

CORTEX-CI has a solid foundation with Phase 2.1 complete. The next critical step is **Phase 3: Security Hardening** to make the platform enterprise-ready. Following the upgrade plan will transform CORTEX-CI into a market-dominating sanctions compliance platform within 8 weeks.

**Recommended Priority:** Phase 3 Security > Phase 4 Real-Time > Phase 5 Quality > Phase 6 Enterprise
