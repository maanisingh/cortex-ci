# Phase 2.1: Multi-Layer Dependency Modeling

## Overview

Phase 2.1 implements **cross-layer dependency analysis** - understanding how entities are connected across different operational layers (legal, financial, operational, human, academic) and how disruptions cascade between them.

---

## Current Implementation Status

### Backend (COMPLETE)

| Endpoint | Status | Description |
|----------|--------|-------------|
| `GET /dependencies` | ✅ Done | List dependencies with layer filtering |
| `GET /dependencies/graph` | ✅ Done | Dependency graph for visualization |
| `GET /dependencies/layers/summary` | ✅ Done | Summary stats for each layer |
| `GET /dependencies/cross-layer-impact/{id}` | ✅ Done | Cross-layer impact analysis |
| CRUD operations | ✅ Done | Create, update, delete dependencies |

### Frontend (TODO)

| Component | Status | Description |
|-----------|--------|-------------|
| `dependencyLayersApi` | ✅ Defined | API client ready in `services/api.ts` |
| Layer Summary Dashboard | ❌ TODO | Show layer distribution and stats |
| Cross-Layer Impact View | ❌ TODO | Visual impact analysis per entity |
| Dependency Graph with Layers | ❌ TODO | Color-coded graph by layer |
| Layer Risk Weights Config | ❌ TODO | Admin UI to adjust risk weights |

---

## Dependency Layers

| Layer | Description | Risk Weight |
|-------|-------------|-------------|
| **LEGAL** | Contracts, grants, legal obligations | 1.5x |
| **FINANCIAL** | Banks, currencies, payment corridors | 1.4x |
| **OPERATIONAL** | Suppliers, logistics, IT systems | 1.0x |
| **HUMAN** | Key personnel, irreplaceable staff | 1.2x |
| **ACADEMIC** | Research partners, funding sources | 0.8x |

---

## Implementation Tasks

### Frontend Components to Build

```
src/
├── pages/
│   ├── DependencyLayers.tsx        # Layer summary dashboard
│   └── CrossLayerAnalysis.tsx      # Entity impact analysis
├── components/
│   ├── layers/
│   │   ├── LayerSummaryCard.tsx    # Stats per layer
│   │   ├── LayerDistributionChart.tsx  # Pie/bar chart
│   │   └── CrossLayerImpactGraph.tsx   # Impact visualization
│   └── dependencies/
│       └── LayerColoredGraph.tsx   # Graph with layer colors
```

### API Integration

```typescript
// Already defined in src/services/api.ts
import { dependencyLayersApi } from './services/api';

// Usage:
const summary = await dependencyLayersApi.summary();
const impact = await dependencyLayersApi.crossLayerImpact(entityId);
```

### Recommended Color Scheme

```typescript
const LAYER_COLORS = {
  legal: '#DC2626',      // Red
  financial: '#F59E0B',  // Amber
  operational: '#3B82F6', // Blue
  human: '#8B5CF6',      // Purple
  academic: '#10B981',   // Green
};
```

---

## Database Schema (Already Exists)

```sql
-- dependencies table
CREATE TABLE dependencies (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  source_entity_id UUID NOT NULL,
  target_entity_id UUID NOT NULL,
  layer VARCHAR(50) NOT NULL,  -- legal, financial, operational, human, academic
  relationship_type VARCHAR(50) NOT NULL,
  criticality INTEGER DEFAULT 5,
  is_bidirectional BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

---

## Testing Requirements

### Unit Tests
- [ ] Layer summary calculation
- [ ] Cross-layer impact scoring
- [ ] Risk weight application
- [ ] Graph generation with layer data

### Integration Tests
- [ ] API endpoint responses
- [ ] Layer filtering works correctly
- [ ] Impact calculation accuracy

### E2E Tests
- [ ] Layer summary dashboard loads
- [ ] Cross-layer analysis displays correctly
- [ ] Graph visualization with layer colors

---

## Acceptance Criteria

1. **Layer Summary Dashboard**
   - Shows count of dependencies per layer
   - Displays average criticality per layer
   - Shows total cross-layer connections

2. **Cross-Layer Impact Analysis**
   - For any entity, shows impact across all layers
   - Provides risk recommendation based on exposure
   - Lists affected entities per layer

3. **Dependency Graph Enhancement**
   - Edges colored by layer
   - Filter by layer(s)
   - Legend showing layer colors

4. **Performance**
   - Layer summary < 200ms response
   - Cross-layer impact < 500ms for 1000 dependencies
   - Graph renders < 2s for 500 nodes

---

## Files to Modify/Create

### Backend (if needed)
- `backend/app/api/v1/endpoints/dependencies.py` - Already complete
- `backend/app/models/dependency.py` - Already has layer enum

### Frontend (TODO)
- `frontend/src/pages/DependencyLayers.tsx` - NEW
- `frontend/src/pages/CrossLayerAnalysis.tsx` - NEW
- `frontend/src/components/layers/` - NEW directory
- `frontend/src/App.tsx` - Add routes
- `frontend/src/components/common/Layout.tsx` - Add nav items

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Performance with large datasets | Implement pagination, lazy loading |
| Complex graph visualization | Use existing ReactFlow, add layer colors |
| User confusion about layers | Add tooltips, documentation |

---

## Estimated Effort

| Task | Estimate |
|------|----------|
| Layer Summary Dashboard | 4 hours |
| Cross-Layer Impact View | 6 hours |
| Graph Enhancement | 4 hours |
| Testing | 4 hours |
| **Total** | **18 hours** |

---

## Next Steps After Phase 2.1

- **Phase 2.2**: Scenario Chains (COMPLETE)
- **Phase 2.3**: Risk Justification Engine (COMPLETE)
- **Phase 2.4**: Institutional Memory (COMPLETE)
- **Phase 2.5**: Controlled AI Integration (COMPLETE)
