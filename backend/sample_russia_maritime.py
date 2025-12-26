#!/usr/bin/env python3
"""
Russia Maritime & Shipping Monitoring for CORTEX-CI.
Vessel tracking, port restrictions, and shipping sanctions.

Run: python3 sample_russia_maritime.py
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
# MARITIME CONSTRAINTS
# ============================================================================
MARITIME_CONSTRAINTS = [
    # Port Restrictions
    {
        "name": "EU Port Ban - Russian-Flagged Vessels",
        "type": "trade_restriction",
        "severity": "critical",
        "description": "Prohibition on Russian-flagged vessels entering EU ports",
        "source_document": "EU Regulation 2022/576",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0576",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["MARITIME", "PORT_BAN", "EU", "CRITICAL"],
    },
    {
        "name": "UK Port Ban - Russian Vessels",
        "type": "trade_restriction",
        "severity": "critical",
        "description": "UK prohibition on Russian-flagged and Russian-owned vessels",
        "source_document": "Russia (Sanctions) (EU Exit) Regulations 2019",
        "external_url": "https://www.gov.uk/government/publications/russia-sanctions-guidance",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["MARITIME", "PORT_BAN", "UK", "CRITICAL"],
    },
    {
        "name": "Canada Port Ban - Russian Vessels",
        "type": "trade_restriction",
        "severity": "critical",
        "description": "Canada prohibition on Russian-flagged vessels",
        "source_document": "SEMA Russia Measures",
        "external_url": "https://www.international.gc.ca/world-monde/international_relations-relations_internationales/sanctions/russia-russie.aspx",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["MARITIME", "PORT_BAN", "CANADA", "CRITICAL"],
    },
    # Shipping Companies
    {
        "name": "Russian Shipping Company Sanctions",
        "type": "sanctions",
        "severity": "critical",
        "description": "Comprehensive sanctions on Russian state shipping companies",
        "source_document": "OFAC SDN List",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/specially-designated-nationals-and-blocked-persons-list-sdn-human-readable-lists",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["MARITIME", "SHIPPING", "SDN", "CRITICAL"],
    },
    # Shadow Fleet
    {
        "name": "Shadow Fleet Detection Protocol",
        "type": "compliance",
        "severity": "critical",
        "description": "Monitoring protocol for vessels in Russian oil shadow fleet",
        "source_document": "G7 Price Cap Coalition Guidance",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["MARITIME", "SHADOW_FLEET", "OIL_PRICE_CAP", "CRITICAL"],
    },
    {
        "name": "Aging Vessel Risk Flag",
        "type": "compliance",
        "severity": "high",
        "description": "Red flag: Vessels over 20 years old in Russian oil trade",
        "source_document": "Industry Guidance",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["MARITIME", "SHADOW_FLEET", "AGING_VESSEL", "RED_FLAG"],
    },
    {
        "name": "Flag Switching Detection",
        "type": "compliance",
        "severity": "critical",
        "description": "Detection of vessels that recently changed flag to avoid sanctions",
        "source_document": "OFAC Guidance",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["MARITIME", "FLAG_SWITCHING", "EVASION", "CRITICAL"],
    },
    {
        "name": "AIS Manipulation Detection",
        "type": "compliance",
        "severity": "critical",
        "description": "Detection of AIS transponder manipulation on vessels in Russian trade",
        "source_document": "IMO/Industry Standards",
        "external_url": "https://www.imo.org/en/OurWork/Safety/Pages/AIS.aspx",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["MARITIME", "AIS", "MANIPULATION", "CRITICAL"],
    },
    {
        "name": "STS (Ship-to-Ship) Transfer Monitoring",
        "type": "compliance",
        "severity": "critical",
        "description": "Enhanced monitoring of ship-to-ship transfers for Russian oil",
        "source_document": "G7 Price Cap Coalition",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["MARITIME", "STS_TRANSFER", "OIL", "CRITICAL"],
    },
    # Maritime Insurance
    {
        "name": "P&I Insurance Ban - Above Cap Oil",
        "type": "financial",
        "severity": "critical",
        "description": "Prohibition on P&I insurance for vessels carrying Russian oil above price cap",
        "source_document": "G7 Price Cap Coalition",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["MARITIME", "INSURANCE", "P&I", "OIL_PRICE_CAP", "CRITICAL"],
    },
    {
        "name": "Hull Insurance Restrictions - Russian Vessels",
        "type": "financial",
        "severity": "high",
        "description": "Restrictions on hull insurance for Russian-linked vessels",
        "source_document": "EU/UK Insurance Regulations",
        "external_url": "https://www.consilium.europa.eu/en/policies/sanctions/restrictive-measures-against-russia-over-ukraine/",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["MARITIME", "INSURANCE", "HULL"],
    },
    # Shipping Services
    {
        "name": "Brokerage Services Ban - Russian Oil",
        "type": "trade_restriction",
        "severity": "critical",
        "description": "Ban on providing ship brokerage for Russian oil above cap",
        "source_document": "G7 Price Cap Coalition",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["MARITIME", "BROKERAGE", "SERVICES", "CRITICAL"],
    },
    {
        "name": "Classification Services Restrictions",
        "type": "trade_restriction",
        "severity": "high",
        "description": "Restrictions on providing classification services to Russian vessels",
        "source_document": "EU Regulation 2022/576",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0576",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["MARITIME", "CLASSIFICATION", "SERVICES"],
    },
    {
        "name": "Flagging/Registration Services Ban",
        "type": "trade_restriction",
        "severity": "high",
        "description": "Prohibition on providing flagging/registration for vessels engaged in sanctions evasion",
        "source_document": "EU/UK Regulations",
        "external_url": "https://www.consilium.europa.eu/en/policies/sanctions/restrictive-measures-against-russia-over-ukraine/",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["MARITIME", "FLAGGING", "REGISTRATION"],
    },
    # Ports & Terminals
    {
        "name": "Russian Port Equipment Export Ban",
        "type": "export_control",
        "severity": "high",
        "description": "Ban on export of port equipment to Russian ports",
        "source_document": "EU Regulation 833/2014",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R0833",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["MARITIME", "PORT_EQUIPMENT", "EXPORT_BAN"],
    },
    # Crew Restrictions
    {
        "name": "Seafarer Visa Restrictions",
        "type": "compliance",
        "severity": "medium",
        "description": "Enhanced screening of Russian seafarers for sanctions compliance",
        "source_document": "National Immigration Policies",
        "external_url": "",
        "applies_to_countries": ["RU"],
        "risk_weight": 3.0,
        "tags": ["MARITIME", "SEAFARER", "VISA"],
    },
]

# ============================================================================
# SHIPPING ENTITIES
# ============================================================================
RUSSIAN_SHIPPING_ENTITIES = [
    {
        "name": "FESCO Transportation Group",
        "type": "corporation",
        "risk_score": 80.0,
        "sanctions_status": "SDN",
        "description": "Major Russian shipping and rail logistics group",
        "sanctions_programs": ["RUSSIA-EO14024", "SDN"],
        "tags": ["SHIPPING", "LOGISTICS", "SDN"],
    },
    {
        "name": "Novorossiysk Commercial Sea Port",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "CAUTION",
        "description": "Russia's largest port by cargo turnover",
        "sanctions_programs": [],
        "tags": ["PORT", "BLACK_SEA", "CAUTION"],
    },
    {
        "name": "Russian Maritime Register of Shipping",
        "type": "corporation",
        "risk_score": 70.0,
        "sanctions_status": "CAUTION",
        "description": "Russian classification society",
        "sanctions_programs": [],
        "tags": ["CLASSIFICATION", "MARITIME", "CAUTION"],
    },
    {
        "name": "Primorsk Commercial Port",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "CAUTION",
        "description": "Major Baltic oil export terminal",
        "sanctions_programs": [],
        "tags": ["PORT", "OIL_TERMINAL", "BALTIC", "CAUTION"],
    },
    {
        "name": "Ust-Luga Container Terminal",
        "type": "corporation",
        "risk_score": 70.0,
        "sanctions_status": "CAUTION",
        "description": "Major Baltic container port",
        "sanctions_programs": [],
        "tags": ["PORT", "CONTAINER", "BALTIC", "CAUTION"],
    },
    {
        "name": "Kozmino Oil Port",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "CAUTION",
        "description": "Far East oil export terminal (ESPO)",
        "sanctions_programs": [],
        "tags": ["PORT", "OIL_TERMINAL", "PACIFIC", "CAUTION"],
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


def load_entities(tenant_id: str, entities: list, category: str) -> int:
    """Load entities into database."""
    print(f"\n{'='*60}")
    print(f"Loading {len(entities)} {category}...")
    print(f"{'='*60}")

    count = 0
    for entity in entities:
        entity_id = str(uuid.uuid4())

        tags = entity.get("tags", [])
        tags_array = "ARRAY[" + ",".join([f"'{t}'" for t in tags]) + "]::varchar[]" if tags else "ARRAY[]::varchar[]"

        custom_data = {
            "sanctions_status": entity.get("sanctions_status", ""),
            "sanctions_programs": entity.get("sanctions_programs", []),
            "risk_score": entity.get("risk_score", 50.0),
        }
        custom_data_json = json.dumps(custom_data).replace("'", "''")

        sql = f"""
        INSERT INTO entities (
            id, tenant_id, name, type,
            description, is_active, tags, custom_data,
            created_at, updated_at
        ) VALUES (
            '{entity_id}',
            '{tenant_id}',
            '{escape_sql(entity["name"])}',
            '{entity["type"]}',
            '{escape_sql(entity.get("description", ""))}',
            true,
            {tags_array},
            '{custom_data_json}'::jsonb,
            NOW(),
            NOW()
        )
        ON CONFLICT DO NOTHING;
        """

        run_sql(sql)
        status = entity.get("sanctions_status", "N/A")
        print(f"  [OK] {entity['name'][:45]:<45} | {status}")
        count += 1

    return count


def main():
    print("=" * 70)
    print("CORTEX-CI Russia Maritime & Shipping Monitoring")
    print("Vessel Tracking, Port Bans, Shadow Fleet Detection")
    print("=" * 70)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")

    total_constraints = load_constraints(tenant_id, MARITIME_CONSTRAINTS, "Maritime Constraints")
    total_entities = load_entities(tenant_id, RUSSIAN_SHIPPING_ENTITIES, "Shipping Entities")

    # Get final counts
    result = run_sql(f"SELECT COUNT(*) FROM constraints WHERE tenant_id = '{tenant_id}';")
    for line in result.split("\n"):
        if line.strip().isdigit():
            print(f"\n{'='*70}")
            print(f"Constraints loaded: {total_constraints}")
            print(f"Entities loaded: {total_entities}")
            print(f"Total constraints in database: {line.strip()}")
            break


if __name__ == "__main__":
    main()
