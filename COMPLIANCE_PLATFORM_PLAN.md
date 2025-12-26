# Cortex-CI: Full Compliance Platform Transformation Plan

## Vision
Transform cortex-ci from a sanctions-focused tool into a **comprehensive enterprise compliance platform** covering all major compliance domains, powered by open source tools and data.

---

## Part 1: Platform Architecture

### Current State (Phase 2.5)
- Entity management (23K+ entities)
- 558+ compliance constraints across 31 types
- Multi-layer dependency modeling
- Risk scoring with justification engine
- Russia sanctions coverage
- Basic audit trails

### Target State (Full Compliance Platform)
```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CORTEX COMPLIANCE PLATFORM                       │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   AML/KYC    │  │  Regulatory  │  │    Policy    │  │    Audit     │ │
│  │  Screening   │  │  Frameworks  │  │  Management  │  │   & Evidence │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Incident   │  │ Vendor Risk  │  │   Training   │  │  Sanctions   │ │
│  │  Management  │  │  Management  │  │ & Awareness  │  │  (existing)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                        UNIFIED DATA LAYER                                │
│  Entities | Controls | Policies | Evidence | Risks | Workflows          │
├─────────────────────────────────────────────────────────────────────────┤
│                     OPEN SOURCE INTEGRATIONS                             │
│  OpenSanctions | NIST | CIS | MITRE | Wazuh | Keycloak | etc.           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Part 2: Modules & Open Source Tools

### Module 1: AML/KYC Screening
**Purpose**: Customer onboarding, identity verification, ongoing monitoring

| Component | Open Source Tool | Description |
|-----------|-----------------|-------------|
| Sanctions Screening | **OpenSanctions** | 4.3M+ entities from 100+ sources |
| Identity Verification | **Onfido OSS SDK** / **Jumio OSS** | Document verification |
| PEP Screening | **OpenSanctions PEP dataset** | Politically exposed persons |
| Fuzzy Name Matching | **OpenSanctions yente** | Matching API with scoring |
| Transaction Monitoring | **Apache Flink** | Real-time stream processing |
| Case Management | **TheHive** | Investigation workflows |
| Risk Scoring | **ML models (scikit-learn)** | Customer risk assessment |

**Data Sources**:
- OpenSanctions (consolidated global sanctions)
- OFAC SDN List (US Treasury)
- EU Consolidated Sanctions
- UN Sanctions List
- PEP databases
- Adverse media feeds

### Module 2: Regulatory Frameworks
**Purpose**: Control libraries, compliance mapping, gap analysis

| Component | Open Source Tool | Description |
|-----------|-----------------|-------------|
| Control Library | **OSCAL (NIST)** | Open Security Controls Assessment Language |
| Framework Mapping | **Crosswalk data** | Map controls across frameworks |
| Assessment Tools | **OpenSCAP** | Automated compliance checking |
| GRC Platform | **Eramba Community** | Risk & control management |
| Policy as Code | **Open Policy Agent (OPA)** | Policy enforcement |

**Frameworks Supported**:
- **NIST CSF** - Cybersecurity Framework
- **NIST 800-53** - Security Controls
- **ISO 27001/27002** - Information Security
- **SOC 2** - Trust Services Criteria
- **PCI-DSS** - Payment Card Security
- **HIPAA** - Healthcare Privacy
- **GDPR** - EU Data Protection
- **SOX** - Financial Controls
- **CIS Controls** - Critical Security Controls
- **MITRE ATT&CK** - Threat Framework

### Module 3: Policy Management
**Purpose**: Create, distribute, track acknowledgement of policies

| Component | Open Source Tool | Description |
|-----------|-----------------|-------------|
| Document Management | **Paperless-ngx** | Document storage & OCR |
| Version Control | **Git** | Policy versioning |
| Workflow Engine | **n8n** / **Temporal** | Approval workflows |
| E-Signature | **DocuSeal** | Open source e-signatures |
| Acknowledgement Tracking | **Custom (FastAPI)** | Track who read what |

### Module 4: Audit & Evidence Management
**Purpose**: Collect evidence, track findings, manage remediation

| Component | Open Source Tool | Description |
|-----------|-----------------|-------------|
| Evidence Collection | **Paperless-ngx** | Automated evidence storage |
| Log Management | **Loki** / **OpenSearch** | Centralized logging |
| SIEM | **Wazuh** | Security monitoring |
| Audit Trails | **Temporal** | Immutable audit logs |
| Finding Tracker | **Custom (FastAPI)** | Track findings & remediation |

### Module 5: Incident Management
**Purpose**: Track security incidents, breaches, response

| Component | Open Source Tool | Description |
|-----------|-----------------|-------------|
| Incident Tracking | **TheHive** | Security incident response |
| Playbooks | **Shuffle SOAR** | Automated response |
| Breach Notification | **n8n** | Automated notifications |
| Timeline Analysis | **Timesketch** | Forensic analysis |

### Module 6: Vendor Risk Management
**Purpose**: Third-party due diligence, ongoing monitoring

| Component | Open Source Tool | Description |
|-----------|-----------------|-------------|
| Vendor Questionnaires | **Custom (FastAPI)** | SIG/CAIQ based |
| Risk Scoring | **Custom ML** | Vendor risk scoring |
| Contract Management | **Docassemble** | Contract automation |
| Continuous Monitoring | **SecurityScorecard OSS** | External scanning |

### Module 7: Training & Awareness
**Purpose**: Compliance training, tracking, phishing simulations

| Component | Open Source Tool | Description |
|-----------|-----------------|-------------|
| LMS | **Moodle** / **Open edX** | Learning management |
| Phishing Simulation | **Gophish** | Phishing tests |
| Training Tracking | **Custom (FastAPI)** | Completion tracking |

### Module 8: Authentication & Security
**Purpose**: Secure access, MFA, SSO

| Component | Open Source Tool | Description |
|-----------|-----------------|-------------|
| Identity Provider | **Keycloak** | SSO, MFA, RBAC |
| Secret Management | **HashiCorp Vault** | Secrets & encryption |
| API Security | **OWASP ZAP** | Security testing |

---

## Part 3: Open Source Data Sources

### 3.1 Sanctions & Watchlists
| Source | URL | Records | Update Frequency |
|--------|-----|---------|------------------|
| **OpenSanctions** | opensanctions.org | 4.3M+ | Daily |
| OFAC SDN | treasury.gov | 12K+ | Weekly |
| EU Consolidated | europa.eu | 8K+ | Weekly |
| UN Sanctions | un.org | 2K+ | As needed |
| UK Sanctions | gov.uk | 6K+ | Weekly |

### 3.2 Regulatory Control Libraries
| Source | Format | Controls |
|--------|--------|----------|
| **NIST 800-53 Rev 5** | OSCAL JSON | 1,189 controls |
| **NIST CSF** | OSCAL JSON | 108 subcategories |
| **CIS Controls v8** | JSON/XML | 153 safeguards |
| **PCI-DSS v4** | PDF → JSON | 264 requirements |
| **ISO 27001:2022** | Custom JSON | 93 controls |
| **MITRE ATT&CK** | STIX | 200+ techniques |
| **SOC 2 TSC** | Custom JSON | 64 criteria |
| **HIPAA** | Custom JSON | 54 specifications |
| **GDPR** | Custom JSON | 99 articles |

### 3.3 Threat Intelligence
| Source | Type | URL |
|--------|------|-----|
| **MITRE ATT&CK** | TTPs | attack.mitre.org |
| **AlienVault OTX** | IOCs | otx.alienvault.com |
| **Abuse.ch** | Malware | abuse.ch |
| **CISA KEV** | Vulnerabilities | cisa.gov |
| **CVE/NVD** | Vulnerabilities | nvd.nist.gov |

### 3.4 Industry Data
| Source | Purpose |
|--------|---------|
| **LEI (GLEIF)** | Legal entity identifiers |
| **BIC/SWIFT** | Bank identifiers |
| **MCC Codes** | Merchant categories |
| **NAICS/SIC** | Industry codes |
| **Country Risk (Transparency Intl)** | CPI scores |

---

## Part 4: Database Schema Extensions

### New Tables Required

```sql
-- Regulatory Frameworks
CREATE TABLE frameworks (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    source_url TEXT,
    last_updated TIMESTAMP
);

