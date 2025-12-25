#!/usr/bin/env python3
"""Populate Cortex CI with realistic AI/ML governance data"""

import httpx

BASE_URL = "https://cortex.alexandratechlab.com/api/v1"


def get_token():
    response = httpx.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@cortex.io", "password": "Admin123!"},
        timeout=30,
    )
    return response.json()["access_token"]


def api_call(method, endpoint, token, data=None):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        if method == "POST":
            r = httpx.post(
                f"{BASE_URL}{endpoint}", json=data, headers=headers, timeout=30
            )
        elif method == "GET":
            r = httpx.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=30)
        elif method == "DELETE":
            r = httpx.delete(f"{BASE_URL}{endpoint}", headers=headers, timeout=30)
        return r
    except Exception as e:
        print(f"    Error: {e}")
        return None


def main():
    token = get_token()
    print("Authenticated successfully")

    # === ENTITIES ===
    print("\nCreating entities...")
    # Use valid entity types: organization, individual, location, financial, vessel, aircraft
    # Store actual entity type in custom_data.entity_subtype
    entities = [
        # AI/ML Models - use "organization" type with entity_subtype in custom_data
        {
            "name": "Credit Scoring Model v3.2",
            "type": "organization",
            "category": "ML Model",
            "subcategory": "Credit Risk",
            "criticality": 5,
            "tags": ["production", "regulated", "high-risk", "ai-model"],
            "custom_data": {
                "entity_subtype": "ai_model",
                "model_type": "XGBoost",
                "accuracy": "94.2%",
                "last_trained": "2024-12-01",
                "features": 47,
                "training_samples": 2500000,
            },
        },
        {
            "name": "Fraud Detection System",
            "type": "organization",
            "category": "ML Model",
            "subcategory": "Fraud Prevention",
            "criticality": 5,
            "tags": ["production", "real-time", "critical", "ai-model"],
            "custom_data": {
                "entity_subtype": "ai_model",
                "model_type": "Ensemble",
                "precision": "99.7%",
                "recall": "87.3%",
                "latency_ms": 12,
            },
        },
        {
            "name": "Customer Churn Predictor",
            "type": "organization",
            "category": "ML Model",
            "subcategory": "Customer Analytics",
            "criticality": 3,
            "tags": ["production", "marketing", "ai-model"],
            "custom_data": {
                "entity_subtype": "ai_model",
                "model_type": "LSTM",
                "auc_roc": "0.89",
                "prediction_window": "30 days",
            },
        },
        {
            "name": "Resume Screening AI",
            "type": "organization",
            "category": "ML Model",
            "subcategory": "HR Automation",
            "criticality": 5,
            "tags": ["production", "regulated", "bias-sensitive", "ai-model"],
            "custom_data": {
                "entity_subtype": "ai_model",
                "model_type": "BERT",
                "languages": ["en", "es", "fr"],
                "bias_audit_date": "2024-11-15",
            },
        },
        {
            "name": "Loan Default Predictor",
            "type": "organization",
            "category": "ML Model",
            "subcategory": "Credit Risk",
            "criticality": 5,
            "tags": ["production", "regulated", "ai-model"],
            "custom_data": {
                "entity_subtype": "ai_model",
                "model_type": "LightGBM",
                "gini_coefficient": "0.72",
                "population_stability": "0.03",
            },
        },
        {
            "name": "Dynamic Pricing Engine",
            "type": "organization",
            "category": "ML Model",
            "subcategory": "Pricing",
            "criticality": 4,
            "tags": ["production", "revenue-critical", "ai-model"],
            "custom_data": {
                "entity_subtype": "ai_model",
                "model_type": "PPO",
                "revenue_lift": "8.3%",
                "fairness_score": "0.91",
            },
        },
        {
            "name": "Sentiment Analysis API",
            "type": "organization",
            "category": "NLP Model",
            "subcategory": "Text Analytics",
            "criticality": 2,
            "tags": ["production", "customer-feedback", "ai-model"],
            "custom_data": {
                "entity_subtype": "ai_model",
                "model_type": "RoBERTa",
                "accuracy": "91.5%",
                "categories": 5,
            },
        },
        {
            "name": "Document Classification System",
            "type": "organization",
            "category": "NLP Model",
            "subcategory": "Document Processing",
            "criticality": 3,
            "tags": ["production", "compliance", "ai-model"],
            "custom_data": {
                "entity_subtype": "ai_model",
                "model_type": "DistilBERT",
                "categories": 23,
                "throughput": "1000 docs/min",
            },
        },
        {
            "name": "Image Recognition Model",
            "type": "organization",
            "category": "Computer Vision",
            "subcategory": "Object Detection",
            "criticality": 3,
            "tags": ["production", "ai-model"],
            "custom_data": {
                "entity_subtype": "ai_model",
                "model_type": "YOLOv8",
                "mAP": "0.87",
                "fps": 45,
            },
        },
        {
            "name": "Speech-to-Text Engine",
            "type": "organization",
            "category": "Speech Model",
            "subcategory": "Transcription",
            "criticality": 3,
            "tags": ["production", "customer-service", "ai-model"],
            "custom_data": {
                "entity_subtype": "ai_model",
                "model_type": "Whisper",
                "wer": "4.2%",
                "languages": 50,
            },
        },
        # Data Systems
        {
            "name": "Customer Data Platform",
            "type": "organization",
            "category": "Data Platform",
            "subcategory": "CDP",
            "criticality": 5,
            "tags": ["production", "pii", "critical", "data-system"],
            "custom_data": {
                "entity_subtype": "data_system",
                "records": 8500000,
                "sources": 12,
                "pii_fields": 34,
                "encryption": "AES-256",
            },
        },
        {
            "name": "Training Data Lake",
            "type": "organization",
            "category": "Data Lake",
            "subcategory": "ML Training",
            "criticality": 4,
            "tags": ["production", "ml-training", "data-system"],
            "custom_data": {
                "entity_subtype": "data_system",
                "size_tb": 45,
                "datasets": 156,
                "labeling_method": "human + synthetic",
            },
        },
        {
            "name": "Feature Store",
            "type": "organization",
            "category": "ML Infrastructure",
            "subcategory": "Feature Engineering",
            "criticality": 5,
            "tags": ["production", "ml-serving", "data-system"],
            "custom_data": {
                "entity_subtype": "data_system",
                "features": 523,
                "refresh_rate": "hourly",
                "serving_latency_ms": 5,
            },
        },
        {
            "name": "Model Registry",
            "type": "organization",
            "category": "MLOps",
            "subcategory": "Model Management",
            "criticality": 4,
            "tags": ["production", "governance", "data-system"],
            "custom_data": {
                "entity_subtype": "data_system",
                "models_tracked": 34,
                "deployments": 89,
                "experiments": 1250,
            },
        },
        {
            "name": "Real-time Event Stream",
            "type": "organization",
            "category": "Data Pipeline",
            "subcategory": "Streaming",
            "criticality": 5,
            "tags": ["production", "real-time", "data-system"],
            "custom_data": {
                "entity_subtype": "data_system",
                "events_per_second": 50000,
                "topics": 45,
                "retention_days": 7,
            },
        },
        # Processes (using system type for abstract entities)
        {
            "name": "Model Validation Process",
            "type": "system",
            "category": "Governance",
            "subcategory": "Model Risk",
            "criticality": 5,
            "tags": ["mandatory", "regulated", "process"],
            "custom_data": {
                "entity_subtype": "process",
                "stages": 7,
                "avg_duration_days": 14,
                "approval_required": True,
            },
        },
        {
            "name": "Data Quality Pipeline",
            "type": "system",
            "category": "Data Ops",
            "subcategory": "Quality Assurance",
            "criticality": 4,
            "tags": ["automated", "daily", "process"],
            "custom_data": {
                "entity_subtype": "process",
                "checks": 45,
                "run_frequency": "daily",
                "alert_threshold": 0.95,
            },
        },
        {
            "name": "Model Retraining Pipeline",
            "type": "system",
            "category": "MLOps",
            "subcategory": "Training",
            "criticality": 4,
            "tags": ["automated", "scheduled", "process"],
            "custom_data": {
                "entity_subtype": "process",
                "trigger": "performance + drift",
                "frequency": "weekly review",
                "approval": "automated",
            },
        },
        {
            "name": "Bias Monitoring Process",
            "type": "system",
            "category": "Governance",
            "subcategory": "Fairness",
            "criticality": 5,
            "tags": ["mandatory", "continuous", "process"],
            "custom_data": {
                "entity_subtype": "process",
                "metrics": ["demographic_parity", "equalized_odds", "calibration"],
                "groups": 8,
            },
        },
        {
            "name": "Incident Response Process",
            "type": "system",
            "category": "Operations",
            "subcategory": "Incident Management",
            "criticality": 5,
            "tags": ["mandatory", "24x7", "process"],
            "custom_data": {
                "entity_subtype": "process",
                "sla_minutes": 15,
                "escalation_levels": 3,
            },
        },
        # Teams
        {
            "name": "ML Engineering Team",
            "type": "organization",
            "category": "Team",
            "subcategory": "Machine Learning",
            "criticality": 4,
            "tags": ["core-team", "team"],
            "custom_data": {
                "entity_subtype": "team",
                "headcount": 12,
                "skills": ["Python", "TensorFlow", "Spark"],
                "manager": "Sarah Chen",
            },
        },
        {
            "name": "AI Ethics Committee",
            "type": "organization",
            "category": "Team",
            "subcategory": "Ethics",
            "criticality": 5,
            "tags": ["cross-functional", "oversight", "team"],
            "custom_data": {
                "entity_subtype": "team",
                "members": 8,
                "meeting_frequency": "bi-weekly",
                "charter_date": "2023-01-15",
            },
        },
        {
            "name": "Data Science Team",
            "type": "organization",
            "category": "Team",
            "subcategory": "Data Science",
            "criticality": 3,
            "tags": ["research", "team"],
            "custom_data": {
                "entity_subtype": "team",
                "headcount": 8,
                "focus_areas": ["NLP", "Computer Vision", "Time Series"],
            },
        },
        {
            "name": "Model Risk Management",
            "type": "organization",
            "category": "Team",
            "subcategory": "Model Risk",
            "criticality": 5,
            "tags": ["second-line", "validation", "team"],
            "custom_data": {
                "entity_subtype": "team",
                "headcount": 5,
                "certifications": ["FRM", "PRM"],
                "reports_to": "CRO",
            },
        },
        {
            "name": "Data Engineering Team",
            "type": "organization",
            "category": "Team",
            "subcategory": "Data Engineering",
            "criticality": 4,
            "tags": ["core-team", "team"],
            "custom_data": {
                "entity_subtype": "team",
                "headcount": 10,
                "platforms": ["Spark", "Kafka", "Airflow"],
            },
        },
        # Infrastructure
        {
            "name": "GPU Training Cluster",
            "type": "asset",
            "category": "Infrastructure",
            "subcategory": "GPU Cluster",
            "criticality": 4,
            "tags": ["on-premise", "training", "infrastructure"],
            "custom_data": {
                "entity_subtype": "infrastructure",
                "gpus": 128,
                "gpu_type": "A100",
                "total_vram_gb": 5120,
            },
        },
        {
            "name": "Model Serving Platform",
            "type": "asset",
            "category": "Infrastructure",
            "subcategory": "Inference",
            "criticality": 5,
            "tags": ["production", "kubernetes", "infrastructure"],
            "custom_data": {
                "entity_subtype": "infrastructure",
                "max_rps": 100000,
                "regions": 3,
                "availability": "99.95%",
            },
        },
        {
            "name": "ML Experiment Platform",
            "type": "asset",
            "category": "Infrastructure",
            "subcategory": "Experimentation",
            "criticality": 3,
            "tags": ["development", "infrastructure"],
            "custom_data": {
                "entity_subtype": "infrastructure",
                "experiments": 5000,
                "artifacts_tb": 12,
                "users": 45,
            },
        },
        {
            "name": "Data Warehouse",
            "type": "asset",
            "category": "Infrastructure",
            "subcategory": "Analytics",
            "criticality": 4,
            "tags": ["production", "analytics", "infrastructure"],
            "custom_data": {
                "entity_subtype": "infrastructure",
                "size_pb": 2.5,
                "tables": 450,
                "daily_queries": 50000,
            },
        },
        # Vendors
        {
            "name": "OpenAI API Integration",
            "type": "organization",
            "category": "Vendor",
            "subcategory": "LLM Provider",
            "criticality": 3,
            "tags": ["external", "api", "vendor"],
            "custom_data": {
                "entity_subtype": "vendor",
                "model": "gpt-4-turbo",
                "monthly_spend": 45000,
                "use_cases": 5,
            },
        },
        {
            "name": "AWS SageMaker",
            "type": "organization",
            "category": "Vendor",
            "subcategory": "ML Platform",
            "criticality": 4,
            "tags": ["external", "cloud", "vendor"],
            "custom_data": {
                "entity_subtype": "vendor",
                "monthly_cost": 85000,
                "endpoints": 12,
                "training_jobs_monthly": 150,
            },
        },
        {
            "name": "Anthropic Claude Integration",
            "type": "organization",
            "category": "Vendor",
            "subcategory": "LLM Provider",
            "criticality": 3,
            "tags": ["external", "api", "vendor"],
            "custom_data": {
                "entity_subtype": "vendor",
                "model": "claude-3-opus",
                "monthly_spend": 32000,
                "use_cases": 3,
            },
        },
        {
            "name": "Hugging Face Enterprise",
            "type": "organization",
            "category": "Vendor",
            "subcategory": "Model Hub",
            "criticality": 2,
            "tags": ["external", "models", "vendor"],
            "custom_data": {
                "entity_subtype": "vendor",
                "private_models": 23,
                "monthly_cost": 5000,
            },
        },
        {
            "name": "Databricks",
            "type": "organization",
            "category": "Vendor",
            "subcategory": "Data Platform",
            "criticality": 4,
            "tags": ["external", "data", "vendor"],
            "custom_data": {
                "entity_subtype": "vendor",
                "monthly_cost": 120000,
                "workspaces": 5,
                "users": 75,
            },
        },
    ]

    entity_ids = {}

    # First, fetch existing entities
    r = api_call("GET", "/entities?page_size=100", token)
    if r and r.status_code == 200:
        existing = r.json().get("items", [])
        for e in existing:
            entity_ids[e["name"]] = e["id"]
        print(f"  Found {len(existing)} existing entities")

    # Create new entities
    for entity in entities:
        if entity["name"] in entity_ids:
            print(f"  Exists: {entity['name']}")
            continue
        r = api_call("POST", "/entities", token, entity)
        if r and r.status_code in [200, 201]:
            entity_ids[entity["name"]] = r.json()["id"]
            print(f"  Created: {entity['name']}")
        else:
            err = r.text[:100] if r else "No response"
            print(f"  Failed: {entity['name']} - {err}")

    # === CONSTRAINTS ===
    print("\nCreating constraints...")
    constraints = [
        # Regulatory
        {
            "name": "EU AI Act - High Risk Classification",
            "type": "regulation",
            "description": "AI systems used for credit scoring, employment decisions, and critical infrastructure are classified as high-risk under EU AI Act.",
            "reference_code": "EU-AI-ACT-6",
            "source_document": "EU AI Act Article 6",
            "effective_date": "2024-08-01",
            "expiry_date": "2030-12-31",
            "severity": "critical",
            "requirements": {
                "conditions": [
                    "Risk assessment required",
                    "Human oversight mandatory",
                    "Transparency obligations",
                ],
                "documentation": ["Conformity assessment", "Technical documentation"],
            },
        },
        {
            "name": "ECOA Fair Lending Requirements",
            "type": "regulation",
            "description": "Equal Credit Opportunity Act prohibits discrimination in credit decisions.",
            "reference_code": "ECOA-1691",
            "source_document": "15 U.S.C. § 1691",
            "effective_date": "1974-10-28",
            "severity": "critical",
            "requirements": {
                "conditions": [
                    "Adverse action notice required",
                    "Non-discrimination in lending",
                ],
                "documentation": ["Adverse action records"],
            },
        },
        {
            "name": "GDPR Automated Decision Making",
            "type": "regulation",
            "description": "Article 22 rights regarding automated individual decision-making including profiling.",
            "reference_code": "GDPR-22",
            "source_document": "GDPR Article 22",
            "effective_date": "2018-05-25",
            "severity": "high",
            "requirements": {
                "conditions": [
                    "Right to human intervention",
                    "Explainability required",
                    "Impact assessment",
                ],
                "documentation": ["DPIA documentation"],
            },
        },
        {
            "name": "CCPA AI Disclosure",
            "type": "regulation",
            "description": "California Consumer Privacy Act requirements for automated decision-making disclosure.",
            "reference_code": "CCPA-1798",
            "source_document": "CCPA Section 1798.185",
            "effective_date": "2023-01-01",
            "severity": "high",
            "requirements": {
                "conditions": ["Opt-out rights", "Disclosure requirements"],
                "documentation": ["Privacy notice"],
            },
        },
        {
            "name": "NYC Local Law 144",
            "type": "regulation",
            "description": "NYC law requiring bias audits for automated employment decision tools.",
            "reference_code": "NYC-LL144",
            "source_document": "NYC Local Law 144",
            "effective_date": "2023-07-05",
            "severity": "high",
            "requirements": {
                "conditions": [
                    "Annual bias audit",
                    "Public disclosure",
                    "Candidate notice",
                ],
                "documentation": ["Bias audit report", "Public summary"],
            },
        },
        {
            "name": "SR 11-7 Model Risk Management",
            "type": "regulation",
            "description": "Federal Reserve guidance on model risk management for banking institutions.",
            "reference_code": "SR-11-7",
            "source_document": "SR Letter 11-7",
            "effective_date": "2011-04-04",
            "severity": "critical",
            "requirements": {
                "conditions": [
                    "Model validation",
                    "Governance framework",
                    "Independent review",
                ],
                "documentation": ["Model documentation", "Validation report"],
            },
        },
        {
            "name": "FCRA Adverse Action",
            "type": "regulation",
            "description": "Fair Credit Reporting Act requirements for adverse action notices.",
            "reference_code": "FCRA-1681m",
            "source_document": "15 U.S.C. § 1681m",
            "effective_date": "1970-10-26",
            "severity": "critical",
            "requirements": {
                "conditions": ["Adverse action notice", "Reason codes required"],
                "documentation": ["Consumer notification records"],
            },
        },
        # Compliance/Policy
        {
            "name": "Model Documentation Standards",
            "type": "compliance",
            "description": "Internal policy requiring comprehensive documentation for all production ML models.",
            "reference_code": "MRM-001",
            "source_document": "Internal Policy MRM-001",
            "effective_date": "2023-06-01",
            "severity": "high",
            "requirements": {
                "conditions": [
                    "Model card required",
                    "Data lineage documented",
                    "Limitations disclosed",
                ],
                "documentation": ["Model card", "Technical specification"],
            },
        },
        {
            "name": "Training Data Governance",
            "type": "compliance",
            "description": "Requirements for training data quality, provenance tracking, and consent verification.",
            "reference_code": "DG-003",
            "source_document": "Internal Policy DG-003",
            "effective_date": "2023-09-01",
            "severity": "high",
            "requirements": {
                "conditions": [
                    "Data provenance tracked",
                    "Consent verified",
                    "Quality metrics met",
                ],
                "documentation": ["Data lineage report", "Consent records"],
            },
        },
        {
            "name": "AI Ethics Review Policy",
            "type": "policy",
            "description": "Mandatory ethics review for AI systems with significant human impact.",
            "reference_code": "ETH-001",
            "source_document": "Ethics Committee Charter",
            "effective_date": "2023-01-15",
            "severity": "high",
            "requirements": {
                "conditions": ["Ethics assessment completed", "Stakeholder review"],
                "documentation": ["Ethics review report"],
            },
        },
        {
            "name": "Model Performance Monitoring",
            "type": "compliance",
            "description": "Requirements for ongoing monitoring of model performance and drift detection.",
            "reference_code": "MRM-002",
            "source_document": "Internal Policy MRM-002",
            "effective_date": "2023-06-01",
            "severity": "high",
            "requirements": {
                "conditions": [
                    "Performance metrics tracked",
                    "Drift detection enabled",
                    "Alert thresholds set",
                ],
                "documentation": ["Monitoring dashboard", "Alert configuration"],
            },
        },
        {
            "name": "Third-Party AI Vendor Policy",
            "type": "compliance",
            "description": "Due diligence and ongoing monitoring requirements for third-party AI/ML vendors.",
            "reference_code": "VND-001",
            "source_document": "Vendor Management Policy",
            "effective_date": "2024-01-01",
            "severity": "high",
            "requirements": {
                "conditions": [
                    "Vendor assessment completed",
                    "Audit rights secured",
                    "Exit strategy defined",
                ],
                "documentation": ["Vendor assessment", "Contract terms"],
            },
        },
        # Contractual
        {
            "name": "OpenAI Usage Policy Compliance",
            "type": "contractual",
            "description": "Contractual obligations under OpenAI terms of service including usage restrictions.",
            "reference_code": "OAI-TOS",
            "source_document": "OpenAI Enterprise Agreement",
            "effective_date": "2024-01-01",
            "expiry_date": "2025-12-31",
            "severity": "medium",
            "requirements": {
                "conditions": ["Usage monitoring enabled", "Content filtering active"],
                "documentation": ["Usage logs"],
            },
        },
        {
            "name": "AWS Data Processing Agreement",
            "type": "contractual",
            "description": "Data processing terms for ML workloads on AWS.",
            "reference_code": "AWS-DPA",
            "source_document": "AWS Enterprise Agreement",
            "effective_date": "2023-07-01",
            "expiry_date": "2026-06-30",
            "severity": "medium",
            "requirements": {
                "conditions": ["Data residency maintained", "Encryption enabled"],
                "documentation": ["Compliance certificate"],
            },
        },
        {
            "name": "Customer Data Usage Rights",
            "type": "contractual",
            "description": "Contractual limitations on use of customer data for model training.",
            "reference_code": "MSA-DATA",
            "source_document": "Master Services Agreement",
            "effective_date": "2020-01-01",
            "severity": "critical",
            "requirements": {
                "conditions": ["Opt-in consent obtained", "Anonymization applied"],
                "documentation": ["Consent records", "Anonymization procedures"],
            },
        },
        # Operational
        {
            "name": "Model Deployment SLA",
            "type": "operational",
            "description": "Service level requirements for model inference including latency and availability.",
            "reference_code": "SLA-001",
            "source_document": "Platform SLA",
            "effective_date": "2024-01-01",
            "severity": "high",
            "requirements": {
                "conditions": ["P99 latency < 50ms", "Availability > 99.9%"],
                "documentation": ["SLA dashboard"],
            },
        },
        {
            "name": "Incident Response for AI Systems",
            "type": "operational",
            "description": "Incident response procedures for AI system failures or bias incidents.",
            "reference_code": "IR-AI-001",
            "source_document": "IR Policy AI-001",
            "effective_date": "2024-03-01",
            "severity": "critical",
            "requirements": {
                "conditions": [
                    "Detection < 5 min",
                    "Response < 15 min",
                    "Post-mortem required",
                ],
                "documentation": ["Incident reports", "Post-mortem documents"],
            },
        },
        {
            "name": "Model Rollback Capability",
            "type": "operational",
            "description": "Requirement to maintain rollback capability to previous model versions.",
            "reference_code": "CM-002",
            "source_document": "Change Management Policy",
            "effective_date": "2023-01-01",
            "severity": "high",
            "requirements": {
                "conditions": ["Version retention 90 days", "Rollback tested"],
                "documentation": ["Rollback procedures", "Test results"],
            },
        },
        # Security
        {
            "name": "Model Security Standards",
            "type": "security",
            "description": "Security requirements for ML model artifacts and inference endpoints.",
            "reference_code": "SEC-ML-001",
            "source_document": "Security Policy",
            "effective_date": "2024-01-01",
            "severity": "critical",
            "requirements": {
                "conditions": [
                    "Model encryption at rest",
                    "Secure inference endpoints",
                    "Access controls",
                ],
                "documentation": ["Security assessment"],
            },
        },
        {
            "name": "Training Data Security",
            "type": "security",
            "description": "Security controls for protecting training data including PII.",
            "reference_code": "SEC-DATA-001",
            "source_document": "Data Security Policy",
            "effective_date": "2023-06-01",
            "severity": "critical",
            "requirements": {
                "conditions": [
                    "Encryption required",
                    "Access logging",
                    "Data masking for PII",
                ],
                "documentation": ["Security controls documentation"],
            },
        },
    ]

    constraint_ids = {}
    for constraint in constraints:
        r = api_call("POST", "/constraints", token, constraint)
        if r and r.status_code in [200, 201]:
            constraint_ids[constraint["name"]] = r.json()["id"]
            print(f"  Created: {constraint['name']}")
        else:
            err = r.text[:100] if r else "No response"
            print(f"  Failed: {constraint['name']} - {err}")

    # === DEPENDENCIES ===
    print("\nCreating dependencies...")
    # Valid relationship_type: depends_on, procures_from, provides_service, uses_infrastructure, etc.
    # Valid layer: legal, financial, operational, academic, human
    # Valid criticality: 1-5 (integer)
    dependencies = [
        # Model -> Data dependencies (operational layer, depends_on)
        {
            "source_entity_id": entity_ids.get("Credit Scoring Model v3.2"),
            "target_entity_id": entity_ids.get("Customer Data Platform"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 5,
            "description": "Credit model requires customer financial data",
        },
        {
            "source_entity_id": entity_ids.get("Credit Scoring Model v3.2"),
            "target_entity_id": entity_ids.get("Feature Store"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 5,
            "description": "Model consumes 47 features from feature store",
        },
        {
            "source_entity_id": entity_ids.get("Fraud Detection System"),
            "target_entity_id": entity_ids.get("Customer Data Platform"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 5,
            "description": "Real-time transaction data for fraud detection",
        },
        {
            "source_entity_id": entity_ids.get("Fraud Detection System"),
            "target_entity_id": entity_ids.get("Real-time Event Stream"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 5,
            "description": "Streaming events for real-time scoring",
        },
        {
            "source_entity_id": entity_ids.get("Customer Churn Predictor"),
            "target_entity_id": entity_ids.get("Customer Data Platform"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 4,
            "description": "Customer behavioral data for churn prediction",
        },
        {
            "source_entity_id": entity_ids.get("Resume Screening AI"),
            "target_entity_id": entity_ids.get("Training Data Lake"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 4,
            "description": "Historical resume and hiring decision data",
        },
        {
            "source_entity_id": entity_ids.get("Loan Default Predictor"),
            "target_entity_id": entity_ids.get("Feature Store"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 5,
            "description": "Loan performance features",
        },
        {
            "source_entity_id": entity_ids.get("Sentiment Analysis API"),
            "target_entity_id": entity_ids.get("Training Data Lake"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 3,
            "description": "Labeled sentiment training data",
        },
        {
            "source_entity_id": entity_ids.get("Dynamic Pricing Engine"),
            "target_entity_id": entity_ids.get("Real-time Event Stream"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 4,
            "description": "Demand signals for pricing",
        },
        # Model -> Infrastructure dependencies (uses_infrastructure)
        {
            "source_entity_id": entity_ids.get("Credit Scoring Model v3.2"),
            "target_entity_id": entity_ids.get("Model Serving Platform"),
            "relationship_type": "uses_infrastructure",
            "layer": "operational",
            "criticality": 5,
            "description": "Production inference endpoint",
        },
        {
            "source_entity_id": entity_ids.get("Fraud Detection System"),
            "target_entity_id": entity_ids.get("Model Serving Platform"),
            "relationship_type": "uses_infrastructure",
            "layer": "operational",
            "criticality": 5,
            "description": "Low-latency serving requirement",
        },
        {
            "source_entity_id": entity_ids.get("Dynamic Pricing Engine"),
            "target_entity_id": entity_ids.get("Model Serving Platform"),
            "relationship_type": "uses_infrastructure",
            "layer": "operational",
            "criticality": 4,
            "description": "Real-time pricing inference",
        },
        {
            "source_entity_id": entity_ids.get("Credit Scoring Model v3.2"),
            "target_entity_id": entity_ids.get("GPU Training Cluster"),
            "relationship_type": "uses_infrastructure",
            "layer": "operational",
            "criticality": 3,
            "description": "Model retraining compute",
        },
        {
            "source_entity_id": entity_ids.get("Document Classification System"),
            "target_entity_id": entity_ids.get("GPU Training Cluster"),
            "relationship_type": "uses_infrastructure",
            "layer": "operational",
            "criticality": 3,
            "description": "Transformer fine-tuning",
        },
        {
            "source_entity_id": entity_ids.get("Image Recognition Model"),
            "target_entity_id": entity_ids.get("GPU Training Cluster"),
            "relationship_type": "uses_infrastructure",
            "layer": "operational",
            "criticality": 4,
            "description": "Vision model training",
        },
        # Model -> Process dependencies (regulated_by for compliance)
        {
            "source_entity_id": entity_ids.get("Credit Scoring Model v3.2"),
            "target_entity_id": entity_ids.get("Model Validation Process"),
            "relationship_type": "regulated_by",
            "layer": "legal",
            "criticality": 5,
            "description": "Regulatory validation before deployment",
        },
        {
            "source_entity_id": entity_ids.get("Loan Default Predictor"),
            "target_entity_id": entity_ids.get("Model Validation Process"),
            "relationship_type": "regulated_by",
            "layer": "legal",
            "criticality": 5,
            "description": "SR 11-7 compliant validation",
        },
        {
            "source_entity_id": entity_ids.get("Resume Screening AI"),
            "target_entity_id": entity_ids.get("Bias Monitoring Process"),
            "relationship_type": "regulated_by",
            "layer": "legal",
            "criticality": 5,
            "description": "NYC Law 144 bias audit requirement",
        },
        {
            "source_entity_id": entity_ids.get("Credit Scoring Model v3.2"),
            "target_entity_id": entity_ids.get("Bias Monitoring Process"),
            "relationship_type": "regulated_by",
            "layer": "legal",
            "criticality": 5,
            "description": "Fair lending bias monitoring",
        },
        {
            "source_entity_id": entity_ids.get("Fraud Detection System"),
            "target_entity_id": entity_ids.get("Model Retraining Pipeline"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 4,
            "description": "Weekly retraining for fraud patterns",
        },
        {
            "source_entity_id": entity_ids.get("Customer Data Platform"),
            "target_entity_id": entity_ids.get("Data Quality Pipeline"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 4,
            "description": "Data quality assurance",
        },
        {
            "source_entity_id": entity_ids.get("Model Serving Platform"),
            "target_entity_id": entity_ids.get("Incident Response Process"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 5,
            "description": "Incident handling for model failures",
        },
        # Team dependencies (human layer, employs/employed_by or depends_on)
        {
            "source_entity_id": entity_ids.get("Credit Scoring Model v3.2"),
            "target_entity_id": entity_ids.get("ML Engineering Team"),
            "relationship_type": "depends_on",
            "layer": "human",
            "criticality": 4,
            "description": "Model development and maintenance",
        },
        {
            "source_entity_id": entity_ids.get("Credit Scoring Model v3.2"),
            "target_entity_id": entity_ids.get("Model Risk Management"),
            "relationship_type": "regulated_by",
            "layer": "human",
            "criticality": 5,
            "description": "Independent validation and sign-off",
        },
        {
            "source_entity_id": entity_ids.get("Resume Screening AI"),
            "target_entity_id": entity_ids.get("AI Ethics Committee"),
            "relationship_type": "regulated_by",
            "layer": "human",
            "criticality": 5,
            "description": "Ethics review for hiring decisions",
        },
        {
            "source_entity_id": entity_ids.get("Dynamic Pricing Engine"),
            "target_entity_id": entity_ids.get("AI Ethics Committee"),
            "relationship_type": "regulated_by",
            "layer": "human",
            "criticality": 4,
            "description": "Fairness review for pricing",
        },
        {
            "source_entity_id": entity_ids.get("Fraud Detection System"),
            "target_entity_id": entity_ids.get("Data Science Team"),
            "relationship_type": "depends_on",
            "layer": "human",
            "criticality": 4,
            "description": "Pattern research",
        },
        {
            "source_entity_id": entity_ids.get("Feature Store"),
            "target_entity_id": entity_ids.get("Data Engineering Team"),
            "relationship_type": "depends_on",
            "layer": "human",
            "criticality": 4,
            "description": "Feature pipeline maintenance",
        },
        # Vendor dependencies (procures_from, financial layer)
        {
            "source_entity_id": entity_ids.get("Document Classification System"),
            "target_entity_id": entity_ids.get("Hugging Face Enterprise"),
            "relationship_type": "procures_from",
            "layer": "financial",
            "criticality": 3,
            "description": "Pre-trained model weights",
        },
        {
            "source_entity_id": entity_ids.get("Sentiment Analysis API"),
            "target_entity_id": entity_ids.get("OpenAI API Integration"),
            "relationship_type": "procures_from",
            "layer": "financial",
            "criticality": 3,
            "description": "Fallback for complex analysis",
        },
        {
            "source_entity_id": entity_ids.get("GPU Training Cluster"),
            "target_entity_id": entity_ids.get("AWS SageMaker"),
            "relationship_type": "procures_from",
            "layer": "financial",
            "criticality": 3,
            "description": "Overflow training capacity",
        },
        {
            "source_entity_id": entity_ids.get("Model Serving Platform"),
            "target_entity_id": entity_ids.get("AWS SageMaker"),
            "relationship_type": "procures_from",
            "layer": "financial",
            "criticality": 4,
            "description": "Managed inference endpoints",
        },
        {
            "source_entity_id": entity_ids.get("Training Data Lake"),
            "target_entity_id": entity_ids.get("Databricks"),
            "relationship_type": "procures_from",
            "layer": "financial",
            "criticality": 4,
            "description": "Data processing platform",
        },
        # Data -> Data dependencies
        {
            "source_entity_id": entity_ids.get("Feature Store"),
            "target_entity_id": entity_ids.get("Customer Data Platform"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 5,
            "description": "Raw data for feature engineering",
        },
        {
            "source_entity_id": entity_ids.get("Training Data Lake"),
            "target_entity_id": entity_ids.get("Customer Data Platform"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 4,
            "description": "Historical data for training",
        },
        {
            "source_entity_id": entity_ids.get("Model Registry"),
            "target_entity_id": entity_ids.get("ML Experiment Platform"),
            "relationship_type": "connected_to",
            "layer": "operational",
            "criticality": 3,
            "description": "Experiment tracking integration",
        },
        {
            "source_entity_id": entity_ids.get("Data Warehouse"),
            "target_entity_id": entity_ids.get("Customer Data Platform"),
            "relationship_type": "depends_on",
            "layer": "operational",
            "criticality": 4,
            "description": "Analytics data source",
        },
    ]

    dep_count = 0
    for dep in dependencies:
        if dep.get("source_entity_id") and dep.get("target_entity_id"):
            r = api_call("POST", "/dependencies", token, dep)
            if r and r.status_code in [200, 201]:
                dep_count += 1
            else:
                err = r.text[:80] if r else "No response"
                print(f"  Failed: {err}")
    print(f"  Created {dep_count} dependencies")

    # === SCENARIOS ===
    print("\nCreating scenarios...")
    # Valid scenario types: entity_restriction, country_embargo, supplier_loss, dependency_failure, custom
    scenarios = [
        {
            "name": "EU AI Act Compliance Assessment",
            "description": "Comprehensive assessment of AI system readiness for EU AI Act high-risk requirements.",
            "type": "custom",
            "parameters": {
                "regulation": "EU AI Act",
                "systems_in_scope": 8,
                "scenario_subtype": "compliance_assessment",
            },
        },
        {
            "name": "Credit Model Bias Audit Q4 2024",
            "description": "Quarterly bias audit for credit scoring model covering demographic parity and equalized odds.",
            "type": "custom",
            "parameters": {
                "model": "Credit Scoring Model v3.2",
                "protected_groups": ["race", "gender", "age"],
                "scenario_subtype": "bias_audit",
            },
        },
        {
            "name": "NYC Law 144 Annual Audit",
            "description": "Annual bias audit for Resume Screening AI as required by NYC Local Law 144.",
            "type": "custom",
            "parameters": {
                "regulation": "NYC Local Law 144",
                "model": "Resume Screening AI",
                "scenario_subtype": "bias_audit",
            },
        },
        {
            "name": "Model Risk Inventory Review",
            "description": "Annual review of model risk inventory including risk tiering and validation status.",
            "type": "custom",
            "parameters": {
                "review_period": "2024",
                "models_in_scope": 10,
                "scenario_subtype": "risk_assessment",
            },
        },
        {
            "name": "Training Data Privacy Assessment",
            "description": "Assessment of training data compliance with GDPR and CCPA.",
            "type": "custom",
            "parameters": {
                "datasets": 156,
                "regulations": ["GDPR", "CCPA"],
                "scenario_subtype": "compliance_assessment",
            },
        },
        {
            "name": "Vendor AI Risk Assessment",
            "description": "Third-party AI vendor risk assessment covering OpenAI, AWS, and Anthropic.",
            "type": "supplier_loss",
            "parameters": {
                "vendors": 4,
                "criteria": ["security", "privacy", "reliability"],
                "scenario_subtype": "vendor_review",
            },
        },
        {
            "name": "Model Failure Impact Analysis",
            "description": "What-if scenario analyzing impact of critical ML model failures.",
            "type": "dependency_failure",
            "parameters": {
                "failure_scenario": "multi_model",
                "duration_hours": 4,
                "scenario_subtype": "what_if",
            },
        },
        {
            "name": "Data Breach Response Scenario",
            "description": "Tabletop exercise for data breach affecting training data lake.",
            "type": "custom",
            "parameters": {
                "breach_type": "training_data",
                "records_affected": 500000,
                "scenario_subtype": "security_incident",
            },
        },
        {
            "name": "Regulatory Examination Prep",
            "description": "Preparation scenario for potential regulatory examination of AI/ML practices.",
            "type": "custom",
            "parameters": {
                "regulator": "OCC",
                "focus_areas": ["model_risk", "fair_lending"],
            },
        },
        {
            "name": "Model Drift Stress Test",
            "description": "Stress test simulating significant data drift across production systems.",
            "type": "custom",
            "parameters": {
                "drift_magnitude": "severe",
                "affected_models": 5,
                "scenario_subtype": "stress_test",
            },
        },
        {
            "name": "Credit Model Validation 2024",
            "description": "Annual independent validation of Credit Scoring Model.",
            "type": "custom",
            "parameters": {
                "model": "Credit Scoring Model v3.2",
                "validation_type": "comprehensive",
                "scenario_subtype": "model_validation",
            },
        },
        {
            "name": "Feature Store Data Quality Check",
            "description": "Comprehensive data quality assessment of feature store.",
            "type": "custom",
            "parameters": {
                "features": 523,
                "quality_metrics": ["completeness", "accuracy", "timeliness"],
                "scenario_subtype": "data_quality",
            },
        },
    ]

    for scenario in scenarios:
        r = api_call("POST", "/scenarios", token, scenario)
        if r and r.status_code in [200, 201]:
            print(f"  Created: {scenario['name']}")
        else:
            err = r.text[:100] if r else "No response"
            print(f"  Failed: {scenario['name']} - {err}")

    print("\n" + "=" * 50)
    print("DATA POPULATION COMPLETE")
    print("=" * 50)
    print(f"Entities: {len(entity_ids)}")
    print(f"Constraints: {len(constraint_ids)}")
    print(f"Dependencies: {dep_count}")
    print(f"Scenarios: {len(scenarios)}")


if __name__ == "__main__":
    main()
