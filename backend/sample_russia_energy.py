#!/usr/bin/env python3
"""
Russia Energy Sector Monitoring for CORTEX-CI.
Comprehensive tracking of Russian energy entities and transactions.

Covers:
- Oil companies (majors and independents)
- Gas companies
- Pipeline operators
- Energy traders
- Shadow fleet vessels
- Price cap compliance

Run: python3 sample_russia_energy.py
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
# RUSSIAN ENERGY COMPANIES
# ============================================================================
RUSSIAN_ENERGY_COMPANIES = [
    # Major Oil Companies
    {
        "name": "Surgutneftegas",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "SSI",
        "description": "Russia's fourth largest oil producer, significant cash reserves",
        "sector": "Oil & Gas",
        "identifiers": {"ticker": "SNGS", "lei": "213800JF3IPRN0E7LU94"},
        "sanctions_programs": ["RUSSIA-EO13662", "SSI-DIRECTIVE4"],
        "tags": ["ENERGY", "OIL", "SSI", "MAJOR_PRODUCER"],
    },
    {
        "name": "Tatneft",
        "type": "corporation",
        "risk_score": 70.0,
        "sanctions_status": "SSI",
        "description": "Major Russian oil company based in Tatarstan",
        "sector": "Oil & Gas",
        "identifiers": {"ticker": "TATN"},
        "sanctions_programs": ["RUSSIA-EO13662", "SSI"],
        "tags": ["ENERGY", "OIL", "SSI", "REGIONAL"],
    },
    {
        "name": "Bashneft",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "SSI",
        "description": "Oil company controlled by Rosneft",
        "sector": "Oil & Gas",
        "identifiers": {},
        "sanctions_programs": ["RUSSIA-EO13662"],
        "tags": ["ENERGY", "OIL", "ROSNEFT_SUBSIDIARY"],
    },
    {
        "name": "Slavneft",
        "type": "corporation",
        "risk_score": 70.0,
        "sanctions_status": "CAUTION",
        "description": "Joint venture between Rosneft and Gazprom Neft",
        "sector": "Oil & Gas",
        "identifiers": {},
        "sanctions_programs": [],
        "tags": ["ENERGY", "OIL", "JV"],
    },
    {
        "name": "Gazprom Neft",
        "type": "corporation",
        "risk_score": 80.0,
        "sanctions_status": "SSI",
        "description": "Oil arm of Gazprom, major producer",
        "sector": "Oil & Gas",
        "identifiers": {"ticker": "SIBN", "lei": "253400FXCXJI0P5GLL39"},
        "sanctions_programs": ["RUSSIA-EO13662", "SSI-DIRECTIVE4"],
        "tags": ["ENERGY", "OIL", "GAZPROM", "SSI"],
    },
    {
        "name": "Russneft",
        "type": "corporation",
        "risk_score": 65.0,
        "sanctions_status": "CAUTION",
        "description": "Mid-sized Russian oil company",
        "sector": "Oil & Gas",
        "identifiers": {},
        "sanctions_programs": [],
        "tags": ["ENERGY", "OIL", "INDEPENDENT"],
    },
    # Gas Companies
    {
        "name": "Novatek",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "SSI",
        "description": "Russia's largest independent gas producer and LNG exporter",
        "sector": "Natural Gas / LNG",
        "identifiers": {"ticker": "NVTK", "lei": "213800P4E7CKZNJ70V41"},
        "sanctions_programs": ["RUSSIA-EO13662", "SSI-DIRECTIVE2"],
        "tags": ["ENERGY", "GAS", "LNG", "SSI", "ARCTIC"],
    },
    {
        "name": "Yamal LNG",
        "type": "corporation",
        "risk_score": 80.0,
        "sanctions_status": "SSI",
        "description": "Major LNG project in Arctic Russia",
        "sector": "LNG",
        "identifiers": {},
        "sanctions_programs": ["RUSSIA-EO13662", "SSI"],
        "tags": ["ENERGY", "LNG", "ARCTIC", "NOVATEK"],
    },
    {
        "name": "Arctic LNG 2",
        "type": "corporation",
        "risk_score": 85.0,
        "sanctions_status": "SDN",
        "description": "Under-construction LNG project, subject to direct sanctions",
        "sector": "LNG",
        "identifiers": {},
        "sanctions_programs": ["RUSSIA-EO14024", "SDN"],
        "tags": ["ENERGY", "LNG", "ARCTIC", "SDN", "CRITICAL"],
    },
    # Pipeline Operators
    {
        "name": "Transneft",
        "type": "corporation",
        "risk_score": 85.0,
        "sanctions_status": "SSI",
        "description": "State-owned pipeline monopoly, transports 93% of Russian oil",
        "sector": "Pipeline",
        "identifiers": {"lei": "253400KMJYPWSF2CNA90"},
        "sanctions_programs": ["RUSSIA-EO13662", "SSI-DIRECTIVE4"],
        "tags": ["ENERGY", "PIPELINE", "OIL", "STATE_OWNED", "SSI"],
    },
    {
        "name": "Gazprom Transgaz",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "SSI",
        "description": "Gazprom subsidiary operating gas pipelines",
        "sector": "Pipeline",
        "identifiers": {},
        "sanctions_programs": ["RUSSIA-EO13662"],
        "tags": ["ENERGY", "PIPELINE", "GAS", "GAZPROM"],
    },
    {
        "name": "Nord Stream AG",
        "type": "corporation",
        "risk_score": 80.0,
        "sanctions_status": "SUSPENDED",
        "description": "Operator of Nord Stream pipelines (now damaged)",
        "sector": "Pipeline",
        "identifiers": {},
        "sanctions_programs": ["CAATSA", "EU-NORDSTREAM"],
        "tags": ["ENERGY", "PIPELINE", "NORD_STREAM", "SWITZERLAND"],
    },
    {
        "name": "Nord Stream 2 AG",
        "type": "corporation",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Nord Stream 2 project company, under sanctions",
        "sector": "Pipeline",
        "identifiers": {},
        "sanctions_programs": ["RUSSIA-NORDSTREAM2", "SDN"],
        "tags": ["ENERGY", "PIPELINE", "NORD_STREAM", "SDN"],
    },
    # Energy Traders
    {
        "name": "Litasco SA",
        "type": "corporation",
        "risk_score": 70.0,
        "sanctions_status": "CAUTION",
        "description": "Lukoil's international trading arm based in Geneva",
        "sector": "Oil Trading",
        "identifiers": {},
        "sanctions_programs": [],
        "tags": ["ENERGY", "TRADING", "LUKOIL", "SWITZERLAND"],
    },
    {
        "name": "Rosneft Trading SA",
        "type": "corporation",
        "risk_score": 80.0,
        "sanctions_status": "SSI",
        "description": "Rosneft's trading subsidiary",
        "sector": "Oil Trading",
        "identifiers": {},
        "sanctions_programs": ["RUSSIA-EO13662", "SSI"],
        "tags": ["ENERGY", "TRADING", "ROSNEFT"],
    },
    {
        "name": "Gazprom Marketing & Trading",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "SSI",
        "description": "Gazprom's international gas trading arm",
        "sector": "Gas Trading",
        "identifiers": {},
        "sanctions_programs": ["RUSSIA-EO13662"],
        "tags": ["ENERGY", "TRADING", "GAZPROM", "GAS"],
    },
]

# ============================================================================
# SHADOW FLEET VESSELS (for oil price cap monitoring)
# ============================================================================
SHADOW_FLEET = [
    {
        "name": "Shadow Fleet Vessel Monitoring",
        "type": "monitoring_program",
        "risk_score": 95.0,
        "sanctions_status": "HIGH_RISK",
        "description": "Program for monitoring vessels used to circumvent oil price cap",
        "sector": "Maritime",
        "identifiers": {},
        "sanctions_programs": ["OIL_PRICE_CAP"],
        "tags": ["SHIPPING", "SHADOW_FLEET", "OIL_PRICE_CAP", "EVASION"],
    },
    {
        "name": "Sovcomflot (SCF Group)",
        "type": "corporation",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Russia's largest shipping company, major tanker operator",
        "sector": "Maritime/Tankers",
        "identifiers": {},
        "sanctions_programs": ["RUSSIA-EO14024", "SDN"],
        "tags": ["SHIPPING", "TANKERS", "STATE_OWNED", "SDN", "CRITICAL"],
    },
]

# ============================================================================
# ENERGY SECTOR CONSTRAINTS
# ============================================================================
ENERGY_CONSTRAINTS = [
    {
        "name": "G7 Russian Oil Price Cap ($60/bbl)",
        "type": "trade_restriction",
        "severity": "critical",
        "description": "Price cap on Russian-origin crude oil at $60 per barrel",
        "source_document": "G7 Price Cap Coalition",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "OIL_PRICE_CAP", "G7", "CRITICAL"],
    },
    {
        "name": "Petroleum Products Price Cap ($100/$45)",
        "type": "trade_restriction",
        "severity": "critical",
        "description": "Price caps on Russian petroleum products ($100 premium, $45 discount)",
        "source_document": "G7 Price Cap Coalition",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "PETROLEUM_PRICE_CAP", "G7", "CRITICAL"],
    },
    {
        "name": "Russian Crude Oil Import Ban (EU)",
        "type": "import_regulation",
        "severity": "critical",
        "description": "EU ban on seaborne Russian crude oil imports",
        "source_document": "EU Regulation 2022/879",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0879",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "OIL", "EU", "IMPORT_BAN", "CRITICAL"],
    },
    {
        "name": "Russian Coal Import Ban (EU)",
        "type": "import_regulation",
        "severity": "high",
        "description": "EU ban on imports of Russian coal",
        "source_document": "EU Regulation 2022/576",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0576",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["ENERGY", "COAL", "EU", "IMPORT_BAN"],
    },
    {
        "name": "LNG Services Restriction",
        "type": "trade_restriction",
        "severity": "high",
        "description": "EU restrictions on transshipment of Russian LNG through EU ports",
        "source_document": "EU 14th Sanctions Package",
        "external_url": "https://www.consilium.europa.eu/en/press/press-releases/",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["ENERGY", "LNG", "EU", "TRANSSHIPMENT"],
    },
    {
        "name": "Energy Equipment Export Ban",
        "type": "export_control",
        "severity": "critical",
        "description": "Ban on export of energy sector technology and equipment to Russia",
        "source_document": "EU Regulation 833/2014",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R0833",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "EXPORT_BAN", "TECHNOLOGY", "CRITICAL"],
    },
    {
        "name": "Oil Refining Technology Export Ban",
        "type": "export_control",
        "severity": "critical",
        "description": "Ban on export of catalytic cracking technology for oil refining",
        "source_document": "BIS Russia Export Controls",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/russia-belarus",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "REFINING", "TECHNOLOGY", "EXPORT_BAN", "CRITICAL"],
    },
    {
        "name": "Arctic Energy Project Investment Ban",
        "type": "financial",
        "severity": "critical",
        "description": "Prohibition on new investment in Russian Arctic energy projects",
        "source_document": "EU Council Decision",
        "external_url": "https://www.consilium.europa.eu/en/policies/sanctions/restrictive-measures-against-russia-over-ukraine/",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "ARCTIC", "INVESTMENT_BAN", "CRITICAL"],
    },
    {
        "name": "Deep Water Drilling Technology Ban",
        "type": "export_control",
        "severity": "critical",
        "description": "Ban on export of deep water oil exploration and production technology",
        "source_document": "SSI Directive 4",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "DEEP_WATER", "TECHNOLOGY", "SSI", "CRITICAL"],
    },
    {
        "name": "Shale Oil Technology Export Ban",
        "type": "export_control",
        "severity": "critical",
        "description": "Ban on export of shale oil extraction technology to Russia",
        "source_document": "SSI Directive 4",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "SHALE", "TECHNOLOGY", "SSI", "CRITICAL"],
    },
    {
        "name": "Maritime Insurance Ban (Russian Oil Above Cap)",
        "type": "financial",
        "severity": "critical",
        "description": "Prohibition on providing insurance for Russian oil transported above price cap",
        "source_document": "G7 Price Cap Coalition",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "INSURANCE", "MARITIME", "OIL_PRICE_CAP", "CRITICAL"],
    },
    {
        "name": "Price Cap Attestation Requirement",
        "type": "compliance",
        "severity": "high",
        "description": "Requirement for attestation that Russian oil was purchased at or below price cap",
        "source_document": "OFAC Guidance",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["ENERGY", "OIL_PRICE_CAP", "ATTESTATION", "COMPLIANCE"],
    },
]


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
            "sector": entity.get("sector", ""),
            "identifiers": entity.get("identifiers", {}),
        }
        custom_data_json = json.dumps(custom_data).replace("'", "''")

        sql = f"""
        INSERT INTO entities (
            id, tenant_id, name, type, risk_score,
            description, is_active, tags, custom_data,
            created_at, updated_at
        ) VALUES (
            '{entity_id}',
            '{tenant_id}',
            '{escape_sql(entity["name"])}',
            '{entity["type"]}',
            {entity.get("risk_score", 50.0)},
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
        print(f"  [OK] {entity['name'][:45]:<45} | Status: {status}")
        count += 1

    return count


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
    print("CORTEX-CI Russia Energy Sector Monitoring")
    print("Oil, Gas, LNG, Pipeline & Price Cap Compliance")
    print("=" * 70)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")

    total_entities = 0
    total_entities += load_entities(tenant_id, RUSSIAN_ENERGY_COMPANIES, "Energy Companies")
    total_entities += load_entities(tenant_id, SHADOW_FLEET, "Shadow Fleet Monitoring")

    total_constraints = load_constraints(tenant_id, ENERGY_CONSTRAINTS, "Energy Sector Constraints")

    # Get final counts
    result = run_sql(f"SELECT COUNT(*) FROM entities WHERE tenant_id = '{tenant_id}';")
    for line in result.split("\n"):
        if line.strip().isdigit():
            print(f"\n{'='*70}")
            print(f"Entities loaded this session: {total_entities}")
            print(f"Total entities in database: {line.strip()}")
            break

    result = run_sql(f"SELECT COUNT(*) FROM constraints WHERE tenant_id = '{tenant_id}';")
    for line in result.split("\n"):
        if line.strip().isdigit():
            print(f"Constraints loaded this session: {total_constraints}")
            print(f"Total constraints in database: {line.strip()}")
            print(f"{'='*70}")
            break


if __name__ == "__main__":
    main()
