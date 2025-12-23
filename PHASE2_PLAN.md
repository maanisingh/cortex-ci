# CORTEX-CI Phase 2: Operational Authority

**Goal:** Make the system indispensable
**Timeline:** 6-9 months
**Status:** 📋 PLANNING

---

## Executive Summary

Phase 2 transforms CORTEX-CI from a useful monitoring tool into required institutional infrastructure. The focus is on:

1. **Multi-layer dependency modeling** - Beyond single graphs
2. **Scenario chains** - Cascading effect prediction
3. **Risk justification engine** - Legal defensibility
4. **Institutional memory** - Survive leadership changes
5. **Controlled AI** - Bounded intelligence

---

## 2.1 Multi-Layer Dependency Modeling

### Current State
- Single dependency graph (32 relationships)
- Basic source → target mapping

### Target State
Five distinct dependency layers:

| Layer | Description | Example |
|-------|-------------|---------|
| **Legal** | Contracts, grants, obligations | "Contract ABC requires vendor X" |
| **Financial** | Banks, currencies, payment corridors | "Payments route through Bank Y" |
| **Operational** | Suppliers, logistics, IT systems | "Server hosted by Provider Z" |
| **Human** | Key personnel, irreplaceable staff | "Project lead is Person W" |
| **Academic** | Research partners, funding sources | "Grant from Foundation V" |

### Implementation Tasks

```
[ ] Create DependencyLayer enum with 5 layers
[ ] Update Dependency model with layer field
[ ] Add layer-specific risk weights
[ ] Build cross-layer impact calculator
[ ] Create layer visualization API
[ ] Add layer-filtered views in dashboard
```

### API Endpoints

```
GET  /api/v1/dependencies?layer=financial
GET  /api/v1/dependencies/cross-layer-impact/{entity_id}
GET  /api/v1/dependencies/layers/summary
POST /api/v1/dependencies (with layer field)
```

---

## 2.2 Scenario Chains

### Current State
- Single scenario: "If X happens → Y breaks"
- Point-in-time analysis

### Target State
Multi-step cascading scenarios:
- "If X happens → Y breaks → Z escalates in 30 days"
- Second-order and third-order effects
- Time-delayed failure prediction

### Data Model

```python
class ScenarioChain:
    id: UUID
    name: str
    description: str

    # Chain steps
    trigger_event: str
    immediate_effects: List[Effect]
    delayed_effects: List[DelayedEffect]  # with time_delay_days

    # Analysis
    total_entities_affected: int
    max_cascade_depth: int
    estimated_timeline_days: int
```

### Implementation Tasks

```
[ ] Create ScenarioChain model
[ ] Create Effect and DelayedEffect models
[ ] Build cascade simulator engine
[ ] Add time-based impact propagation
[ ] Create scenario chain visualization
[ ] Add scenario comparison feature
```

---

## 2.3 Risk Justification Engine

### Current State
- Risk scores with basic factors
- No explanation capability

### Target State
Every risk rating includes:
- **Why this rating?** - Factor breakdown
- **What assumptions?** - Documented inputs
- **Which sources?** - Citation trail
- **What uncertainty?** - Confidence intervals

### Legal Defense Output

```json
{
  "entity_id": "...",
  "risk_score": 78.5,
  "level": "HIGH",
  "justification": {
    "primary_factors": [
      {
        "factor": "country_risk",
        "contribution": 35.2,
        "source": "OFAC SDN List",
        "evidence": "Entity located in sanctioned jurisdiction (RU)"
      },
      {
        "factor": "direct_match",
        "contribution": 30.0,
        "source": "UN Consolidated List",
        "evidence": "Exact name match: UN-12345"
      }
    ],
    "assumptions": [
      "Country code derived from registered address",
      "Name matching uses exact match algorithm"
    ],
    "uncertainty": {
      "confidence": 0.85,
      "factors": ["Possible name variations not checked"]
    },
    "generated_at": "2025-12-23T22:00:00Z",
    "analyst_can_override": true
  }
}
```

### Implementation Tasks

```
[ ] Create RiskJustification model
[ ] Track factor contributions in risk calculation
[ ] Add source citation to each factor
[ ] Build uncertainty quantification
[ ] Create justification export (PDF)
[ ] Add analyst override capability with audit
```

---

## 2.4 Institutional Memory Mode

### Current State
- Current snapshot only
- No historical comparison
- Knowledge lost on staff turnover

### Target State
- Timeline views across years
- Historical constraint comparisons
- "Lessons learned" archive
- Decision outcome tracking

### Features

