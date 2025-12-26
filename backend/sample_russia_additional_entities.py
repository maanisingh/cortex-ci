#!/usr/bin/env python3
"""
Additional Russia Sanctioned Entities for CORTEX-CI.
Expanding entity coverage for comprehensive compliance.

Run: python3 sample_russia_additional_entities.py
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
# ADDITIONAL RUSSIAN BANKS
# ============================================================================
ADDITIONAL_BANKS = [
    {
        "name": "Otkritie Bank",
        "type": "financial_institution",
        "risk_score": 85.0,
        "sanctions_status": "SDN",
        "description": "Large Russian bank under full blocking sanctions",
        "sanctions_programs": ["RUSSIA-EO14024", "SDN"],
        "tags": ["BANK", "SDN", "RETAIL"],
    },
    {
        "name": "Sovcombank",
        "type": "financial_institution",
        "risk_score": 85.0,
        "sanctions_status": "SDN",
        "description": "Major Russian bank under sanctions",
        "sanctions_programs": ["RUSSIA-EO14024", "SDN"],
        "tags": ["BANK", "SDN", "RETAIL"],
    },
    {
        "name": "Novikombank",
        "type": "financial_institution",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Defense industry bank, Rostec affiliated",
        "sanctions_programs": ["RUSSIA-EO14024", "SDN", "DEFENSE"],
        "tags": ["BANK", "SDN", "DEFENSE", "CRITICAL"],
    },
    {
        "name": "SMP Bank",
        "type": "financial_institution",
        "risk_score": 95.0,
        "sanctions_status": "SDN",
        "description": "Bank owned by Rotenberg brothers",
        "sanctions_programs": ["RUSSIA-EO13661", "SDN"],
        "tags": ["BANK", "SDN", "ROTENBERG", "CRITICAL"],
    },
    {
        "name": "Transkapitalbank",
        "type": "financial_institution",
        "risk_score": 85.0,
        "sanctions_status": "SDN",
        "description": "Russian bank under sanctions",
        "sanctions_programs": ["RUSSIA-EO14024", "SDN"],
        "tags": ["BANK", "SDN"],
    },
    {
        "name": "Tinkoff Bank",
        "type": "financial_institution",
        "risk_score": 70.0,
        "sanctions_status": "CAUTION",
        "description": "Digital bank, limited sanctions",
        "sanctions_programs": [],
        "tags": ["BANK", "DIGITAL", "CAUTION"],
    },
    {
        "name": "Renaissance Credit",
        "type": "financial_institution",
        "risk_score": 75.0,
        "sanctions_status": "SSI",
        "description": "Consumer credit bank",
        "sanctions_programs": ["RUSSIA-EO14024"],
        "tags": ["BANK", "CONSUMER"],
    },
]

# ============================================================================
# RUSSIAN INSURANCE COMPANIES
# ============================================================================
RUSSIAN_INSURANCE = [
    {
        "name": "Sogaz Insurance",
        "type": "corporation",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Largest Russian insurer, Gazprom linked, under sanctions",
        "sanctions_programs": ["RUSSIA-EO14024", "SDN"],
        "tags": ["INSURANCE", "SDN", "GAZPROM", "CRITICAL"],
    },
    {
        "name": "RESO-Garantia",
        "type": "corporation",
        "risk_score": 70.0,
        "sanctions_status": "CAUTION",
        "description": "Major Russian insurance company",
        "sanctions_programs": [],
        "tags": ["INSURANCE", "CAUTION"],
    },
    {
        "name": "Ingosstrakh",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "CAUTION",
        "description": "Large Russian insurer",
        "sanctions_programs": [],
        "tags": ["INSURANCE", "CAUTION"],
    },
    {
        "name": "Alfastrakhovanie",
        "type": "corporation",
        "risk_score": 80.0,
        "sanctions_status": "SDN",
        "description": "Alfa Group insurance company, under sanctions",
        "sanctions_programs": ["RUSSIA-EO14024"],
        "tags": ["INSURANCE", "ALFA_GROUP", "SDN"],
    },
]

# ============================================================================
# ADDITIONAL RUSSIAN OLIGARCHS
# ============================================================================
ADDITIONAL_OLIGARCHS = [
    {
        "name": "Oleg Deripaska",
        "type": "individual",
        "risk_score": 95.0,
        "sanctions_status": "SDN",
        "description": "Aluminum magnate, Rusal founder, under sanctions (with limited delistings)",
        "sanctions_programs": ["RUSSIA-EO14024", "SDN"],
        "tags": ["OLIGARCH", "SDN", "ALUMINUM", "CRITICAL"],
    },
    {
        "name": "Viktor Vekselberg",
        "type": "individual",
        "risk_score": 95.0,
        "sanctions_status": "SDN",
        "description": "Energy and metals billionaire, Renova Group",
        "sanctions_programs": ["RUSSIA-EO14024", "SDN"],
        "tags": ["OLIGARCH", "SDN", "ENERGY", "CRITICAL"],
    },
    {
        "name": "Alexey Mordashov",
        "type": "individual",
        "risk_score": 90.0,
        "sanctions_status": "EU_UK_SANCTIONED",
        "description": "Steel magnate, Severstal owner, EU/UK sanctioned",
        "sanctions_programs": ["EU-RUSSIA", "UK-RUSSIA"],
        "tags": ["OLIGARCH", "STEEL", "EU_SANCTIONS"],
    },
    {
        "name": "Andrey Melnichenko",
        "type": "individual",
        "risk_score": 90.0,
        "sanctions_status": "EU_UK_SANCTIONED",
        "description": "Fertilizer and coal magnate, EuroChem founder",
        "sanctions_programs": ["EU-RUSSIA", "UK-RUSSIA"],
        "tags": ["OLIGARCH", "FERTILIZER", "EU_SANCTIONS"],
    },
    {
        "name": "Vladimir Lisin",
        "type": "individual",
        "risk_score": 85.0,
        "sanctions_status": "UK_SANCTIONED",
        "description": "Steel billionaire, NLMK owner",
        "sanctions_programs": ["UK-RUSSIA"],
        "tags": ["OLIGARCH", "STEEL", "UK_SANCTIONS"],
    },
    {
        "name": "Leonid Mikhelson",
        "type": "individual",
        "risk_score": 90.0,
        "sanctions_status": "EU_UK_SANCTIONED",
        "description": "Novatek founder and CEO, LNG billionaire",
        "sanctions_programs": ["EU-RUSSIA", "UK-RUSSIA"],
        "tags": ["OLIGARCH", "LNG", "NOVATEK", "EU_SANCTIONS"],
    },
    {
        "name": "Vagit Alekperov",
        "type": "individual",
        "risk_score": 90.0,
        "sanctions_status": "UK_SANCTIONED",
        "description": "Lukoil founder, former president",
        "sanctions_programs": ["UK-RUSSIA"],
        "tags": ["OLIGARCH", "LUKOIL", "OIL", "UK_SANCTIONS"],
    },
    {
        "name": "German Khan",
        "type": "individual",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Alfa Group co-founder, under US/EU/UK sanctions",
        "sanctions_programs": ["RUSSIA-EO14024", "EU-RUSSIA", "UK-RUSSIA"],
        "tags": ["OLIGARCH", "SDN", "ALFA_GROUP", "CRITICAL"],
    },
]

# ============================================================================
# RUSSIAN MEDIA & TELECOM
# ============================================================================
RUSSIAN_MEDIA_TELECOM = [
    {
        "name": "RT (Russia Today)",
        "type": "corporation",
        "risk_score": 85.0,
        "sanctions_status": "RESTRICTED",
        "description": "State-funded media outlet, banned in EU/UK/Canada",
        "sanctions_programs": ["EU-MEDIA-BAN", "UK-MEDIA-BAN"],
        "tags": ["MEDIA", "STATE_MEDIA", "RESTRICTED"],
    },
    {
        "name": "Sputnik News",
        "type": "corporation",
        "risk_score": 85.0,
        "sanctions_status": "RESTRICTED",
        "description": "State-funded news agency, restricted in Western countries",
        "sanctions_programs": ["EU-MEDIA-BAN", "UK-MEDIA-BAN"],
        "tags": ["MEDIA", "STATE_MEDIA", "RESTRICTED"],
    },
    {
        "name": "National Media Group",
        "type": "corporation",
        "risk_score": 90.0,
        "sanctions_status": "SDN",
        "description": "Major media holding, Kovalchuk owned",
        "sanctions_programs": ["RUSSIA-EO14024"],
        "tags": ["MEDIA", "KOVALCHUK", "SDN"],
    },
    {
        "name": "Rostelecom",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "CAUTION",
        "description": "State telecom company, internet provider",
        "sanctions_programs": [],
        "tags": ["TELECOM", "STATE_OWNED", "CAUTION"],
    },
    {
        "name": "MTS (Mobile TeleSystems)",
        "type": "corporation",
        "risk_score": 70.0,
        "sanctions_status": "CAUTION",
        "description": "Largest Russian mobile operator",
        "sanctions_programs": [],
        "tags": ["TELECOM", "MOBILE", "CAUTION"],
    },
]

# ============================================================================
# RUSSIAN MINING & METALS
# ============================================================================
RUSSIAN_MINING = [
    {
        "name": "Norilsk Nickel",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "CAUTION",
        "description": "World's largest nickel and palladium producer",
        "sanctions_programs": [],
        "tags": ["MINING", "NICKEL", "PALLADIUM", "CAUTION"],
    },
    {
        "name": "Rusal",
        "type": "corporation",
        "risk_score": 70.0,
        "sanctions_status": "DELISTED",
        "description": "Major aluminum producer, sanctions removed 2019",
        "sanctions_programs": [],
        "tags": ["MINING", "ALUMINUM", "DELISTED"],
    },
    {
        "name": "Severstal",
        "type": "corporation",
        "risk_score": 80.0,
        "sanctions_status": "EU_UK_SANCTIONED",
        "description": "Major steel producer, Mordashov controlled",
        "sanctions_programs": ["EU-RUSSIA", "UK-RUSSIA"],
        "tags": ["MINING", "STEEL", "EU_SANCTIONS"],
    },
    {
        "name": "NLMK (Novolipetsk Steel)",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "CAUTION",
        "description": "Major steel producer, Lisin controlled",
        "sanctions_programs": [],
        "tags": ["MINING", "STEEL", "CAUTION"],
    },
    {
        "name": "MMC (Magnitogorsk Iron and Steel)",
        "type": "corporation",
        "risk_score": 70.0,
        "sanctions_status": "CAUTION",
        "description": "Large Russian steelmaker",
        "sanctions_programs": [],
        "tags": ["MINING", "STEEL", "CAUTION"],
    },
    {
        "name": "ALROSA",
        "type": "corporation",
        "risk_score": 85.0,
        "sanctions_status": "SDN",
        "description": "World's largest diamond producer, state-owned, under sanctions",
        "sanctions_programs": ["RUSSIA-EO14024", "SDN"],
        "tags": ["MINING", "DIAMONDS", "STATE_OWNED", "SDN"],
    },
    {
        "name": "Polymetal",
        "type": "corporation",
        "risk_score": 70.0,
        "sanctions_status": "CAUTION",
        "description": "Precious metals producer",
        "sanctions_programs": [],
        "tags": ["MINING", "GOLD", "SILVER", "CAUTION"],
    },
    {
        "name": "EuroChem",
        "type": "corporation",
        "risk_score": 80.0,
        "sanctions_status": "CAUTION",
        "description": "Major fertilizer producer, Melnichenko controlled",
        "sanctions_programs": [],
        "tags": ["MINING", "FERTILIZER", "CAUTION"],
    },
    {
        "name": "Uralkali",
        "type": "corporation",
        "risk_score": 75.0,
        "sanctions_status": "CAUTION",
        "description": "Major potash producer",
        "sanctions_programs": [],
        "tags": ["MINING", "POTASH", "FERTILIZER", "CAUTION"],
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
        risk = entity.get("risk_score", 0)
        print(f"  [OK] {entity['name'][:40]:<40} | Risk: {risk:>5.1f} | {status}")
        count += 1

    return count


def main():
    print("=" * 70)
    print("CORTEX-CI Additional Russia Entities")
    print("Expanding Sanctioned Entity Coverage")
    print("=" * 70)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")

    total = 0
    total += load_entities(tenant_id, ADDITIONAL_BANKS, "Additional Banks")
    total += load_entities(tenant_id, RUSSIAN_INSURANCE, "Insurance Companies")
    total += load_entities(tenant_id, ADDITIONAL_OLIGARCHS, "Additional Oligarchs")
    total += load_entities(tenant_id, RUSSIAN_MEDIA_TELECOM, "Media & Telecom")
    total += load_entities(tenant_id, RUSSIAN_MINING, "Mining & Metals")

    # Get final count
    result = run_sql(f"SELECT COUNT(*) FROM entities WHERE tenant_id = '{tenant_id}';")
    for line in result.split("\n"):
        if line.strip().isdigit():
            print(f"\n{'='*70}")
            print(f"Entities loaded this session: {total}")
            print(f"Total entities in database: {line.strip()}")
            print(f"{'='*70}")
            break


if __name__ == "__main__":
    main()