CREATE TABLE controls (
    id UUID PRIMARY KEY,
    framework_id UUID REFERENCES frameworks(id),
    control_id VARCHAR(50),
    title TEXT,
    description TEXT,
    category VARCHAR(100),
    parent_id UUID REFERENCES controls(id)
);

CREATE TABLE control_mappings (
    source_control_id UUID REFERENCES controls(id),
    target_control_id UUID REFERENCES controls(id),
    relationship_type VARCHAR(50),
    confidence FLOAT
);

-- Policies
CREATE TABLE policies (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    version VARCHAR(20),
    status VARCHAR(50),
    owner_id UUID,
    effective_date DATE,
    review_date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE policy_acknowledgements (
    id UUID PRIMARY KEY,
    policy_id UUID REFERENCES policies(id),
    user_id UUID,
    acknowledged_at TIMESTAMP,
    ip_address INET,
    signature TEXT
);

-- Evidence & Audits
CREATE TABLE evidence (
    id UUID PRIMARY KEY,
    control_id UUID REFERENCES controls(id),
    title VARCHAR(255),
    description TEXT,
    file_path TEXT,
    collected_at TIMESTAMP,
    collected_by UUID,
    valid_from DATE,
    valid_until DATE
);

CREATE TABLE audit_findings (
    id UUID PRIMARY KEY,
    control_id UUID REFERENCES controls(id),
    finding_type VARCHAR(50),
    severity VARCHAR(20),
    description TEXT,
    remediation_plan TEXT,
    status VARCHAR(50),
    due_date DATE,
    assigned_to UUID
);

-- Vendors
CREATE TABLE vendors (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(100),
    risk_tier INTEGER,
    risk_score FLOAT,
    last_assessment_date DATE,
    next_review_date DATE,
    status VARCHAR(50)
);

CREATE TABLE vendor_assessments (
    id UUID PRIMARY KEY,
    vendor_id UUID REFERENCES vendors(id),
    assessment_type VARCHAR(100),
    score FLOAT,
    findings JSONB,
    completed_at TIMESTAMP,
    completed_by UUID
);

-- Incidents
CREATE TABLE incidents (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    severity VARCHAR(20),
    status VARCHAR(50),
    category VARCHAR(100),
    detected_at TIMESTAMP,
    reported_at TIMESTAMP,
    resolved_at TIMESTAMP,
    assigned_to UUID,
    root_cause TEXT,
    lessons_learned TEXT
);

-- Training
CREATE TABLE training_courses (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    duration_minutes INTEGER,
    required_for JSONB,
    frequency_months INTEGER
);

CREATE TABLE training_completions (
    id UUID PRIMARY KEY,
    course_id UUID REFERENCES training_courses(id),
    user_id UUID,
    completed_at TIMESTAMP,
    score FLOAT,
    certificate_url TEXT
);

-- Customer Screening (AML/KYC)
CREATE TABLE customers (
    id UUID PRIMARY KEY,
    type VARCHAR(20), -- individual, organization
    name VARCHAR(255),
    risk_rating VARCHAR(20),
    onboarding_status VARCHAR(50),
    last_reviewed DATE,
    next_review_date DATE,
    metadata JSONB
);

CREATE TABLE screening_results (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(id),
    screening_type VARCHAR(50),
    match_score FLOAT,
    matched_entity_id VARCHAR(255),
    matched_source VARCHAR(100),
    status VARCHAR(50),
    reviewed_by UUID,
    reviewed_at TIMESTAMP
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(id),
    transaction_type VARCHAR(50),
    amount DECIMAL(20,2),
    currency VARCHAR(3),
    counterparty TEXT,
    timestamp TIMESTAMP,
    risk_flags JSONB,
    status VARCHAR(50)
);
```

---

## Part 5: Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Core infrastructure for all modules

- [ ] Set up Keycloak for authentication
- [ ] Create unified database schema (above tables)
- [ ] Build base API structure for new modules
- [ ] Implement OSCAL parser for control imports
- [ ] Set up n8n for workflow automation

**Deliverables**:
- `/api/v1/frameworks` - Framework management
- `/api/v1/controls` - Control library
- `/api/v1/policies` - Policy CRUD
- SSO integration

### Phase 2: AML/KYC Screening (Weeks 3-4)
**Goal**: Full sanctions screening capability

- [ ] Integrate OpenSanctions yente API
- [ ] Build customer onboarding workflow
- [ ] Implement fuzzy matching with configurable thresholds
- [ ] Create case management for matches
- [ ] Build transaction monitoring rules engine

**Deliverables**:
- `/api/v1/customers` - Customer management
- `/api/v1/screening` - Screening operations
- `/api/v1/transactions` - Transaction monitoring
- Match review UI

### Phase 3: Regulatory Frameworks (Weeks 5-6)
**Goal**: Control library with mapping

- [ ] Import NIST 800-53, CSF, CIS Controls
- [ ] Build control mapping engine
- [ ] Create gap analysis tools
- [ ] Implement assessment workflows

**Deliverables**:
- Full control library (1500+ controls)
- Cross-framework mapping
- Gap analysis reports
- Assessment templates

### Phase 4: Policy & Evidence (Weeks 7-8)
**Goal**: Policy lifecycle and evidence collection

- [ ] Build policy editor with versioning
- [ ] Implement acknowledgement tracking
- [ ] Create evidence repository
- [ ] Link evidence to controls

**Deliverables**:
- Policy management UI
- E-signature integration
- Evidence collection workflows
- Audit trail reports

### Phase 5: Advanced Features (Weeks 9-10)
**Goal**: Vendor risk, incidents, training

- [ ] Vendor risk questionnaires (SIG-based)
- [ ] Incident response workflows
- [ ] Training module integration
- [ ] Dashboard consolidation

**Deliverables**:
- Vendor portal
- Incident management
- Training tracker
- Executive dashboards

---

## Part 6: API Structure

```
/api/v1/
├── auth/                    # Keycloak integration
│   ├── login
│   ├── logout
│   └── refresh
├── entities/                # Existing - sanctions entities
├── constraints/             # Existing - compliance constraints
├── customers/               # NEW - AML/KYC
│   ├── GET, POST, PUT
│   ├── /{id}/screen
│   ├── /{id}/transactions
│   └── /{id}/risk-assessment
├── screening/               # NEW - Watchlist screening
│   ├── POST /search
│   ├── GET /results
│   └── POST /resolve
├── frameworks/              # NEW - Regulatory
│   ├── GET, POST
│   └── /{id}/controls
├── controls/                # NEW - Control library
│   ├── GET, POST, PUT
│   ├── /{id}/evidence
│   ├── /{id}/assessments
│   └── /mappings
├── policies/                # NEW - Policy management
│   ├── GET, POST, PUT
│   ├── /{id}/versions
│   ├── /{id}/acknowledge
│   └── /{id}/acknowledgements
├── evidence/                # NEW - Evidence collection
│   ├── GET, POST
│   └── /{id}/download
├── audits/                  # NEW - Audit management
│   ├── GET, POST
│   ├── /{id}/findings
│   └── /{id}/reports
├── vendors/                 # NEW - Vendor risk
│   ├── GET, POST, PUT
│   ├── /{id}/assessments
│   └── /{id}/documents
├── incidents/               # NEW - Incident mgmt
│   ├── GET, POST, PUT
│   ├── /{id}/timeline
│   └── /{id}/response
└── training/                # NEW - Training
    ├── /courses
    ├── /assignments
    └── /completions
```

---

## Part 7: Frontend Pages

### New Pages Required

| Page | Route | Purpose |
|------|-------|---------|
| Compliance Dashboard | `/dashboard` | Unified view all modules |
| Customer Screening | `/customers` | AML/KYC management |
| Screening Queue | `/screening` | Review matches |
| Control Library | `/controls` | Browse frameworks |
| Gap Analysis | `/controls/gaps` | Find missing controls |
| Policy Library | `/policies` | Manage policies |
| Evidence Repository | `/evidence` | Upload/link evidence |
| Audit Management | `/audits` | Track audits |
| Vendor Portal | `/vendors` | Vendor risk |
| Incident Tracker | `/incidents` | Manage incidents |
| Training Center | `/training` | Assign/track training |
| Reports | `/reports` | Generate reports |

---

## Part 8: Open Source Tool Integration Plan

### Immediate Integrations (Phase 1-2)

1. **Keycloak** (Authentication)
   ```yaml
   # docker-compose addition
   keycloak:
     image: quay.io/keycloak/keycloak:latest
     environment:
       KEYCLOAK_ADMIN: admin
       KEYCLOAK_ADMIN_PASSWORD: ${KC_PASSWORD}
     ports:
       - "8080:8080"
   ```

2. **OpenSanctions yente** (Screening)
   ```yaml
   yente:
     image: ghcr.io/opensanctions/yente:latest
     ports:
       - "8000:8000"
     volumes:
       - ./data/opensanctions:/data
   ```

3. **n8n** (Workflows)
   ```yaml
   n8n:
     image: n8nio/n8n:latest
     ports:
       - "5678:5678"
     volumes:
       - ./data/n8n:/home/node/.n8n
   ```

### Later Integrations (Phase 3+)

4. **Wazuh** (SIEM/Logging)
5. **TheHive** (Incident Response)
6. **Paperless-ngx** (Document Management)
7. **Gophish** (Phishing Simulation)
8. **DocuSeal** (E-Signatures)

---

## Part 9: Data Import Scripts

### OpenSanctions Import
```python
# scripts/import_opensanctions.py
import httpx
from app.database import get_session

OPENSANCTIONS_URL = "https://data.opensanctions.org/datasets/latest/default/entities.ftm.json"

async def import_opensanctions():
    async with httpx.AsyncClient() as client:
        response = await client.get(OPENSANCTIONS_URL, follow_redirects=True)
        for line in response.iter_lines():
            entity = json.loads(line)
            # Transform and insert...
```

### NIST OSCAL Import
```python
# scripts/import_nist_oscal.py
import json

NIST_800_53_URL = "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json"

async def import_nist_controls():
    async with httpx.AsyncClient() as client:
        response = await client.get(NIST_800_53_URL)
        catalog = response.json()
        for group in catalog['catalog']['groups']:
            for control in group.get('controls', []):
                # Insert control...
```

### CIS Controls Import
```python
# Available from CIS website (requires free registration)
# https://www.cisecurity.org/controls/v8
```

---

## Part 10: Success Metrics

| Metric | Target |
|--------|--------|
| Frameworks supported | 10+ |
| Controls in library | 2,000+ |
| Entities for screening | 5M+ |
| API response time | <200ms |
| Uptime | 99.9% |
| User satisfaction | >4.5/5 |

---

## Quick Start

```bash
# 1. Add new services to docker-compose
docker-compose up -d keycloak yente n8n

# 2. Run database migrations
alembic upgrade head

# 3. Import initial data
python scripts/import_opensanctions.py
python scripts/import_nist_oscal.py
python scripts/import_cis_controls.py

# 4. Start the platform
docker-compose up -d
```

---

## Questions to Answer

Before starting implementation, decide:

1. **Priority order** - Which module first? (AML/KYC vs Regulatory vs Policy)
2. **Authentication** - Keycloak vs current auth?
3. **Data freshness** - How often to sync OpenSanctions? (Daily recommended)
4. **Multi-tenancy** - Single tenant or multi-tenant SaaS?
5. **Deployment** - Same server or distributed?

---

*Document created: December 2024*
*Last updated: December 2024*
