#!/usr/bin/env python3
"""
Import sanctions data directly via psql.
Simpler approach that uses direct SQL.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
import subprocess
import uuid
from datetime import datetime

DATA_DIR = Path("/root/cortex-ci/data/sanctions")
OFAC_SDN_FILE = DATA_DIR / "ofac_sdn.xml"
UN_SANCTIONS_FILE = DATA_DIR / "un_sanctions.xml"

# DB connection
DB_CONTAINER = "compose-input-solid-state-array-q9m3z5-db-1"
DB_USER = "cortex"
DB_NAME = "cortex_ci"


def run_sql(sql: str):
    """Execute SQL in the database container."""
    cmd = [
        "docker", "exec", "-i", DB_CONTAINER,
        "psql", "-U", DB_USER, "-d", DB_NAME, "-c", sql
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SQL Error: {result.stderr}")
    return result.stdout


def get_tenant_id():
    """Get the default tenant ID."""
    result = run_sql("SELECT id FROM tenants WHERE slug = 'default';")
    for line in result.split('\n'):
        line = line.strip()
        if line and '-' in line and len(line) == 36:
            return line
    return None


def escape_sql(s: str) -> str:
    """Escape string for SQL."""
    if s is None:
        return ""
    return s.replace("'", "''").replace("\\", "\\\\")


def get_country_code(country_name: str) -> str:
    """Convert country name to ISO code."""
    country_map = {
        "cuba": "CU", "iran": "IR", "russia": "RU", "russian federation": "RU",
        "syria": "SY", "north korea": "KP", "venezuela": "VE", "belarus": "BY",
        "myanmar": "MM", "burma": "MM", "china": "CN", "united states": "US",
        "united kingdom": "GB", "germany": "DE", "france": "FR", "japan": "JP",
        "switzerland": "CH", "spain": "ES", "italy": "IT", "ukraine": "UA",
        "saudi arabia": "SA", "israel": "IL", "india": "IN", "pakistan": "PK",
        "afghanistan": "AF", "iraq": "IQ", "yemen": "YE", "libya": "LY",
    }
    if not country_name:
        return None
    return country_map.get(country_name.lower().strip())


def import_constraints(tenant_id: str):
    """Import sanctions constraints."""
    # Note: constrainttype enum: POLICY, REGULATION, COMPLIANCE, CONTRACTUAL, OPERATIONAL, FINANCIAL, SECURITY, CUSTOM
    constraints = [
        ("OFAC SDN Screening", "Entities on the OFAC Specially Designated Nationals list", "REGULATION", "CRITICAL", "OFAC-SDN"),
        ("EU Financial Sanctions", "EU restrictive measures against designated persons", "REGULATION", "CRITICAL", "EU-FSF"),
        ("UN Security Council Sanctions", "Mandatory UN Security Council sanctions", "REGULATION", "CRITICAL", "UN-SC"),
        ("Russia Sanctions Program", "Comprehensive sanctions targeting Russia", "REGULATION", "CRITICAL", "RUSSIA-EO"),
        ("Iran Sanctions Program", "Sanctions targeting Iran", "REGULATION", "CRITICAL", "IRAN-TRA"),
        ("North Korea Sanctions", "Comprehensive DPRK sanctions", "REGULATION", "CRITICAL", "DPRK-NKSR"),
        ("AML Requirements", "Anti-Money Laundering compliance", "COMPLIANCE", "HIGH", "AML-BSA"),
        ("FATF Compliance", "Financial Action Task Force standards", "COMPLIANCE", "HIGH", "FATF-40"),
    ]

    print("Importing constraints...")
    for name, desc, ctype, severity, ref_code in constraints:
        sql = f"""
        INSERT INTO constraints (id, tenant_id, name, description, type, severity, reference_code,
                                 applies_to_entity_types, applies_to_countries, applies_to_categories,
                                 risk_weight, is_mandatory, is_active, tags, requirements, custom_data,
                                 created_at, updated_at)
        SELECT '{uuid.uuid4()}', '{tenant_id}', '{escape_sql(name)}', '{escape_sql(desc)}',
               '{ctype}', '{severity}', '{ref_code}',
               ARRAY[]::varchar[], ARRAY[]::varchar[], ARRAY[]::varchar[],
               1.0, true, true, ARRAY['sanctions','compliance']::varchar[], '{{}}'::jsonb, '{{}}'::jsonb,
               NOW(), NOW()
        WHERE NOT EXISTS (
            SELECT 1 FROM constraints WHERE tenant_id = '{tenant_id}' AND reference_code = '{ref_code}'
        );
        """
        run_sql(sql)
    print("Constraints imported!")


def import_ofac_entities(tenant_id: str, limit: int = 500):
    """Import OFAC SDN entities."""
    if not OFAC_SDN_FILE.exists():
        print(f"OFAC file not found: {OFAC_SDN_FILE}")
        return

    print(f"Parsing OFAC SDN (limit: {limit})...")
    ns = {"sdn": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/XML"}

    tree = ET.parse(OFAC_SDN_FILE)
    root = tree.getroot()

    count = 0
    for entry in root.findall(".//sdn:sdnEntry", ns):
        if count >= limit:
            break

        uid = entry.find("sdn:uid", ns)
        last_name = entry.find("sdn:lastName", ns)
        first_name = entry.find("sdn:firstName", ns)
        sdn_type = entry.find("sdn:sdnType", ns)

        # Get programs
        programs = []
        program_list = entry.find("sdn:programList", ns)
        if program_list is not None:
            for prog in program_list.findall("sdn:program", ns):
                if prog.text:
                    programs.append(prog.text)

        # Get country
        country = None
        address_list = entry.find("sdn:addressList", ns)
        if address_list is not None:
            for addr in address_list.findall("sdn:address", ns):
                country_elem = addr.find("sdn:country", ns)
                if country_elem is not None and country_elem.text:
                    country = country_elem.text
                    break

        # Build name
        name_parts = []
        if first_name is not None and first_name.text:
            name_parts.append(first_name.text)
        if last_name is not None and last_name.text:
            name_parts.append(last_name.text)
        name = " ".join(name_parts) if name_parts else "Unknown"
        name = name[:500]

        # Entity type (enum: ORGANIZATION, INDIVIDUAL, LOCATION, FINANCIAL, VESSEL, AIRCRAFT, etc.)
        entity_type = "INDIVIDUAL"
        if sdn_type is not None and sdn_type.text:
            sdn_type_lower = sdn_type.text.lower()
            if sdn_type_lower == "entity":
                entity_type = "ORGANIZATION"
            elif sdn_type_lower == "vessel":
                entity_type = "VESSEL"
            elif sdn_type_lower == "aircraft":
                entity_type = "AIRCRAFT"

        external_id = f"OFAC-{uid.text}" if uid is not None and uid.text else None
        country_code = get_country_code(country) if country else None
        tags = programs[:3] if programs else []

        # Insert entity
        sql = f"""
        INSERT INTO entities (id, tenant_id, type, name, aliases, external_id, country_code,
                              category, subcategory, tags, criticality, is_active, notes,
                              custom_data, created_at, updated_at)
        SELECT '{uuid.uuid4()}', '{tenant_id}', '{entity_type}', '{escape_sql(name)}',
               ARRAY[]::varchar[], {f"'{external_id}'" if external_id else 'NULL'},
               {f"'{country_code}'" if country_code else 'NULL'},
               'sanctioned_entity', 'ofac_sdn',
               ARRAY[{','.join([f"'{escape_sql(t)}'" for t in tags])}]::varchar[],
               5, true, 'OFAC SDN Entry',
               '{{"source": "OFAC"}}'::jsonb, NOW(), NOW()
        WHERE NOT EXISTS (
            SELECT 1 FROM entities WHERE tenant_id = '{tenant_id}' AND external_id = '{external_id}'
        );
        """
        run_sql(sql)
        count += 1

        if count % 100 == 0:
            print(f"  Imported {count} OFAC entities...")

    print(f"Imported {count} OFAC entities")


def import_un_entities(tenant_id: str, limit: int = 300):
    """Import UN sanctions entities."""
    if not UN_SANCTIONS_FILE.exists():
        print(f"UN file not found: {UN_SANCTIONS_FILE}")
        return

    print(f"Parsing UN Sanctions (limit: {limit})...")

    tree = ET.parse(UN_SANCTIONS_FILE)
    root = tree.getroot()

    count = 0
    for elem in root.iter():
        if count >= limit:
            break

        if elem.tag.endswith("INDIVIDUAL") or elem.tag == "INDIVIDUAL":
            first_name = ""
            second_name = ""

            for child in elem:
                if "FIRST_NAME" in child.tag:
                    first_name = child.text or ""
                elif "SECOND_NAME" in child.tag:
                    second_name = child.text or ""

            name = f"{first_name} {second_name}".strip()
            if not name or len(name) < 2:
                continue

            dataid = elem.get("DATAID", str(uuid.uuid4())[:8])
            external_id = f"UN-{dataid}"

            sql = f"""
            INSERT INTO entities (id, tenant_id, type, name, aliases, external_id,
                                  category, subcategory, tags, criticality, is_active, notes,
                                  custom_data, created_at, updated_at)
            SELECT '{uuid.uuid4()}', '{tenant_id}', 'INDIVIDUAL', '{escape_sql(name[:500])}',
                   ARRAY[]::varchar[], '{external_id}',
                   'sanctioned_entity', 'un_consolidated',
                   ARRAY['UN_SANCTIONS']::varchar[],
                   5, true, 'UN Consolidated Sanctions',
                   '{{"source": "UN"}}'::jsonb, NOW(), NOW()
            WHERE NOT EXISTS (
                SELECT 1 FROM entities WHERE tenant_id = '{tenant_id}' AND external_id = '{external_id}'
            );
            """
            run_sql(sql)
            count += 1

        if count % 100 == 0 and count > 0:
            print(f"  Imported {count} UN entities...")

    print(f"Imported {count} UN entities")


def import_opensanctions(tenant_id: str, limit: int = 1000):
    """Import OpenSanctions entities."""
    opensanctions_file = DATA_DIR / "opensanctions_default.json"
    if not opensanctions_file.exists():
        print(f"OpenSanctions file not found: {opensanctions_file}")
        return

    print(f"Parsing OpenSanctions (limit: {limit})...")

    count = 0
    imported = 0

    with open(opensanctions_file, 'r') as f:
        for line in f:
            if imported >= limit:
                break

            try:
                record = json.loads(line.strip())
            except:
                continue

            # Only process Person, Company, Organization schemas
            schema = record.get("schema", "")
            if schema not in ["Person", "Company", "Organization", "LegalEntity"]:
                continue

            # Skip non-targets
            if not record.get("target", True):
                continue

            props = record.get("properties", {})
            names = props.get("name", [])
            if not names:
                continue

            name = names[0][:500] if names else "Unknown"
            external_id = record.get("id", "")[:255]

            # Determine entity type
            entity_type = "INDIVIDUAL" if schema == "Person" else "ORGANIZATION"

            # Get datasets as tags
            datasets = record.get("datasets", [])[:3]

            sql = f"""
            INSERT INTO entities (id, tenant_id, type, name, aliases, external_id,
                                  category, subcategory, tags, criticality, is_active, notes,
                                  custom_data, created_at, updated_at)
            SELECT '{uuid.uuid4()}', '{tenant_id}', '{entity_type}', '{escape_sql(name)}',
                   ARRAY[]::varchar[], '{escape_sql(external_id)}',
                   'sanctioned_entity', 'opensanctions',
                   ARRAY[{','.join([f"'{escape_sql(t)}'" for t in datasets])}]::varchar[],
                   5, true, 'OpenSanctions: {schema}',
                   '{{"source": "OpenSanctions", "schema": "{schema}"}}'::jsonb, NOW(), NOW()
            WHERE NOT EXISTS (
                SELECT 1 FROM entities WHERE tenant_id = '{tenant_id}' AND external_id = '{escape_sql(external_id)}'
            );
            """
            run_sql(sql)
            imported += 1
            count += 1

            if imported % 500 == 0:
                print(f"  Imported {imported} OpenSanctions entities...")

    print(f"Imported {imported} OpenSanctions entities")


def main():
    import sys

    print("=" * 60)
    print("CORTEX-CI Real Sanctions Data Import")
    print("=" * 60)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("Error: Could not find default tenant!")
        return

    print(f"Using tenant: {tenant_id}")

    # Parse command line args
    source = "all"
    limit = 5000

    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == "--source" and i + 1 < len(sys.argv):
                source = sys.argv[i + 1]
            if arg == "--limit" and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])

    print(f"Source: {source}, Limit: {limit}")

    # Import constraints (always)
    import_constraints(tenant_id)

    # Import entities based on source
    if source in ["ofac", "all"]:
        import_ofac_entities(tenant_id, limit=limit)

    if source in ["un", "all"]:
        import_un_entities(tenant_id, limit=min(limit, 1000))

    if source in ["opensanctions", "all"]:
        import_opensanctions(tenant_id, limit=limit)

    # Show final counts
    print("\n" + "=" * 60)
    print("Import Complete! Final counts:")
    print(run_sql("SELECT COUNT(*) as entities FROM entities;"))
    print(run_sql("SELECT COUNT(*) as constraints FROM constraints;"))
    print(run_sql("SELECT type, COUNT(*) FROM entities GROUP BY type;"))
    print("=" * 60)


if __name__ == "__main__":
    main()
