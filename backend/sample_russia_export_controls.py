#!/usr/bin/env python3
"""
Russia Export Controls & Dual-Use Goods for CORTEX-CI.
Comprehensive tracking of export control restrictions to Russia.

Covers:
- Dual-use goods categories
- Military end-use restrictions
- Technology transfer controls
- Semiconductor restrictions
- Machine tool controls
- Quantum computing restrictions

Run: python3 sample_russia_export_controls.py
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
# EXPORT CONTROL CATEGORIES (EAR/CCL)
# ============================================================================
EXPORT_CONTROL_CONSTRAINTS = [
    # Semiconductors & Electronics
    {
        "name": "Advanced Semiconductors Export Control (Russia)",
        "type": "export_control",
        "severity": "critical",
        "description": "Restrictions on advanced semiconductors and integrated circuits to Russia",
        "source_document": "BIS Final Rule - Russia Semiconductor Controls",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/russia-belarus",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "SEMICONDUCTORS", "ELECTRONICS", "CRITICAL"],
        "eccn_codes": ["3A001", "3A002", "3A991", "3A992"],
    },
    {
        "name": "FPGA and Programmable Logic Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on field-programmable gate arrays and programmable logic devices",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "FPGA", "ELECTRONICS", "CRITICAL"],
        "eccn_codes": ["3A001.a.7", "3A001.a.9"],
    },
    {
        "name": "Memory Devices Export Control",
        "type": "export_control",
        "severity": "high",
        "description": "Controls on advanced memory chips (DRAM, NAND, etc.)",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["EXPORT_CONTROL", "MEMORY", "ELECTRONICS"],
        "eccn_codes": ["3A001.a.3", "3A991"],
    },
    # Computing & Quantum
    {
        "name": "Quantum Computing Technology Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on quantum computing hardware, software, and technology",
        "source_document": "BIS Emerging Technologies Controls",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/russia-belarus",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "QUANTUM", "EMERGING_TECH", "CRITICAL"],
        "eccn_codes": ["3A090", "3D001", "3E001"],
    },
    {
        "name": "High-Performance Computing Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on supercomputers and high-performance computing systems",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "HPC", "COMPUTING", "CRITICAL"],
        "eccn_codes": ["4A003", "4A004", "4D001", "4E001"],
    },
    {
        "name": "AI and Machine Learning Export Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on artificial intelligence and machine learning technology",
        "source_document": "BIS AI/ML Controls",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/russia-belarus",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "AI", "ML", "EMERGING_TECH", "CRITICAL"],
        "eccn_codes": ["4D090", "4E090"],
    },
    # Manufacturing Equipment
    {
        "name": "Semiconductor Manufacturing Equipment",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on equipment for semiconductor fabrication",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "SME", "MANUFACTURING", "CRITICAL"],
        "eccn_codes": ["3B001", "3B002", "3B991", "3B992"],
    },
    {
        "name": "Advanced Machine Tools Export Control",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on CNC machine tools and precision manufacturing equipment",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "MACHINE_TOOLS", "CNC", "MANUFACTURING", "CRITICAL"],
        "eccn_codes": ["2B001", "2B002", "2B003"],
    },
    {
        "name": "Additive Manufacturing Equipment Controls",
        "type": "export_control",
        "severity": "high",
        "description": "Controls on 3D printing and additive manufacturing for metal parts",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["EXPORT_CONTROL", "3D_PRINTING", "ADDITIVE_MFG"],
        "eccn_codes": ["2B999"],
    },
    # Aerospace & Defense
    {
        "name": "Aerospace-Grade Materials Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on carbon fiber, titanium, and aerospace alloys",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "AEROSPACE", "MATERIALS", "CRITICAL"],
        "eccn_codes": ["1C010", "1C210", "1A002"],
    },
    {
        "name": "Inertial Navigation Systems Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on inertial navigation and guidance systems",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "NAVIGATION", "GUIDANCE", "DEFENSE", "CRITICAL"],
        "eccn_codes": ["7A003", "7A103", "7D001", "7E001"],
    },
    {
        "name": "Drone/UAV Component Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on unmanned aerial vehicle components and technology",
        "source_document": "BIS Russia UAV Controls",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/russia-belarus",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "UAV", "DRONES", "DEFENSE", "CRITICAL"],
        "eccn_codes": ["9A012", "9A612", "9D001", "9E001"],
    },
    {
        "name": "Night Vision and Thermal Imaging",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on night vision, thermal imaging, and image intensifiers",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "NIGHT_VISION", "THERMAL", "DEFENSE", "CRITICAL"],
        "eccn_codes": ["6A002", "6A003", "6D003"],
    },
    # Communications & Encryption
    {
        "name": "Encryption Technology Controls",
        "type": "export_control",
        "severity": "high",
        "description": "Controls on encryption software and hardware",
        "source_document": "BIS EAR Cat 5",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["EXPORT_CONTROL", "ENCRYPTION", "CYBERSECURITY"],
        "eccn_codes": ["5A002", "5D002", "5E002"],
    },
    {
        "name": "Telecommunications Equipment Controls",
        "type": "export_control",
        "severity": "high",
        "description": "Controls on advanced telecommunications equipment",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.5,
        "tags": ["EXPORT_CONTROL", "TELECOM", "COMMUNICATIONS"],
        "eccn_codes": ["5A001", "5B001", "5D001"],
    },
    # Marine & Underwater
    {
        "name": "Underwater/Marine Technology Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on underwater systems, sonar, and marine technology",
        "source_document": "BIS EAR",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "MARINE", "UNDERWATER", "SONAR", "CRITICAL"],
        "eccn_codes": ["8A001", "8A002", "8D001"],
    },
    # Nuclear Related
    {
        "name": "Nuclear Related Technology Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on nuclear-related dual-use equipment and technology",
        "source_document": "BIS NRC Controls",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "NUCLEAR", "DUAL_USE", "CRITICAL"],
        "eccn_codes": ["0A001", "0B001", "0C001", "0D001", "0E001"],
    },
    # Biological & Chemical
    {
        "name": "Chemical/Biological Equipment Controls",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on equipment usable for chemical/biological weapons",
        "source_document": "BIS EAR CWC/BWC",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "CHEMICAL", "BIOLOGICAL", "WMD", "CRITICAL"],
        "eccn_codes": ["1C350", "1C351", "2B350", "2B351"],
    },
]

# ============================================================================
# MILITARY END-USE CONTROLS
# ============================================================================
MILITARY_END_USE = [
    {
        "name": "Russia Military End-Use (MEU) Rule",
        "type": "export_control",
        "severity": "critical",
        "description": "Comprehensive controls on items for military end-use in Russia",
        "source_document": "15 CFR 744.21",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/russia-belarus",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "MEU", "MILITARY", "CRITICAL"],
    },
    {
        "name": "Russia Military End-User (MEU) List",
        "type": "export_control",
        "severity": "critical",
        "description": "List of Russian military end-users subject to license requirements",
        "source_document": "Supplement No. 4 to Part 744",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern/entity-list",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "MEU_LIST", "MILITARY", "CRITICAL"],
    },
    {
        "name": "Russia Foreign Direct Product Rule",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on foreign-produced items made with US technology destined for Russia",
        "source_document": "15 CFR 734.9",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/russia-belarus",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "FDPR", "EXTRATERRITORIAL", "CRITICAL"],
    },
    {
        "name": "Entity List - Russia",
        "type": "export_control",
        "severity": "critical",
        "description": "Russian entities subject to specific license requirements",
        "source_document": "Supplement No. 4 to Part 744",
        "external_url": "https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern/entity-list",
        "applies_to_countries": ["RU"],
        "risk_weight": 5.0,
        "tags": ["EXPORT_CONTROL", "ENTITY_LIST", "BIS", "CRITICAL"],
    },
]

# ============================================================================
# LUXURY GOODS BAN
# ============================================================================
LUXURY_GOODS_BAN = [
    {
        "name": "Luxury Goods Export Ban to Russia",
        "type": "trade_restriction",
        "severity": "high",
        "description": "Ban on export of luxury goods exceeding thresholds to Russia",
        "source_document": "Executive Order 14068",
        "external_url": "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/russian-harmful-foreign-activities-sanctions",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.0,
        "tags": ["TRADE", "LUXURY_GOODS", "EXPORT_BAN"],
    },
    {
        "name": "High-End Vehicles Export Ban",
        "type": "trade_restriction",
        "severity": "high",
        "description": "Ban on export of vehicles over $50,000 to Russia",
        "source_document": "EU Regulation 2022/328",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0328",
        "applies_to_countries": ["RU"],
        "risk_weight": 4.0,
        "tags": ["TRADE", "VEHICLES", "LUXURY", "EXPORT_BAN"],
    },
    {
        "name": "Jewelry and Precious Metals Ban",
        "type": "trade_restriction",
        "severity": "medium",
        "description": "Ban on export of jewelry and precious metals over thresholds",
        "source_document": "EU Regulation 2022/328",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0328",
        "applies_to_countries": ["RU"],
        "risk_weight": 3.5,
        "tags": ["TRADE", "JEWELRY", "LUXURY", "EXPORT_BAN"],
    },
    {
        "name": "High-End Electronics Consumer Ban",
        "type": "trade_restriction",
        "severity": "medium",
        "description": "Ban on export of high-end consumer electronics to Russia",
        "source_document": "EU Regulation 2022/328",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0328",
        "applies_to_countries": ["RU"],
        "risk_weight": 3.0,
        "tags": ["TRADE", "ELECTRONICS", "LUXURY", "EXPORT_BAN"],
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

        # Include ECCN codes in custom_data
        custom_data = {}
        if "eccn_codes" in constraint:
            custom_data["eccn_codes"] = constraint["eccn_codes"]
        custom_data_json = json.dumps(custom_data).replace("'", "''")

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
            '{custom_data_json}'::jsonb,
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
    print("CORTEX-CI Russia Export Controls & Dual-Use Goods")
    print("Comprehensive Technology Transfer Restrictions")
    print("=" * 70)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")

    total = 0
    total += load_constraints(tenant_id, EXPORT_CONTROL_CONSTRAINTS, "Export Control Categories")
    total += load_constraints(tenant_id, MILITARY_END_USE, "Military End-Use Rules")
    total += load_constraints(tenant_id, LUXURY_GOODS_BAN, "Luxury Goods Restrictions")

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
