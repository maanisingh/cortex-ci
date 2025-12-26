#!/usr/bin/env python3
"""
Russia Sanctions Scenarios for CORTEX-CI.
Pre-built scenarios for simulating sanctions impact and cascading effects.

Scenario Categories:
- New sanctions designation (SDN, SSI)
- Secondary sanctions enforcement
- SWIFT disconnection impact
- Export control violations
- Energy sector restrictions
- Asset freeze scenarios
- Supply chain disruption

Run: python3 sample_russia_scenarios.py
"""

import json
import subprocess
import uuid
from datetime import datetime, date, timedelta

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
# RUSSIA SANCTIONS SCENARIOS
# ============================================================================
RUSSIA_SCENARIOS = [
    # SDN Designation Scenarios
    {
        "name": "New SDN Designation - Major Russian Bank",
        "description": "Scenario simulating OFAC adding a new major Russian bank to SDN list. Immediate blocking of all assets and prohibition of transactions.",
        "type": "sanctions_designation",
        "severity": "critical",
        "trigger_entity": "VTB Bank",
        "parameters": {
            "sanctions_type": "SDN",
            "sanctions_program": "RUSSIA-EO14024",
            "effective_date": "immediate",
            "wind_down_period": "30 days",
            "asset_freeze": True,
            "transaction_ban": True,
        },
        "expected_impacts": [
            "All US persons must freeze assets and cease transactions",
            "Secondary sanctions risk for non-US banks",
            "SWIFT messaging restrictions",
            "Correspondent banking termination",
            "Trade finance disruption",
        ],
        "affected_sectors": ["Banking", "Trade Finance", "Energy", "Defense"],
        "risk_multiplier": 2.5,
        "tags": ["SDN", "BANKING", "OFAC", "CRITICAL"],
    },
    {
        "name": "Secondary Sanctions Enforcement - European Bank",
        "description": "OFAC enforcement action against non-US bank for continued transactions with sanctioned Russian entities.",
        "type": "enforcement",
        "severity": "high",
        "trigger_entity": None,
        "parameters": {
            "penalty_range": "$50M - $500M",
            "remediation_requirements": [
                "Enhanced compliance program",
                "Independent monitor",
                "Regular reporting to OFAC",
            ],
            "correspondent_banking_impact": True,
        },
        "expected_impacts": [
            "Global de-risking acceleration",
            "Increased compliance costs for all banks",
            "Reduction in Russia-related transactions",
            "Enhanced due diligence requirements",
        ],
        "affected_sectors": ["Global Banking", "Trade Finance"],
        "risk_multiplier": 1.8,
        "tags": ["SECONDARY_SANCTIONS", "ENFORCEMENT", "BANKING"],
    },

    # SWIFT Disconnection
    {
        "name": "SWIFT Disconnection - Russian Bank",
        "description": "Additional Russian banks disconnected from SWIFT messaging system.",
        "type": "swift_disconnection",
        "severity": "critical",
        "trigger_entity": "Gazprombank",
        "parameters": {
            "swift_ban": True,
            "alternative_systems": ["SPFS (Russian)", "CIPS (Chinese)"],
            "transition_period": "0 days",
            "correspondent_impact": "severe",
        },
        "expected_impacts": [
            "Immediate payment processing disruption",
            "Trade settlement delays",
            "Energy payment complications",
            "Alternative payment route development",
        ],
        "affected_sectors": ["Banking", "Energy", "Trade"],
        "risk_multiplier": 2.2,
        "tags": ["SWIFT", "PAYMENTS", "CRITICAL"],
    },

    # Export Control Scenarios
    {
        "name": "Export Control Violation - Semiconductor Diversion",
        "description": "Detection of controlled semiconductor components diverted to Russian defense entities.",
        "type": "export_control",
        "severity": "critical",
        "trigger_entity": "Mikron Group",
        "parameters": {
            "controlled_items": ["Advanced chips", "FPGA", "Memory"],
            "diversion_method": "Third-country transshipment",
            "suspected_end_use": "Military",
            "enforcement_risk": "high",
        },
        "expected_impacts": [
            "BIS Entity List addition",
            "Enhanced license requirements",
            "Third-country screening intensification",
            "Supply chain audit requirements",
        ],
        "affected_sectors": ["Technology", "Defense", "Manufacturing"],
        "risk_multiplier": 2.0,
        "tags": ["EXPORT_CONTROL", "SEMICONDUCTORS", "DEFENSE"],
    },
    {
        "name": "Military End-Use Detection - UAV Components",
        "description": "Components identified in Russian military drones traced back through supply chain.",
        "type": "export_control",
        "severity": "critical",
        "trigger_entity": "Rostec",
        "parameters": {
            "component_types": ["Engines", "Sensors", "Navigation"],
            "detection_method": "Battlefield recovery",
            "countries_involved": ["China", "UAE", "Turkey"],
            "timeline": "6 months",
        },
        "expected_impacts": [
            "Enhanced end-use screening",
            "Third-party due diligence requirements",
            "Transshipment route monitoring",
            "Supplier certification requirements",
        ],
        "affected_sectors": ["Aerospace", "Defense", "Technology"],
        "risk_multiplier": 2.3,
        "tags": ["EXPORT_CONTROL", "MILITARY", "UAV"],
    },

    # Energy Sector Scenarios
    {
        "name": "Oil Price Cap Violation",
        "description": "Detection of Russian oil transactions above G7 price cap.",
        "type": "trade_restriction",
        "severity": "high",
        "trigger_entity": "Rosneft",
        "parameters": {
            "price_cap": "$60/barrel",
            "violation_amount": "$75/barrel",
            "shipping_companies": ["Shadow fleet vessels"],
            "insurance_implications": True,
        },
        "expected_impacts": [
            "Shipping company sanctions",
            "Insurance provider restrictions",
            "Enhanced attestation requirements",
            "Shadow fleet targeting",
        ],
        "affected_sectors": ["Energy", "Shipping", "Insurance"],
        "risk_multiplier": 1.7,
        "tags": ["OIL_PRICE_CAP", "ENERGY", "SHIPPING"],
    },
    {
        "name": "LNG Transshipment Restrictions",
        "description": "New restrictions on Russian LNG transshipment through EU ports.",
        "type": "trade_restriction",
        "severity": "high",
        "trigger_entity": "Gazprom",
        "parameters": {
            "affected_ports": ["EU ports"],
            "transshipment_ban": True,
            "direct_sales_permitted": "Temporary",
            "implementation_timeline": "90 days",
        },
        "expected_impacts": [
            "LNG route restructuring",
            "Asian market redirection",
            "Price arbitrage elimination",
            "European energy security impact",
        ],
        "affected_sectors": ["Energy", "Shipping", "Trade"],
        "risk_multiplier": 1.5,
        "tags": ["LNG", "ENERGY", "EU_SANCTIONS"],
    },

    # Oligarch/PEP Scenarios
    {
        "name": "Oligarch Asset Freeze Expansion",
        "description": "G7 coordinated expansion of asset freezes to additional Russian oligarchs.",
        "type": "asset_freeze",
        "severity": "high",
        "trigger_entity": "Vladimir Potanin",
        "parameters": {
            "jurisdictions": ["US", "EU", "UK", "Canada", "Japan"],
            "asset_types": ["Real estate", "Yachts", "Aircraft", "Investments"],
            "corporate_structures": "Traced",
            "family_members_included": True,
        },
        "expected_impacts": [
            "Asset tracing intensification",
            "Corporate structure unwinding",
            "Trust and foundation scrutiny",
            "Nominee identification",
        ],
        "affected_sectors": ["Real Estate", "Luxury", "Financial Services"],
        "risk_multiplier": 1.6,
        "tags": ["OLIGARCH", "ASSET_FREEZE", "PEP"],
    },
    {
        "name": "Putin Inner Circle Designation",
        "description": "Additional designations of Putin's close associates and their business networks.",
        "type": "sanctions_designation",
        "severity": "critical",
        "trigger_entity": "Yuri Kovalchuk",
        "parameters": {
            "designated_network": ["Business partners", "Family", "Associates"],
            "asset_scope": "Global",
            "travel_ban": True,
            "business_relationship_prohibition": True,
        },
        "expected_impacts": [
            "Bank Rossiya cascading effects",
            "Media company restrictions",
            "Financial network disruption",
            "Third-party relationship termination",
        ],
        "affected_sectors": ["Banking", "Media", "Real Estate"],
        "risk_multiplier": 2.0,
        "tags": ["PUTIN_CIRCLE", "SDN", "CRITICAL"],
    },

    # Defense Sector Scenarios
    {
        "name": "Defense Sector Supply Chain Disruption",
        "description": "Comprehensive sanctions on Russian defense supply chain entities.",
        "type": "supply_chain",
        "severity": "critical",
        "trigger_entity": "Almaz-Antey",
        "parameters": {
            "affected_entities": ["Suppliers", "Subsidiaries", "JVs"],
            "technology_restrictions": "Comprehensive",
            "third_country_sourcing_ban": True,
            "enforcement_priority": "High",
        },
        "expected_impacts": [
            "Component shortage acceleration",
            "Production timeline delays",
            "Quality degradation",
            "Alternative sourcing attempts",
        ],
        "affected_sectors": ["Defense", "Technology", "Manufacturing"],
        "risk_multiplier": 2.4,
        "tags": ["DEFENSE", "SUPPLY_CHAIN", "CRITICAL"],
    },
    {
        "name": "Tank Production Bottleneck",
        "description": "Targeted sanctions on tank production supply chain.",
        "type": "supply_chain",
        "severity": "critical",
        "trigger_entity": "Uralvagonzavod",
        "parameters": {
            "critical_components": ["Optics", "Electronics", "Engines"],
            "current_inventory": "6 months",
            "production_impact": "50% reduction",
            "alternative_sources": "Limited",
        },
        "expected_impacts": [
            "Tank production decline",
            "Quality compromises",
            "Older model refurbishment increase",
            "Component cannibalization",
        ],
        "affected_sectors": ["Defense", "Manufacturing"],
        "risk_multiplier": 2.1,
        "tags": ["DEFENSE", "TANKS", "SUPPLY_CHAIN"],
    },

    # Aviation Sector
    {
        "name": "Aircraft Leasing Seizure Scenario",
        "description": "Enforcement of aircraft repossession from Russian airlines.",
        "type": "asset_seizure",
        "severity": "high",
        "trigger_entity": "Aeroflot",
        "parameters": {
            "aircraft_count": "500+",
            "lessor_countries": ["Ireland", "Bermuda", "Cayman"],
            "insurance_claims": "Active",
            "legal_proceedings": "Multiple jurisdictions",
        },
        "expected_impacts": [
            "Insurance market disruption",
            "Leasing contract restructuring",
            "Russian domestic aviation impact",
            "Parts cannibalization",
        ],
        "affected_sectors": ["Aviation", "Insurance", "Leasing"],
        "risk_multiplier": 1.8,
        "tags": ["AVIATION", "LEASING", "INSURANCE"],
    },

    # Technology Sector
    {
        "name": "Technology Sanctions Expansion",
        "description": "Expanded restrictions on technology exports to Russia.",
        "type": "export_control",
        "severity": "high",
        "trigger_entity": "Yandex",
        "parameters": {
            "technology_categories": ["Cloud", "AI/ML", "Quantum", "Cyber"],
            "license_policy": "Presumption of denial",
            "deemed_export_restrictions": True,
            "collaboration_ban": True,
        },
        "expected_impacts": [
            "Tech company isolation",
            "Talent flight acceleration",
            "Innovation capacity reduction",
            "Parallel import reliance",
        ],
        "affected_sectors": ["Technology", "Research", "Education"],
        "risk_multiplier": 1.7,
        "tags": ["TECHNOLOGY", "EXPORT_CONTROL", "AI"],
    },

    # Financial System Stress
    {
        "name": "Ruble Crisis Scenario",
        "description": "Major currency crisis triggered by sanctions escalation.",
        "type": "economic_stress",
        "severity": "critical",
        "trigger_entity": "Central Bank of Russia",
        "parameters": {
            "currency_depreciation": "40%",
            "capital_controls": "Enhanced",
            "interest_rate_response": "20%+",
            "foreign_reserve_access": "Limited",
        },
        "expected_impacts": [
            "Import cost surge",
            "Inflation acceleration",
            "Consumer spending collapse",
            "Corporate default risk",
        ],
        "affected_sectors": ["Banking", "Retail", "Manufacturing", "All"],
        "risk_multiplier": 2.5,
        "tags": ["CURRENCY", "ECONOMIC", "CRITICAL"],
    },

    # Comprehensive Scenario
    {
        "name": "Full Economic Isolation Scenario",
        "description": "Maximum pressure scenario with comprehensive sanctions enforcement.",
        "type": "comprehensive",
        "severity": "critical",
        "trigger_entity": None,
        "parameters": {
            "scope": "Economy-wide",
            "coordination": "G7 + partners",
            "enforcement": "Maximum",
            "secondary_sanctions": "Active",
            "timeline": "Accelerated",
        },
        "expected_impacts": [
            "GDP contraction 15-20%",
            "Trade volume reduction 60%",
            "Financial system isolation",
            "Technology degradation",
            "Brain drain acceleration",
        ],
        "affected_sectors": ["All"],
        "risk_multiplier": 3.0,
        "tags": ["COMPREHENSIVE", "MAXIMUM_PRESSURE", "CRITICAL"],
    },
]