| Feature | Description |
|---------|-------------|
| **Timeline View** | See entity risk over time |
| **Constraint History** | What changed and when |
| **Outcome Tracking** | Link decisions to results |
| **Knowledge Base** | Searchable lessons learned |
| **Transition Reports** | Leadership handoff docs |

### Data Model

```python
class HistoricalSnapshot:
    id: UUID
    entity_id: UUID
    snapshot_date: date
    risk_score: Decimal
    constraints_applied: List[UUID]
    notes: str

class DecisionOutcome:
    id: UUID
    decision_date: date
    decision_summary: str
    entities_involved: List[UUID]
    outcome_date: date
    outcome_summary: str
    lessons_learned: str
```

### Implementation Tasks

```
[ ] Create HistoricalSnapshot model
[ ] Add daily snapshot scheduler
[ ] Create DecisionOutcome model
[ ] Build timeline visualization API
[ ] Add constraint diff comparison
[ ] Create transition report generator
```

---

## 2.5 Controlled AI Integration

### Current State
- Deterministic scoring only
- No ML/AI components

### Target State
- **Pattern detection** - Anomaly identification
- **Risk acceleration** - Stress test simulation
- **Explanation summaries** - Natural language reports

### Boundaries (NEVER)
- ❌ Political forecasting
- ❌ Prescriptive decisions
- ❌ Opaque scoring
- ❌ Autonomous actions

### Boundaries (ALLOWED)
- ✅ Pattern detection with human review
- ✅ Anomaly flagging for investigation
- ✅ Report summarization
- ✅ Scenario acceleration

### Implementation

```python
class AIAnalysis:
    id: UUID
    analysis_type: str  # "anomaly", "pattern", "summary"
    input_data: dict
    output: dict
    confidence: float
    model_version: str
    requires_human_approval: bool
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
```

### Implementation Tasks

```
[ ] Create AIAnalysis model
[ ] Implement anomaly detection (isolation forest)
[ ] Add pattern detection (clustering)
[ ] Build human approval workflow
[ ] Create model cards for transparency
[ ] Add explainability reports
```

---

## Database Migrations Required

```sql
-- Phase 2 migrations

-- 2.1 Multi-layer dependencies
ALTER TABLE dependencies ADD COLUMN layer VARCHAR(50) DEFAULT 'operational';
CREATE TYPE dependency_layer AS ENUM ('legal', 'financial', 'operational', 'human', 'academic');

-- 2.2 Scenario chains
CREATE TABLE scenario_chains (...);
CREATE TABLE chain_effects (...);

-- 2.3 Risk justification
CREATE TABLE risk_justifications (...);
ALTER TABLE risk_scores ADD COLUMN justification_id UUID;

-- 2.4 Institutional memory
CREATE TABLE historical_snapshots (...);
CREATE TABLE decision_outcomes (...);

-- 2.5 AI analysis
CREATE TABLE ai_analyses (...);
```

---

## API Additions

### New Endpoints

```
# Multi-layer dependencies
GET  /api/v1/dependencies/layers
GET  /api/v1/dependencies/cross-impact/{entity_id}

# Scenario chains
POST /api/v1/scenarios/chains
GET  /api/v1/scenarios/chains/{id}/simulate

# Risk justification
GET  /api/v1/risks/{entity_id}/justification
GET  /api/v1/risks/{entity_id}/justification/export

# Institutional memory
GET  /api/v1/history/entity/{entity_id}/timeline
GET  /api/v1/history/constraints/changes
POST /api/v1/history/decisions

# AI analysis
POST /api/v1/ai/analyze
GET  /api/v1/ai/analyses/{id}
POST /api/v1/ai/analyses/{id}/approve
```

---

## Success Metrics

| Metric | Phase 1 | Phase 2 Target |
|--------|---------|----------------|
| Entities | 23,364 | 100,000+ |
| Dependency layers | 1 | 5 |
| Scenario depth | 1 | 3+ cascade levels |
| Users | 4 | 20+ |
| Risk justification | None | 100% coverage |
| Historical data | None | 1+ year retention |

---

## Timeline

| Month | Focus |
|-------|-------|
| 1-2 | Multi-layer dependencies |
| 2-3 | Scenario chains |
| 3-4 | Risk justification engine |
| 4-5 | Institutional memory |
| 5-6 | Controlled AI integration |
| 6-7 | Testing & refinement |
| 7-9 | Documentation & training |

---

## Next Steps

To begin Phase 2:

1. **Prioritize** - Which feature first?
2. **Allocate** - Developer resources
3. **Migrate** - Database schema updates
4. **Implement** - Feature by feature
5. **Test** - With real institutional users

---

*Document created: December 23, 2025*
*Phase 2 estimated start: Q1 2026*
