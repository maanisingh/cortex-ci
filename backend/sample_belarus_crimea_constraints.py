#!/usr/bin/env python3
"""
Belarus & Crimea Constraints for CORTEX-CI.
Related jurisdictions for comprehensive Russia compliance.

Run: python3 sample_belarus_crimea_constraints.py
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
# BELARUS SANCTIONS CONSTRAINTS
# ============================================================================
BELARUS_CONSTRAINTS = [
    {
        "name": "OFAC Belarus Sanctions (EO 14038)",
        "type": "sanctions",
        "severity": "critical",
        "description": "Executive Order 14038 imposing comprehensive sanctions on Belarus regime",
        "source_document": "Executive Order 14038",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/belarus-sanctions",
        "applies_to_countries": ["BY"],
        "risk_weight": 5.0,
        "tags": ["SANCTIONS", "BELARUS", "OFAC", "CRITICAL"],
    },
    {
        "name": "EU Belarus Sanctions Package",
        "type": "sanctions",
        "severity": "critical",
        "description": "EU restrictive measures against Belarus following forced landing of Ryanair flight and support for Russia",
        "source_document": "Council Regulation (EU) 2021/1030",
        "external_url": "https://www.consilium.europa.eu/en/policies/sanctions/restrictive-measures-against-belarus/",
        "applies_to_countries": ["BY"],
        "risk_weight": 5.0,
        "tags": ["SANCTIONS", "BELARUS", "EU", "CRITICAL"],
    },
    {
        "name": "UK Belarus Sanctions Regime",
        "type": "sanctions",
        "severity": "critical",
        "description": "UK sanctions on Belarus for human rights violations and support for Russian aggression",
        "source_document": "Belarus (Sanctions) (EU Exit) Regulations 2019",
        "external_url": "https://www.gov.uk/government/publications/the-uk-sanctions-list",
        "applies_to_countries": ["BY"],
        "risk_weight": 4.5,
        "tags": ["SANCTIONS", "BELARUS", "UK"],
    },
    {
        "name": "Belarus Potash Export Ban",
        "type": "trade_restriction",
        "severity": "high",
        "description": "Prohibition on import of potash and related products from Belarus",
        "source_document": "EU Regulation 2021/1030",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32021R1030",
        "applies_to_countries": ["BY"],
        "risk_weight": 4.0,
        "tags": ["TRADE", "BELARUS", "POTASH", "IMPORT_BAN"],
    },
    {
        "name": "Belarus Petroleum Export Ban",
        "type": "trade_restriction",
        "severity": "high",
        "description": "Prohibition on import of petroleum products from Belarus",
        "source_document": "EU Regulation 2022/577",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0577",
        "applies_to_countries": ["BY"],
        "risk_weight": 4.0,
        "tags": ["TRADE", "BELARUS", "PETROLEUM", "IMPORT_BAN"],
    },
    {
        "name": "Belarus Tobacco Import Ban",
        "type": "trade_restriction",
        "severity": "medium",
        "description": "Prohibition on import of tobacco products from Belarus",
        "source_document": "EU Regulation 2021/1030",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32021R1030",
        "applies_to_countries": ["BY"],
        "risk_weight": 3.0,
        "tags": ["TRADE", "BELARUS", "TOBACCO"],
    },
    {
        "name": "Belarus Dual-Use Technology Export Ban",
        "type": "export_control",
        "severity": "critical",
        "description": "Export controls on dual-use goods and technology to Belarus",
        "source_document": "BIS Final Rule - Belarus",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/russia-belarus",
        "applies_to_countries": ["BY"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "BELARUS", "DUAL_USE", "CRITICAL"],
    },
    {
        "name": "Belarus Aviation Parts Export Ban",
        "type": "export_control",
        "severity": "high",
        "description": "Prohibition on export of aircraft and parts to Belarus",
        "source_document": "EU Regulation 2022/328",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0328",
        "applies_to_countries": ["BY"],
        "risk_weight": 4.5,
        "tags": ["EXPORT_CONTROL", "BELARUS", "AVIATION"],
    },
    {
        "name": "Belarus Luxury Goods Export Ban",
        "type": "trade_restriction",
        "severity": "medium",
        "description": "Prohibition on export of luxury goods to Belarus",
        "source_document": "EU Regulation 2022/328",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0328",
        "applies_to_countries": ["BY"],
        "risk_weight": 2.5,
        "tags": ["TRADE", "BELARUS", "LUXURY_GOODS"],
    },
    {
        "name": "Belarus Financial Sector Restrictions",
        "type": "financial",
        "severity": "critical",
        "description": "Restrictions on financial transactions with Belarus banks and entities",
        "source_document": "EU Council Decision 2012/642/CFSP",
        "external_url": "https://www.consilium.europa.eu/en/policies/sanctions/restrictive-measures-against-belarus/",
        "applies_to_countries": ["BY"],
        "risk_weight": 5.0,
        "tags": ["FINANCIAL", "BELARUS", "BANKING", "CRITICAL"],
    },
    {
        "name": "Belarus SWIFT Restrictions",
        "type": "financial",
        "severity": "critical",
        "description": "Belarusian banks disconnected from SWIFT messaging system",
        "source_document": "EU Council Decision",
        "external_url": "https://www.consilium.europa.eu/en/policies/sanctions/restrictive-measures-against-belarus/",
        "applies_to_countries": ["BY"],
        "risk_weight": 5.0,
        "tags": ["FINANCIAL", "BELARUS", "SWIFT", "CRITICAL"],
    },
]

# ============================================================================
# CRIMEA/SEVASTOPOL SANCTIONS
# ============================================================================
CRIMEA_CONSTRAINTS = [
    {
        "name": "OFAC Crimea Region Sanctions (EO 13685)",
        "type": "sanctions",
        "severity": "critical",
        "description": "Comprehensive embargo on Crimea region including prohibition on transactions",
        "source_document": "Executive Order 13685",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/ukraine-russia-related-sanctions",
        "applies_to_countries": ["UA-43"],  # Crimea ISO code
        "risk_weight": 5.0,
        "tags": ["SANCTIONS", "CRIMEA", "OFAC", "EMBARGO", "CRITICAL"],
    },
    {
        "name": "EU Crimea Territorial Sanctions",
        "type": "sanctions",
        "severity": "critical",
        "description": "EU non-recognition policy prohibiting imports from Crimea and Sevastopol",
        "source_document": "Council Regulation (EU) 2023/1214",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R1214",
        "applies_to_countries": ["UA-43"],
        "risk_weight": 5.0,
        "tags": ["SANCTIONS", "CRIMEA", "EU", "EMBARGO", "CRITICAL"],
    },
    {
        "name": "Crimea Import Ban",
        "type": "import_regulation",
        "severity": "critical",
        "description": "Complete ban on imports of goods originating in Crimea",
        "source_document": "EU Regulation 692/2014",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R0692",
        "applies_to_countries": ["UA-43"],
        "risk_weight": 5.0,
        "tags": ["TRADE", "CRIMEA", "IMPORT_BAN", "CRITICAL"],
    },
    {
        "name": "Crimea Export Ban",
        "type": "export_control",
        "severity": "critical",
        "description": "Prohibition on export of goods and services to Crimea",
        "source_document": "EU Regulation 692/2014",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R0692",
        "applies_to_countries": ["UA-43"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "CRIMEA", "CRITICAL"],
    },
    {
        "name": "Crimea Tourism & Investment Ban",
        "type": "trade_restriction",
        "severity": "high",
        "description": "Prohibition on tourism services and new investment in Crimea",
        "source_document": "EU Regulation 692/2014",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R0692",
        "applies_to_countries": ["UA-43"],
        "risk_weight": 4.5,
        "tags": ["TRADE", "CRIMEA", "TOURISM", "INVESTMENT_BAN"],
    },
    {
        "name": "Crimea Financial Services Ban",
        "type": "financial",
        "severity": "critical",
        "description": "Prohibition on providing financial services to entities in Crimea",
        "source_document": "EU Regulation 692/2014",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R0692",
        "applies_to_countries": ["UA-43"],
        "risk_weight": 5.0,
        "tags": ["FINANCIAL", "CRIMEA", "SERVICES_BAN", "CRITICAL"],
    },
    {
        "name": "Crimea Infrastructure Investment Ban",
        "type": "trade_restriction",
        "severity": "critical",
        "description": "Prohibition on infrastructure-related services and investment",
        "source_document": "EU Regulation 692/2014",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R0692",
        "applies_to_countries": ["UA-43"],
        "risk_weight": 5.0,
        "tags": ["TRADE", "CRIMEA", "INFRASTRUCTURE", "CRITICAL"],
    },
    {
        "name": "Crimea Energy Sector Ban",
        "type": "trade_restriction",
        "severity": "critical",
        "description": "Prohibition on energy sector equipment and services to Crimea",
        "source_document": "EU Regulation 692/2014",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R0692",
        "applies_to_countries": ["UA-43"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "CRIMEA", "EXPORT_BAN", "CRITICAL"],
    },
]

# ============================================================================
# DONETSK/LUHANSK (OCCUPIED TERRITORIES)
# ============================================================================
DNR_LNR_CONSTRAINTS = [
    {
        "name": "OFAC Donetsk/Luhansk Sanctions (EO 14065)",
        "type": "sanctions",
        "severity": "critical",
        "description": "Comprehensive sanctions on so-called DNR and LNR territories",
        "source_document": "Executive Order 14065",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/ukraine-russia-related-sanctions",
        "applies_to_countries": ["UA-14", "UA-09"],  # Donetsk, Luhansk oblasts
        "risk_weight": 5.0,
        "tags": ["SANCTIONS", "DNR_LNR", "OFAC", "CRITICAL"],
    },
    {
        "name": "EU Non-Recognition of Occupied Territories",
        "type": "sanctions",
        "severity": "critical",
        "description": "EU non-recognition policy for territories occupied by Russia in Ukraine",
        "source_document": "Council Decision (CFSP) 2022/266",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022D0266",
        "applies_to_countries": ["UA-14", "UA-09"],
        "risk_weight": 5.0,
        "tags": ["SANCTIONS", "DNR_LNR", "EU", "CRITICAL"],
    },
    {
        "name": "Occupied Territories Import Ban",
        "type": "import_regulation",
        "severity": "critical",
        "description": "Ban on imports originating from non-government controlled areas",
        "source_document": "EU Regulation 2022/263",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0263",
        "applies_to_countries": ["UA-14", "UA-09"],
        "risk_weight": 5.0,
        "tags": ["TRADE", "DNR_LNR", "IMPORT_BAN", "CRITICAL"],
    },
    {
        "name": "Occupied Territories Export Ban",
        "type": "export_control",
        "severity": "critical",
        "description": "Prohibition on export of goods and services to occupied territories",
        "source_document": "EU Regulation 2022/263",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0263",
        "applies_to_countries": ["UA-14", "UA-09"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "DNR_LNR", "CRITICAL"],
    },
]

# ============================================================================
# TRANSSHIPMENT & EVASION RULES
# ============================================================================
EVASION_CONSTRAINTS = [
    {
        "name": "Russia Sanctions Evasion - Third Country Transshipment",
        "type": "compliance",
        "severity": "critical",
        "description": "Due diligence requirements for detecting transshipment through third countries to evade Russia sanctions",
        "source_document": "OFAC Compliance Guidance",
        "external_url": "https://home.treasury.gov/system/files/126/ofac_ransomware_advisory.pdf",
        "applies_to_countries": ["KZ", "AM", "GE", "AZ", "KG", "UZ", "TJ", "TM", "TR", "AE", "CN"],
        "risk_weight": 4.5,
        "tags": ["EVASION", "TRANSSHIPMENT", "COMPLIANCE", "CRITICAL"],
    },
    {
        "name": "Shell Company Screening - Russia Related",
        "type": "kyc",
        "severity": "critical",
        "description": "Enhanced screening for shell companies potentially used to evade Russia sanctions",
        "source_document": "FinCEN Advisory FIN-2022-A001",
        "external_url": "https://www.fincen.gov/resources/advisories/fincen-advisory-fin-2022-a001",
        "applies_to_countries": [],
        "risk_weight": 5.0,
        "tags": ["EVASION", "SHELL_COMPANY", "KYC", "CRITICAL"],
    },
    {
        "name": "Cryptocurrency Sanctions Evasion",
        "type": "aml",
        "severity": "critical",
        "description": "Monitoring for use of cryptocurrency to evade Russia sanctions",
        "source_document": "FinCEN Alert",
        "external_url": "https://www.fincen.gov/news/news-releases/fincen-and-us-treasury-issue-alert-potential-russian-sanctions-evasion",
        "applies_to_countries": [],
        "risk_weight": 5.0,
        "tags": ["EVASION", "CRYPTOCURRENCY", "AML", "CRITICAL"],
    },
    {
        "name": "High-Risk Transshipment Jurisdictions",
        "type": "compliance",
        "severity": "high",
        "description": "Enhanced due diligence for transactions through jurisdictions identified as high-risk for Russia sanctions evasion",
        "source_document": "BIS Russia/Belarus Export Control Guidance",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/russia-belarus",
        "applies_to_countries": ["AE", "TR", "CN", "KZ", "AM", "GE", "RS", "IN"],
        "risk_weight": 4.0,
        "tags": ["EVASION", "TRANSSHIPMENT", "DUE_DILIGENCE"],
    },
    {
        "name": "Front Company Red Flags",
        "type": "kyc",
        "severity": "high",
        "description": "Red flags for identifying front companies used to circumvent Russia sanctions",
        "source_document": "OFAC Compliance Guidance",
        "external_url": "https://ofac.treasury.gov/media/923781/download",
        "applies_to_countries": [],
        "risk_weight": 4.5,
        "tags": ["EVASION", "FRONT_COMPANY", "RED_FLAGS", "KYC"],
    },
    {
        "name": "Dual-Use Goods Diversion Monitoring",
        "type": "export_control",
        "severity": "critical",
        "description": "Enhanced end-use/end-user screening for potential diversion of dual-use goods to Russia",
        "source_document": "BIS Know Your Customer Guidance",
        "external_url": "https://www.bis.doc.gov/index.php/compliance-a-training/export-management-a-compliance/compliance/23-compliance-a-training/47-know-your-customer-guidance",
        "applies_to_countries": [],
        "risk_weight": 5.0,
        "tags": ["EVASION", "DUAL_USE", "DIVERSION", "CRITICAL"],
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
    print("CORTEX-CI Belarus & Crimea Constraints Loader")
    print("Extended Russia Compliance Coverage")
    print("=" * 70)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")

    total = 0
    total += load_constraints(tenant_id, BELARUS_CONSTRAINTS, "Belarus Constraints")
    total += load_constraints(tenant_id, CRIMEA_CONSTRAINTS, "Crimea Constraints")
    total += load_constraints(tenant_id, DNR_LNR_CONSTRAINTS, "DNR/LNR Constraints")
    total += load_constraints(tenant_id, EVASION_CONSTRAINTS, "Evasion Detection Rules")

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
