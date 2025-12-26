#!/usr/bin/env python3
"""
Russia Entity Dependencies for CORTEX-CI.
Maps relationships between Russian sanctioned entities.

Dependency Types:
- ownership: Parent/subsidiary relationships
- financial: Banking/financial service relationships
- supply_chain: Vendor/supplier relationships
- personnel: Shared executives/board members
- contractual: Government contracts

Run: python3 sample_russia_dependencies.py
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


def get_tenant_id() -> str:
    """Get default tenant ID."""
    result = run_sql("SELECT id FROM tenants WHERE slug = 'default';")
    for line in result.split("\n"):
        line = line.strip()
        if line and "-" in line and len(line) == 36:
            return line
    return None


def get_entity_id(tenant_id: str, name: str) -> str:
    """Get entity ID by name."""
    sql = f"SELECT id FROM entities WHERE tenant_id = '{tenant_id}' AND name ILIKE '%{name}%' LIMIT 1;"
    result = run_sql(sql)
    for line in result.split("\n"):
        line = line.strip()
        if line and "-" in line and len(line) == 36:
            return line
    return None


# ============================================================================
# RUSSIA ENTITY DEPENDENCIES
# ============================================================================
RUSSIA_DEPENDENCIES = [
    # Gazprom relationships
    {
        "source": "Gazprom",
        "target": "Gazprombank",
        "type": "financial",
        "layer": "financial",
        "strength": 95.0,
        "description": "Gazprom's primary banking partner, holds significant stake",
    },
    {
        "source": "Gazprom",
        "target": "Central Bank of Russia",
        "type": "financial",
        "layer": "regulatory",
        "strength": 80.0,
        "description": "Central bank regulatory oversight of Gazprom finances",
    },
    {
        "source": "Gazprom",
        "target": "Rosatom",
        "type": "contractual",
        "layer": "operational",
        "strength": 60.0,
        "description": "Energy infrastructure cooperation agreements",
    },

    # Rosneft relationships
    {
        "source": "Rosneft",
        "target": "Igor Sechin",
        "type": "personnel",
        "layer": "governance",
        "strength": 100.0,
        "description": "Igor Sechin is CEO of Rosneft",
    },
    {
        "source": "Rosneft",
        "target": "Gazprombank",
        "type": "financial",
        "layer": "financial",
        "strength": 75.0,
        "description": "Banking services and financing",
    },
    {
        "source": "Rosneft",
        "target": "VTB Bank",
        "type": "financial",
        "layer": "financial",
        "strength": 85.0,
        "description": "Major lending and financial services",
    },

    # Rostec (Defense conglomerate) relationships
    {
        "source": "Rostec",
        "target": "Sergey Chemezov",
        "type": "personnel",
        "layer": "governance",
        "strength": 100.0,
        "description": "Sergey Chemezov is CEO of Rostec",
    },
    {
        "source": "Rostec",
        "target": "Almaz-Antey",
        "type": "ownership",
        "layer": "legal",
        "strength": 90.0,
        "description": "Rostec has significant control over Almaz-Antey",
    },
    {
        "source": "Rostec",
        "target": "Russian Helicopters",
        "type": "ownership",
        "layer": "legal",
        "strength": 100.0,
        "description": "Russian Helicopters is wholly owned by Rostec",
    },
    {
        "source": "Rostec",
        "target": "Kalashnikov Concern",
        "type": "ownership",
        "layer": "legal",
        "strength": 75.0,
        "description": "Rostec majority shareholder of Kalashnikov",
    },
    {
        "source": "Rostec",
        "target": "United Aircraft Corporation (UAC)",
        "type": "ownership",
        "layer": "legal",
        "strength": 100.0,
        "description": "UAC is a Rostec subsidiary",
    },
    {
        "source": "Rostec",
        "target": "Promsvyazbank",
        "type": "financial",
        "layer": "financial",
        "strength": 90.0,
        "description": "PSB designated as defense sector bank for Rostec entities",
    },

    # Bank Rossiya / Putin circle
    {
        "source": "Bank Rossiya",
        "target": "Yuri Kovalchuk",
        "type": "ownership",
        "layer": "legal",
        "strength": 100.0,
        "description": "Yuri Kovalchuk is largest shareholder of Bank Rossiya",
    },
    {
        "source": "Bank Rossiya",
        "target": "Arkady Rotenberg",
        "type": "financial",
        "layer": "financial",
        "strength": 80.0,
        "description": "Rotenberg companies bank with Bank Rossiya",
    },
    {
        "source": "Bank Rossiya",
        "target": "Gennady Timchenko",
        "type": "financial",
        "layer": "financial",
        "strength": 75.0,
        "description": "Timchenko business relationships with Bank Rossiya",
    },

    # Alfa Group relationships
    {
        "source": "Alfa-Bank",
        "target": "Mikhail Fridman",
        "type": "ownership",
        "layer": "legal",
        "strength": 100.0,
        "description": "Mikhail Fridman co-founded and controls Alfa Group",
    },
    {
        "source": "Alfa-Bank",
        "target": "Petr Aven",
        "type": "personnel",
        "layer": "governance",
        "strength": 100.0,
        "description": "Petr Aven is Chairman of Alfa-Bank",
    },

    # Sberbank - largest Russian bank
    {
        "source": "Sberbank of Russia",
        "target": "Central Bank of Russia",
        "type": "ownership",
        "layer": "legal",
        "strength": 100.0,
        "description": "Central Bank of Russia owns majority stake in Sberbank",
    },
    {
        "source": "Sberbank of Russia",
        "target": "Gazprom",
        "type": "financial",
        "layer": "financial",
        "strength": 85.0,
        "description": "Major lender to Gazprom",
    },
    {
        "source": "Sberbank of Russia",
        "target": "Rosneft",
        "type": "financial",
        "layer": "financial",
        "strength": 85.0,
        "description": "Major lender to Rosneft",
    },
    {
        "source": "Sberbank of Russia",
        "target": "Aeroflot",
        "type": "financial",
        "layer": "financial",
        "strength": 70.0,
        "description": "Banking services for Aeroflot",
    },

    # VTB relationships
    {
        "source": "VTB Bank",
        "target": "Russian Railways (RZD)",
        "type": "financial",
        "layer": "financial",
        "strength": 80.0,
        "description": "Major financing for RZD infrastructure projects",
    },
    {
        "source": "VTB Bank",
        "target": "Rostec",
        "type": "financial",
        "layer": "financial",
        "strength": 75.0,
        "description": "Defense sector financing",
    },

    # Rotenberg construction empire
    {
        "source": "Arkady Rotenberg",
        "target": "Boris Rotenberg",
        "type": "personnel",
        "layer": "governance",
        "strength": 100.0,
        "description": "Brothers, joint business interests",
    },
    {
        "source": "Arkady Rotenberg",
        "target": "Russian Railways (RZD)",
        "type": "contractual",
        "layer": "operational",
        "strength": 90.0,
        "description": "Major construction contracts with RZD",
    },
    {
        "source": "Arkady Rotenberg",
        "target": "Gazprom",
        "type": "contractual",
        "layer": "operational",
        "strength": 85.0,
        "description": "Pipeline construction contracts",
    },

    # Timchenko / Gunvor energy trading
    {
        "source": "Gennady Timchenko",
        "target": "Rosneft",
        "type": "contractual",
        "layer": "operational",
        "strength": 85.0,
        "description": "Oil trading relationships",
    },
    {
        "source": "Gennady Timchenko",
        "target": "Gazprom",
        "type": "contractual",
        "layer": "operational",
        "strength": 80.0,
        "description": "Gas trading relationships",
    },

    # Defense supply chain
    {
        "source": "Mikron Group",
        "target": "Almaz-Antey",
        "type": "supply_chain",
        "layer": "operational",
        "strength": 95.0,
        "description": "Semiconductor supply for missile systems",
    },
    {
        "source": "Mikron Group",
        "target": "Tactical Missiles Corporation",
        "type": "supply_chain",
        "layer": "operational",
        "strength": 90.0,
        "description": "Electronics for guided munitions",
    },
    {
        "source": "Baikal Electronics",
        "target": "Rostec",
        "type": "supply_chain",
        "layer": "operational",
        "strength": 85.0,
        "description": "Processor supply for defense systems",
    },

    # Aircraft/Defense
    {
        "source": "United Aircraft Corporation (UAC)",
        "target": "Russian Helicopters",
        "type": "contractual",
        "layer": "operational",
        "strength": 70.0,
        "description": "Component sharing and joint development",
    },
    {
        "source": "United Aircraft Corporation (UAC)",
        "target": "Aeroflot",
        "type": "contractual",
        "layer": "operational",
        "strength": 75.0,
        "description": "Civilian aircraft supply to Aeroflot",
    },

    # Shipbuilding
    {
        "source": "United Shipbuilding Corporation (USC)",
        "target": "Promsvyazbank",
        "type": "financial",
        "layer": "financial",
        "strength": 85.0,
        "description": "Defense sector banking services",
    },

    # Oligarch - Usmanov
    {
        "source": "Alisher Usmanov",
        "target": "VTB Bank",
        "type": "financial",
        "layer": "financial",
        "strength": 70.0,
        "description": "Banking relationships",
    },

    # Roman Abramovich
    {
        "source": "Roman Abramovich",
        "target": "Sberbank of Russia",
        "type": "financial",
        "layer": "financial",
        "strength": 65.0,
        "description": "Historical banking relationships",
    },

    # Kaspersky - regulatory
    {
        "source": "Kaspersky Lab",
        "target": "Central Bank of Russia",
        "type": "contractual",
        "layer": "operational",
        "strength": 50.0,
        "description": "Cybersecurity services to Russian government",
    },

    # Tanks
    {
        "source": "Uralvagonzavod",
        "target": "Rostec",
        "type": "ownership",
        "layer": "legal",
        "strength": 100.0,
        "description": "Uralvagonzavod is part of Rostec",
    },
    {
        "source": "Uralvagonzavod",
        "target": "Promsvyazbank",
        "type": "financial",
        "layer": "financial",
        "strength": 85.0,
        "description": "Defense sector banking",
    },
]


def load_dependencies(tenant_id: str):
    """Load Russia entity dependencies."""
    print(f"\n{'='*70}")
    print(f"Loading {len(RUSSIA_DEPENDENCIES)} Russia Entity Dependencies...")
    print(f"{'='*70}")

    success = 0
    failed = 0

    for dep in RUSSIA_DEPENDENCIES:
        source_id = get_entity_id(tenant_id, dep["source"])
        target_id = get_entity_id(tenant_id, dep["target"])

        if not source_id:
            print(f"  [SKIP] Source not found: {dep['source']}")
            failed += 1
            continue
        if not target_id:
            print(f"  [SKIP] Target not found: {dep['target']}")
            failed += 1
            continue

        dep_id = str(uuid.uuid4())

        sql = f"""
        INSERT INTO dependencies (
            id, tenant_id, source_entity_id, target_entity_id,
            relationship_type, layer, strength, description,
            is_active, created_at, updated_at
        ) VALUES (
            '{dep_id}',
            '{tenant_id}',
            '{source_id}',
            '{target_id}',
            '{dep["type"]}',
            '{dep.get("layer", "operational")}',
            {dep.get("strength", 50.0)},
            '{dep.get("description", "").replace("'", "''")}',
            true,
            NOW(),
            NOW()
        )
        ON CONFLICT DO NOTHING;
        """

        run_sql(sql)
        print(f"  [OK] {dep['source'][:25]:<25} --({dep['type'][:12]:<12})--> {dep['target'][:25]:<25}")
        success += 1

    print(f"\n{'='*70}")
    print(f"Dependencies created: {success}")
    print(f"Skipped (entity not found): {failed}")
    print(f"{'='*70}")

    return success


def main():
    print("=" * 70)
    print("CORTEX-CI Russia Entity Dependencies Loader")
    print("Mapping Relationships for Sanctions Analysis")
    print("=" * 70)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")

    total = load_dependencies(tenant_id)

    # Get final count
    result = run_sql(f"SELECT COUNT(*) FROM dependencies WHERE tenant_id = '{tenant_id}';")
    for line in result.split("\n"):
        if line.strip().isdigit():
            print(f"\nTotal dependencies in database: {line.strip()}")
            break


if __name__ == "__main__":
    main()
