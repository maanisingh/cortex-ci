#!/usr/bin/env python3
"""
Russia Beneficial Ownership Screening for CORTEX-CI.
Rules for identifying hidden Russian ownership and control.

Covers:
- Ultimate beneficial owner (UBO) identification
- Complex corporate structure analysis
- Nominee and straw-man detection
- Trust and foundation scrutiny
- PEP relationship mapping

Run: python3 sample_russia_beneficial_ownership.py
"""

import json
import subprocess
import uuid
from datetime import datetime

DB_CONTAINER = "compose-input-solid-state-array-q9m3z5-db-1"
DB_USER = "cortex"
DB_NAME = "cortex_ci"


def run_sql(sql: str) -> str:
    """Execute SQL in database container."""
    cmd = [
        "docker",
        "exec",
        "-i",
        DB_CONTAINER,
        "psql",
        "-U",
        DB_USER,
        "-d",
        DB_NAME,
        "-c",
        sql,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def escape_sql(s: str) -> str:
    """Escape string for SQL."""
    if s is None:
        return ""
    return s.replace("'", "''").replace("\\", "\\\\")


def get_tenant_id() -> str:
    """Get default tenant ID."""
    result = run_sql("SELECT id FROM tenants WHERE slug = 'default';")
    for line in result.split("\n"):
        line = line.strip()
        if line and "-" in line and len(line) == 36:
            return line
    return None


# ============================================================================
# BENEFICIAL OWNERSHIP SCREENING RULES
# ============================================================================
BENEFICIAL_OWNERSHIP_CONSTRAINTS = [
    # Core UBO Requirements
    {
        "name": "Russia UBO Identification Requirement",
        "type": "kyc",
        "severity": "critical",
        "description": "Mandatory identification of ultimate beneficial owners for entities with Russian nexus",
        "source_document": "FinCEN CDD Rule",
        "external_url": "https://www.fincen.gov/resources/statutes-and-regulations/cdd-final-rule",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["KYC", "UBO", "RUSSIA", "MANDATORY", "CRITICAL"],
    },
    {
        "name": "25% Ownership Threshold - Russia Enhanced",
        "type": "kyc",
        "severity": "high",
        "description": "Enhanced screening for Russian nationals with 25%+ ownership in any entity",
        "source_document": "FinCEN CDD Rule",
        "external_url": "https://www.fincen.gov/resources/statutes-and-regulations/cdd-final-rule",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["KYC", "UBO", "THRESHOLD", "OWNERSHIP"],
    },
    {
        "name": "10% Ownership Threshold - Sanctioned Russian PEPs",
        "type": "kyc",
        "severity": "critical",
        "description": "Lower threshold for sanctioned Russian PEPs - any 10%+ ownership triggers review",
        "source_document": "OFAC Guidance",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/faqs",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["KYC", "UBO", "PEP", "LOWERED_THRESHOLD", "CRITICAL"],
    },
    # Corporate Structure Analysis
    {
        "name": "Multi-Layer Corporate Structure - Russia Risk",
        "type": "compliance",
        "severity": "high",
        "description": "Enhanced due diligence for entities with 3+ layers of corporate ownership involving Russian entities",
        "source_document": "FATF Guidance",
        "external_url": "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Transparency-beneficial-ownership.html",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["KYC", "CORPORATE_STRUCTURE", "LAYERING", "RED_FLAG"],
    },
    {
        "name": "Nominee Director/Shareholder Detection - Russia",
        "type": "kyc",
        "severity": "critical",
        "description": "Screening for nominee arrangements potentially concealing Russian beneficial owners",
        "source_document": "FATF Best Practices",
        "external_url": "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Bpp-bo-legal-persons.html",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["KYC", "NOMINEE", "CONCEALMENT", "CRITICAL"],
    },
    {
        "name": "Bearer Share Prohibition Verification",
        "type": "kyc",
        "severity": "high",
        "description": "Verification that entity does not use bearer shares to conceal Russian ownership",
        "source_document": "FATF R24",
        "external_url": "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Fatf-recommendations.html",
        "applies_to_countries": [],
        "risk_weight": 4.0,
        "tags": ["KYC", "BEARER_SHARES", "OWNERSHIP"],
    },
    # Trust and Foundation Screening
    {
        "name": "Trust Beneficiary Screening - Russia Nexus",
        "type": "kyc",
        "severity": "critical",
        "description": "Identification of all trust beneficiaries with potential Russian connections",
        "source_document": "FATF R25",
        "external_url": "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Fatf-recommendations.html",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["KYC", "TRUST", "BENEFICIARY", "RUSSIA", "CRITICAL"],
    },
    {
        "name": "Private Foundation Scrutiny - Russian Settlors",
        "type": "kyc",
        "severity": "critical",
        "description": "Enhanced scrutiny of private foundations with Russian settlors or beneficiaries",
        "source_document": "OFAC FAQ 1063",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/faqs",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["KYC", "FOUNDATION", "RUSSIA", "CRITICAL"],
    },
    # Family Member Screening
    {
        "name": "Close Family Member Screening - Sanctioned Russians",
        "type": "kyc",
        "severity": "critical",
        "description": "Screening for close family members of sanctioned Russian individuals",
        "source_document": "OFAC Guidance",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/faqs",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["KYC", "FAMILY", "SANCTIONS", "CRITICAL"],
    },
    {
        "name": "Spouse and Adult Children Screening",
        "type": "kyc",
        "severity": "high",
        "description": "Specific screening for spouses and adult children of Russian oligarchs",
        "source_document": "FinCEN Advisory",
        "external_url": "https://www.fincen.gov/resources/advisories",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["KYC", "FAMILY", "OLIGARCH"],
    },
    # Jurisdiction Red Flags
    {
        "name": "High-Risk Jurisdiction Ownership - Russia Gateway",
        "type": "compliance",
        "severity": "high",
        "description": "Enhanced review for ownership through jurisdictions used to obscure Russian connections",
        "source_document": "FATF Grey List",
        "external_url": "https://www.fatf-gafi.org/en/countries/grey-list.html",
        "applies_to_countries": ["CY", "MT", "BVI", "JE", "GG", "IM"],
        "risk_weight": 4.5,
        "tags": ["KYC", "JURISDICTION", "GATEWAY", "RED_FLAG"],
    },
    {
        "name": "Cyprus Structure Scrutiny - Russian Connections",
        "type": "compliance",
        "severity": "high",
        "description": "Cyprus historically used by Russian entities - enhanced ownership verification",
        "source_document": "EU AML Directive",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32018L0843",
        "applies_to_countries": ["CY"],
        "risk_weight": 4.5,
        "tags": ["KYC", "CYPRUS", "RUSSIA", "RED_FLAG"],
    },
    # Control Without Ownership
    {
        "name": "Control Through Contract Detection - Russia",
        "type": "compliance",
        "severity": "high",
        "description": "Identification of control through contractual arrangements bypassing ownership thresholds",
        "source_document": "FATF Best Practices",
        "external_url": "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Bpp-bo-legal-persons.html",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["KYC", "CONTROL", "CONTRACT", "CIRCUMVENTION"],
    },
    {
        "name": "Voting Rights Disparities - Russian Entities",
        "type": "compliance",
        "severity": "high",
        "description": "Analysis of voting rights vs ownership to detect hidden Russian control",
        "source_document": "Corporate Governance Guidelines",
        "external_url": "https://www.oecd.org/corporate/principles-corporate-governance/",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.0,
        "tags": ["KYC", "VOTING_RIGHTS", "CONTROL"],
    },
    # Real Estate Specific
    {
        "name": "Real Estate Beneficial Ownership - Russia",
        "type": "aml",
        "severity": "critical",
        "description": "Enhanced verification of beneficial ownership for real estate purchases by Russian-linked entities",
        "source_document": "FinCEN Geographic Targeting Orders",
        "external_url": "https://www.fincen.gov/news/news-releases/fincen-renews-and-expands-real-estate-geographic-targeting-orders",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["AML", "REAL_ESTATE", "GTO", "RUSSIA", "CRITICAL"],
    },
    {
        "name": "All-Cash Purchase Red Flag - Russian Buyers",
        "type": "aml",
        "severity": "critical",
        "description": "Enhanced scrutiny for all-cash real estate purchases with Russian beneficial owners",
        "source_document": "FinCEN GTO",
        "external_url": "https://www.fincen.gov/news/news-releases/fincen-renews-and-expands-real-estate-geographic-targeting-orders",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["AML", "ALL_CASH", "REAL_ESTATE", "RED_FLAG", "CRITICAL"],
    },
    # Yacht and Aircraft
    {
        "name": "Yacht Beneficial Ownership Verification - Russia",
        "type": "compliance",
        "severity": "critical",
        "description": "Verification of beneficial ownership for yachts potentially linked to Russian oligarchs",
        "source_document": "OFAC Sanctions Advisory",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/recent-actions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["LUXURY", "YACHT", "OLIGARCH", "RUSSIA", "CRITICAL"],
    },
    {
        "name": "Private Aircraft Ownership Tracing - Russia",
        "type": "compliance",
        "severity": "critical",
        "description": "Tracing beneficial ownership of private aircraft to identify Russian oligarch assets",
        "source_document": "OFAC Sanctions Advisory",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/recent-actions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["LUXURY", "AIRCRAFT", "OLIGARCH", "RUSSIA", "CRITICAL"],
    },
    # Corporate Service Provider Scrutiny
    {
        "name": "CSP Due Diligence - Russia Related Clients",
        "type": "compliance",
        "severity": "high",
        "description": "Enhanced due diligence on corporate service providers handling Russian-linked entities",
        "source_document": "FATF R22",
        "external_url": "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Fatf-recommendations.html",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["COMPLIANCE", "CSP", "DUE_DILIGENCE"],
    },
    {
        "name": "Formation Agent Verification - Russian Clients",
        "type": "compliance",
        "severity": "high",
        "description": "Verification of formation agent practices for entities with Russian ownership",
        "source_document": "FATF Guidance",
        "external_url": "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Guidance-tcsp.html",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["COMPLIANCE", "FORMATION_AGENT", "VERIFICATION"],
    },
]

# ============================================================================
# RED FLAG INDICATORS
# ============================================================================
RED_FLAG_CONSTRAINTS = [
    {
        "name": "Rapid Corporate Restructuring - Russia Nexus",
        "type": "compliance",
        "severity": "critical",
        "description": "Red flag: Rapid changes in ownership structure following sanctions announcements",
        "source_document": "FinCEN Advisory FIN-2022-A001",
        "external_url": "https://www.fincen.gov/resources/advisories",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["RED_FLAG", "RESTRUCTURING", "EVASION", "CRITICAL"],
    },
    {
        "name": "Power of Attorney Abuse Detection",
        "type": "compliance",
        "severity": "high",
        "description": "Detection of power of attorney arrangements potentially concealing Russian principals",
        "source_document": "FATF Typologies",
        "external_url": "https://www.fatf-gafi.org/en/publications/Methodsandtrends/Ml-tf-typologies.html",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["RED_FLAG", "POA", "CONCEALMENT"],
    },
    {
        "name": "Inconsistent Documentation - Russian Entities",
        "type": "compliance",
        "severity": "high",
        "description": "Red flag: Inconsistencies between stated and actual beneficial ownership",
        "source_document": "FATF Guidance",
        "external_url": "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Transparency-beneficial-ownership.html",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["RED_FLAG", "DOCUMENTATION", "INCONSISTENCY"],
    },
    {
        "name": "Unusual Transaction Patterns Post-Sanctions",
        "type": "aml",
        "severity": "critical",
        "description": "Red flag: Changed transaction patterns after Russian-related sanctions",
        "source_document": "FinCEN Advisory",
        "external_url": "https://www.fincen.gov/resources/advisories",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["RED_FLAG", "TRANSACTION", "SANCTIONS", "CRITICAL"],
    },
]


def load_constraints(tenant_id: str, constraints: list, category: str) -> int:
    """Load constraints into database."""
    print(f"\n{'='*60}")
    print(f"Loading {len(constraints)} {category}...")
    print(f"{'='*60}")

    count = 0
    for constraint in constraints:
        constraint_id = str(uuid.uuid4())

        countries = constraint.get("applies_to_countries", [])
        countries_array = (
            "ARRAY[" + ",".join([f"'{c}'" for c in countries]) + "]::varchar[]"
            if countries
            else "ARRAY[]::varchar[]"
        )

        tags = constraint.get("tags", ["COMPLIANCE"])
        tags_array = "ARRAY[" + ",".join([f"'{t}'" for t in tags]) + "]::varchar[]"

        sql = f"""
        INSERT INTO constraints (
            id, tenant_id, name, description, type, severity,
            source_document, external_url, applies_to_countries,
            risk_weight, is_active, is_mandatory, tags, custom_data,
            created_at, updated_at
        ) VALUES (
            '{constraint_id}',
            '{tenant_id}',
            '{escape_sql(constraint["name"])}',
            '{escape_sql(constraint.get("description", ""))}',
            '{constraint["type"]}',
            '{constraint["severity"]}',
            '{escape_sql(constraint.get("source_document", ""))}',
            '{escape_sql(constraint.get("external_url", ""))}',
            {countries_array},
            {constraint.get("risk_weight", 1.0)},
            true,
            true,
            {tags_array},
            '{{}}'::jsonb,
            NOW(),
            NOW()
        )
        ON CONFLICT DO NOTHING;
        """

        run_sql(sql)
        sev = constraint.get("severity", "medium")
        print(f"  [OK] [{sev.upper()[:4]:>4}] {constraint['name'][:50]}")
        count += 1

    return count


def main():
    print("=" * 70)
    print("CORTEX-CI Russia Beneficial Ownership Screening")
    print("UBO Identification & Hidden Control Detection")
    print("=" * 70)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")

    total = 0
    total += load_constraints(tenant_id, BENEFICIAL_OWNERSHIP_CONSTRAINTS, "Beneficial Ownership Rules")
    total += load_constraints(tenant_id, RED_FLAG_CONSTRAINTS, "Red Flag Indicators")

    # Get final count
    result = run_sql(f"SELECT COUNT(*) FROM constraints WHERE tenant_id = '{tenant_id}';")
    for line in result.split("\n"):
        if line.strip().isdigit():
            print(f"\n{'='*70}")
            print(f"Constraints loaded this session: {total}")
            print(f"Total constraints in database: {line.strip()}")
            print(f"{'='*70}")
            break


if __name__ == "__main__":
    main()
