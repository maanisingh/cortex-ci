#!/usr/bin/env python3
"""
Sample Russia-related constraints for CORTEX-CI.
These represent typical compliance requirements when dealing with Russian entities.

Run: python sample_russia_constraints.py
"""

import json
import subprocess
import uuid
from datetime import datetime, date

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


# Russia-related constraint templates
RUSSIA_CONSTRAINTS = [
    # OFAC Russia Sanctions
    {
        "name": "OFAC Russia Harmful Foreign Activities Sanctions",
        "type": "sanctions",
        "severity": "critical",
        "description": "Executive Order 14024 prohibiting transactions with persons engaged in harmful foreign activities of the Russian Federation",
        "source_document": "Executive Order 14024",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU", "BY"],
        "risk_weight": 5.0,
    },
    {
        "name": "OFAC Sectoral Sanctions Identifications List (SSI)",
        "type": "sanctions",
        "severity": "critical",
        "description": "Restrictions on certain transactions with specified Russian financial, energy, and defense sector entities",
        "source_document": "Directives 1-4 under EO 13662",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/consolidated-sanctions-list/sectoral-sanctions-identifications-ssi-list",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
    },
    {
        "name": "OFAC SDN Russia-related Designations",
        "type": "sanctions",
        "severity": "critical",
        "description": "Specially Designated Nationals and Blocked Persons associated with Russia",
        "source_document": "31 CFR Part 589",
        "external_url": "https://www.treasury.gov/ofac/downloads/sdn.xml",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
    },
    # EU Sanctions
    {
        "name": "EU Restrictive Measures (Russia/Ukraine)",
        "type": "sanctions",
        "severity": "critical",
        "description": "EU sanctions adopted in response to Russia's military aggression against Ukraine",
        "source_document": "Council Regulation (EU) 2022/263",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0263",
        "applies_to_countries": ["RU", "BY"],
        "risk_weight": 4.8,
    },
    {
        "name": "EU Financial Sector Sanctions (Russia)",
        "type": "financial",
        "severity": "critical",
        "description": "Prohibitions on providing certain financial services to Russian entities",
        "source_document": "Council Decision 2014/512/CFSP",
        "external_url": "https://www.consilium.europa.eu/en/policies/sanctions/restrictive-measures-against-russia-over-ukraine/",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
    },
    # UK Sanctions
    {
        "name": "UK Russia Sanctions Regime",
        "type": "sanctions",
        "severity": "critical",
        "description": "UK sanctions in response to Russian actions undermining Ukrainian sovereignty",
        "source_document": "Russia (Sanctions) (EU Exit) Regulations 2019",
        "external_url": "https://www.gov.uk/government/publications/russia-sanctions-guidance",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
    },
    # Export Controls
    {
        "name": "Russia Export Control Restrictions",
        "type": "export_control",
        "severity": "high",
        "description": "Export controls on dual-use goods, technology, and luxury goods to Russia",
        "source_document": "Export Administration Regulations (EAR)",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/russia-belarus",
        "applies_to_countries": ["RU", "BY"],
        "risk_weight": 4.0,
    },
    {
        "name": "Russia Military End-Use Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Restrictions on items intended for military end use or military end users in Russia",
        "source_document": "Entity List Rule",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern/entity-list",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
    },
    # Trade Restrictions
    {
        "name": "Russia Trade Prohibitions (Luxury Goods)",
        "type": "trade_restriction",
        "severity": "medium",
        "description": "Ban on export of luxury goods to Russia including vehicles, jewelry, and high-end electronics",
        "source_document": "EU Regulation 833/2014",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R0833",
        "applies_to_countries": ["RU"],
        "risk_weight": 2.5,
    },
    {
        "name": "Russia Energy Sector Restrictions",
        "type": "trade_restriction",
        "severity": "high",
        "description": "Restrictions on equipment and services for Russian energy sector",
        "source_document": "G7 Oil Price Cap",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.0,
    },
    # Financial Restrictions
    {
        "name": "SWIFT Disconnection (Russian Banks)",
        "type": "financial",
        "severity": "critical",
        "description": "Certain Russian banks disconnected from SWIFT messaging system",
        "source_document": "EU Council Decision",
        "external_url": "https://www.consilium.europa.eu/en/press/press-releases/2022/06/03/russia-s-aggression-against-ukraine-eu-adopts-sixth-package-of-sanctions/",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
    },
    {
        "name": "Russian Central Bank Asset Freeze",
        "type": "financial",
        "severity": "critical",
        "description": "Restrictions on transactions with the Central Bank of Russia",
        "source_document": "Executive Order 14024",
        "external_url": "https://home.treasury.gov/news/press-releases/jy0608",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
    },
    # AML/KYC
    {
        "name": "Enhanced Due Diligence (Russia)",
        "type": "aml",
        "severity": "high",
        "description": "Enhanced customer due diligence requirements for Russian-connected entities",
        "source_document": "FATF Guidance",
        "external_url": "https://www.fatf-gafi.org/en/publications/Fatfgeneral/call-for-action-march-2022.html",
        "applies_to_countries": ["RU"],
        "risk_weight": 3.5,
    },
    {
        "name": "Russian Oligarch Screening",
        "type": "kyc",
        "severity": "high",
        "description": "Screening requirements for Russian politically exposed persons and oligarchs",
        "source_document": "FinCEN Advisory",
        "external_url": "https://www.fincen.gov/news/news-releases/fincen-advises-increased-vigilance-potential-russian-sanctions-evasion-attempts",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.0,
    },
    # Compliance Requirements
    {
        "name": "Russia Sanctions Compliance Program",
        "type": "compliance",
        "severity": "high",
        "description": "Required compliance program for organizations with potential Russia exposure",
        "source_document": "OFAC Compliance Framework",
        "external_url": "https://home.treasury.gov/system/files/126/framework_ofac_cc.pdf",
        "applies_to_countries": ["RU"],
        "risk_weight": 3.0,
    },
    # Import Restrictions
    {
        "name": "Russia Import Bans (Oil/Gas)",
        "type": "import_regulation",
        "severity": "critical",
        "description": "Ban on imports of Russian oil, coal, and LNG",
        "source_document": "EU Energy Package",
        "external_url": "https://energy.ec.europa.eu/topics/oil-gas-and-coal/eu-russia-energy-relations_en",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
    },
]


def load_constraints(tenant_id: str):
    """Load sample Russia constraints."""
    print(f"Loading {len(RUSSIA_CONSTRAINTS)} Russia-related constraints...")

    for constraint in RUSSIA_CONSTRAINTS:
        constraint_id = str(uuid.uuid4())

        countries = constraint.get("applies_to_countries", [])
        countries_array = "ARRAY[" + ",".join([f"'{c}'" for c in countries]) + "]::varchar[]" if countries else "ARRAY[]::varchar[]"

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
            ARRAY['RUSSIA', 'SANCTIONS', 'COMPLIANCE']::varchar[],
            '{{}}'::jsonb,
            NOW(),
            NOW()
        )
        ON CONFLICT DO NOTHING;
        """

        run_sql(sql)
        print(f"  ✓ {constraint['name']}")

    # Get count
    result = run_sql(f"SELECT COUNT(*) FROM constraints WHERE tenant_id = '{tenant_id}';")
    for line in result.split("\n"):
        if line.strip().isdigit():
            print(f"\nTotal constraints: {line.strip()}")
            break


def main():
    print("=" * 60)
    print("CORTEX-CI Russia Constraints Loader")
    print("=" * 60)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")
    load_constraints(tenant_id)

    print("\n" + "=" * 60)
    print("Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