def load_scenarios(tenant_id: str):
    """Load Russia sanctions scenarios."""
    print(f"\n{'='*70}")
    print(f"Loading {len(RUSSIA_SCENARIOS)} Russia Sanctions Scenarios...")
    print(f"{'='*70}")

    success = 0
    for scenario in RUSSIA_SCENARIOS:
        scenario_id = str(uuid.uuid4())

        # Get trigger entity ID if specified
        trigger_entity_id = None
        if scenario.get("trigger_entity"):
            trigger_entity_id = get_entity_id(tenant_id, scenario["trigger_entity"])

        # Build parameters JSON
        params = scenario.get("parameters", {})
        params["expected_impacts"] = scenario.get("expected_impacts", [])
        params["affected_sectors"] = scenario.get("affected_sectors", [])
        params["risk_multiplier"] = scenario.get("risk_multiplier", 1.0)
        params_json = json.dumps(params).replace("'", "''")

        tags = scenario.get("tags", ["RUSSIA"])
        tags_array = "ARRAY[" + ",".join([f"'{t}'" for t in tags]) + "]::varchar[]"

        trigger_ref = f"'{trigger_entity_id}'" if trigger_entity_id else "NULL"

        sql = f"""
        INSERT INTO scenarios (
            id, tenant_id, name, description, type, status,
            parameters, trigger_entity_id, tags,
            created_at, updated_at
        ) VALUES (
            '{scenario_id}',
            '{tenant_id}',
            '{escape_sql(scenario["name"])}',
            '{escape_sql(scenario.get("description", ""))}',
            '{scenario.get("type", "what_if")}',
            'draft',
            '{params_json}'::jsonb,
            {trigger_ref},
            {tags_array},
            NOW(),
            NOW()
        )
        ON CONFLICT DO NOTHING;
        """

        run_sql(sql)
        sev = scenario.get("severity", "medium")
        print(f"  [OK] [{sev.upper()[:4]:>4}] {scenario['name'][:55]}")
        success += 1

    return success


def main():
    print("=" * 70)
    print("CORTEX-CI Russia Sanctions Scenarios Loader")
    print("Pre-built Scenarios for Impact Simulation")
    print("=" * 70)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")

    total = load_scenarios(tenant_id)

    # Get final count
    result = run_sql(f"SELECT COUNT(*) FROM scenarios WHERE tenant_id = '{tenant_id}';")
    for line in result.split("\n"):
        if line.strip().isdigit():
            print(f"\n{'='*70}")
            print(f"Scenarios loaded: {total}")
            print(f"Total scenarios in database: {line.strip()}")
            print(f"{'='*70}")
            break


if __name__ == "__main__":
    main()
