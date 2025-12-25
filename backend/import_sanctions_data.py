#!/usr/bin/env python3
"""
Import real sanctions data into CORTEX-CI database.

Data sources:
- OFAC SDN List (US Treasury): https://www.treasury.gov/ofac/downloads/sdn.xml
- OpenSanctions: https://data.opensanctions.org/datasets/latest/default/entities.ftm.json
- UN Consolidated Sanctions: https://scsanctions.un.org/resources/xml/en/consolidated.xml

Usage:
    python import_sanctions_data.py --source ofac --limit 1000
    python import_sanctions_data.py --source opensanctions --limit 5000
    python import_sanctions_data.py --source un --limit 500
    python import_sanctions_data.py --all --limit 2000
"""

import asyncio
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict, Any
from uuid import uuid4
import argparse
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import (
    Entity,
    Constraint,
    Tenant,
    EntityType,
    ConstraintType,
    ConstraintSeverity,
)


# Data file paths
DATA_DIR = Path(__file__).parent.parent / "data" / "sanctions"
OFAC_SDN_FILE = DATA_DIR / "ofac_sdn.xml"
OPENSANCTIONS_FILE = DATA_DIR / "opensanctions_default.json"
UN_SANCTIONS_FILE = DATA_DIR / "un_sanctions.xml"


def get_country_code(country_name: str) -> Optional[str]:
    """Convert country name to ISO 3166-1 alpha-2 code."""
    country_map = {
        "cuba": "CU",
        "iran": "IR",
        "russia": "RU",
        "russian federation": "RU",
        "syria": "SY",
        "syrian arab republic": "SY",
        "north korea": "KP",
        "korea, democratic people's republic of": "KP",
        "venezuela": "VE",
        "belarus": "BY",
        "myanmar": "MM",
        "burma": "MM",
        "zimbabwe": "ZW",
        "china": "CN",
        "hong kong": "HK",
        "united states": "US",
        "usa": "US",
        "united kingdom": "GB",
        "uk": "GB",
        "germany": "DE",
        "france": "FR",
        "japan": "JP",
        "switzerland": "CH",
        "spain": "ES",
        "italy": "IT",
        "netherlands": "NL",
        "belgium": "BE",
        "austria": "AT",
        "poland": "PL",
        "ukraine": "UA",
        "turkey": "TR",
        "saudi arabia": "SA",
        "uae": "AE",
        "united arab emirates": "AE",
        "israel": "IL",
        "india": "IN",
        "pakistan": "PK",
        "afghanistan": "AF",
        "iraq": "IQ",
        "lebanon": "LB",
        "yemen": "YE",
        "libya": "LY",
        "sudan": "SD",
        "south sudan": "SS",
        "somalia": "SO",
        "eritrea": "ER",
        "ethiopia": "ET",
        "mali": "ML",
        "central african republic": "CF",
        "congo": "CD",
        "drc": "CD",
    }
    if not country_name:
        return None
    return country_map.get(country_name.lower().strip())


def parse_ofac_sdn(limit: int = 1000) -> List[Dict[str, Any]]:
    """Parse OFAC SDN XML file."""
    if not OFAC_SDN_FILE.exists():
        print(f"OFAC SDN file not found: {OFAC_SDN_FILE}")
        return []

    print(f"Parsing OFAC SDN from {OFAC_SDN_FILE}...")

    # Define namespace
    ns = {
        "sdn": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/XML"
    }

    tree = ET.parse(OFAC_SDN_FILE)
    root = tree.getroot()

    entities = []
    count = 0

    for entry in root.findall(".//sdn:sdnEntry", ns):
        if count >= limit:
            break

        uid = entry.find("sdn:uid", ns)
        last_name = entry.find("sdn:lastName", ns)
        first_name = entry.find("sdn:firstName", ns)
        sdn_type = entry.find("sdn:sdnType", ns)

        # Get programs (sanctions programs)
        programs = []
        program_list = entry.find("sdn:programList", ns)
        if program_list is not None:
            for prog in program_list.findall("sdn:program", ns):
                if prog.text:
                    programs.append(prog.text)

        # Get aliases
        aliases = []
        aka_list = entry.find("sdn:akaList", ns)
        if aka_list is not None:
            for aka in aka_list.findall("sdn:aka", ns):
                aka_name = aka.find("sdn:lastName", ns)
                if aka_name is not None and aka_name.text:
                    aliases.append(aka_name.text)

        # Get address/country
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

        # Determine entity type
        entity_type = EntityType.PERSON
        if sdn_type is not None and sdn_type.text:
            if sdn_type.text.lower() == "entity":
                entity_type = EntityType.ORGANIZATION
            elif sdn_type.text.lower() == "vessel":
                entity_type = EntityType.ORGANIZATION
            elif sdn_type.text.lower() == "aircraft":
                entity_type = EntityType.ORGANIZATION

        entities.append(
            {
                "external_id": f"OFAC-{uid.text}" if uid is not None else None,
                "name": name,
                "type": entity_type,
                "aliases": aliases[:10],  # Limit aliases
                "country_code": get_country_code(country) if country else None,
                "category": "sanctioned_entity",
                "subcategory": "ofac_sdn",
                "tags": programs[:5],  # Sanctions programs as tags
                "criticality": 5,  # High criticality for sanctioned entities
                "notes": f"OFAC SDN Entry. Programs: {', '.join(programs[:3])}",
                "source": "OFAC",
            }
        )
        count += 1

    print(f"Parsed {len(entities)} entities from OFAC SDN")
    return entities


def parse_opensanctions(limit: int = 1000) -> List[Dict[str, Any]]:
    """Parse OpenSanctions JSON Lines file."""
    if not OPENSANCTIONS_FILE.exists():
        print(f"OpenSanctions file not found: {OPENSANCTIONS_FILE}")
        return []

    print(f"Parsing OpenSanctions from {OPENSANCTIONS_FILE}...")

    entities = []
    count = 0

    with open(OPENSANCTIONS_FILE, "r") as f:
        for line in f:
            if count >= limit:
                break

            try:
                record = json.loads(line.strip())
            except json.JSONDecodeError:
                continue

            # Only process Person, Company, Organization schemas
            schema = record.get("schema", "")
            if schema not in ["Person", "Company", "Organization", "LegalEntity"]:
                continue

            # Skip non-targets (auxiliary data)
            if not record.get("target", True):
                continue

            props = record.get("properties", {})

            # Get name
            names = props.get("name", [])
            if not names:
                continue
            name = names[0] if names else "Unknown"

            # Get aliases
            aliases = props.get("alias", [])[:10]

            # Get country
            countries = props.get("country", [])
            country_code = countries[0] if countries else None
            if country_code and len(country_code) > 2:
                country_code = get_country_code(country_code)

            # Determine entity type
            entity_type = (
                EntityType.PERSON if schema == "Person" else EntityType.ORGANIZATION
            )

            # Get datasets as tags
            datasets = record.get("datasets", [])[:5]

            entities.append(
                {
                    "external_id": record.get("id"),
                    "name": name[:500],
                    "type": entity_type,
                    "aliases": aliases,
                    "country_code": country_code[:3] if country_code else None,
                    "category": "sanctioned_entity",
                    "subcategory": "opensanctions",
                    "tags": datasets,
                    "criticality": 5,
                    "notes": f"OpenSanctions ID: {record.get('id')}. Schema: {schema}",
                    "source": "OpenSanctions",
                }
            )
            count += 1

    print(f"Parsed {len(entities)} entities from OpenSanctions")
    return entities


def parse_un_sanctions(limit: int = 500) -> List[Dict[str, Any]]:
    """Parse UN Consolidated Sanctions XML file."""
    if not UN_SANCTIONS_FILE.exists():
        print(f"UN Sanctions file not found: {UN_SANCTIONS_FILE}")
        return []

    print(f"Parsing UN Sanctions from {UN_SANCTIONS_FILE}...")

    tree = ET.parse(UN_SANCTIONS_FILE)
    root = tree.getroot()

    entities = []
    count = 0

    # Try to find individuals and entities
    for individual in root.iter():
        if count >= limit:
            break

        if individual.tag.endswith("INDIVIDUAL") or individual.tag == "INDIVIDUAL":
            # Get name components
            first_name = ""
            second_name = ""
            third_name = ""

            for child in individual:
                if child.tag.endswith("FIRST_NAME") or child.tag == "FIRST_NAME":
                    first_name = child.text or ""
                elif child.tag.endswith("SECOND_NAME") or child.tag == "SECOND_NAME":
                    second_name = child.text or ""
                elif child.tag.endswith("THIRD_NAME") or child.tag == "THIRD_NAME":
                    third_name = child.text or ""

            name = " ".join([first_name, second_name, third_name]).strip()
            if not name:
                continue

            # Get reference number
            dataid = individual.get("DATAID", "")

            entities.append(
                {
                    "external_id": f"UN-{dataid}" if dataid else None,
                    "name": name[:500],
                    "type": EntityType.PERSON,
                    "aliases": [],
                    "country_code": None,
                    "category": "sanctioned_entity",
                    "subcategory": "un_consolidated",
                    "tags": ["UN_SANCTIONS"],
                    "criticality": 5,
                    "notes": "UN Consolidated Sanctions List",
                    "source": "UN",
                }
            )
            count += 1

        elif individual.tag.endswith("ENTITY") or individual.tag == "ENTITY":
            # Get entity name
            name = ""
            for child in individual:
                if child.tag.endswith("FIRST_NAME") or child.tag == "FIRST_NAME":
                    name = child.text or ""
                    break

            if not name:
                continue

            dataid = individual.get("DATAID", "")

            entities.append(
                {
                    "external_id": f"UN-{dataid}" if dataid else None,
                    "name": name[:500],
                    "type": EntityType.ORGANIZATION,
                    "aliases": [],
                    "country_code": None,
                    "category": "sanctioned_entity",
                    "subcategory": "un_consolidated",
                    "tags": ["UN_SANCTIONS"],
                    "criticality": 5,
                    "notes": "UN Consolidated Sanctions List",
                    "source": "UN",
                }
            )
            count += 1

    print(f"Parsed {len(entities)} entities from UN Sanctions")
    return entities


def create_sanctions_constraints() -> List[Dict[str, Any]]:
    """Create constraint records for sanctions programs."""
    constraints = [
        {
            "name": "OFAC SDN Screening",
            "description": "Entities on the OFAC Specially Designated Nationals list are prohibited from conducting business with US persons.",
            "type": ConstraintType.SANCTION,
            "severity": ConstraintSeverity.CRITICAL,
            "reference_code": "OFAC-SDN",
            "source_document": "31 CFR Part 500-599",
            "external_url": "https://ofac.treasury.gov/specially-designated-nationals-list-sdn-list",
            "applies_to_countries": ["US"],
            "is_mandatory": True,
            "risk_weight": 1.0,
        },
        {
            "name": "EU Financial Sanctions",
            "description": "Restrictive measures against designated persons and entities under EU Common Foreign and Security Policy.",
            "type": ConstraintType.SANCTION,
            "severity": ConstraintSeverity.CRITICAL,
            "reference_code": "EU-FSF",
            "source_document": "EU Council Regulations",
            "external_url": "https://www.sanctionsmap.eu/",
            "applies_to_countries": ["EU"],
            "is_mandatory": True,
            "risk_weight": 1.0,
        },
        {
            "name": "UN Security Council Sanctions",
            "description": "Mandatory sanctions imposed by the UN Security Council under Chapter VII of the UN Charter.",
            "type": ConstraintType.SANCTION,
            "severity": ConstraintSeverity.CRITICAL,
            "reference_code": "UN-SC-SANCTIONS",
            "source_document": "UN Security Council Resolutions",
            "external_url": "https://scsanctions.un.org/",
            "applies_to_countries": [],
            "is_mandatory": True,
            "risk_weight": 1.0,
        },
        {
            "name": "Russia Sanctions Program",
            "description": "Comprehensive sanctions targeting Russian government, oligarchs, and key sectors.",
            "type": ConstraintType.SANCTION,
            "severity": ConstraintSeverity.CRITICAL,
            "reference_code": "RUSSIA-EO",
            "source_document": "Executive Orders 13660, 13661, 13662, 13685, 14024",
            "external_url": "https://ofac.treasury.gov/sanctions-programs-and-country-information/ukraine-russia-related-sanctions",
            "applies_to_countries": ["RU"],
            "is_mandatory": True,
            "risk_weight": 1.0,
        },
        {
            "name": "Iran Sanctions Program",
            "description": "Sanctions targeting Iran's nuclear program, terrorism support, and human rights abuses.",
            "type": ConstraintType.SANCTION,
            "severity": ConstraintSeverity.CRITICAL,
            "reference_code": "IRAN-TRA",
            "source_document": "Iran Transactions and Sanctions Regulations",
            "external_url": "https://ofac.treasury.gov/sanctions-programs-and-country-information/iran-sanctions",
            "applies_to_countries": ["IR"],
            "is_mandatory": True,
            "risk_weight": 1.0,
        },
        {
            "name": "North Korea Sanctions Program",
            "description": "Comprehensive sanctions targeting North Korea's weapons programs.",
            "type": ConstraintType.SANCTION,
            "severity": ConstraintSeverity.CRITICAL,
            "reference_code": "DPRK-NKSR",
            "source_document": "North Korea Sanctions Regulations",
            "external_url": "https://ofac.treasury.gov/sanctions-programs-and-country-information/north-korea-sanctions",
            "applies_to_countries": ["KP"],
            "is_mandatory": True,
            "risk_weight": 1.0,
        },
        {
            "name": "Anti-Money Laundering Requirements",
            "description": "Customer due diligence and transaction monitoring requirements under AML regulations.",
            "type": ConstraintType.REGULATION,
            "severity": ConstraintSeverity.HIGH,
            "reference_code": "AML-BSA",
            "source_document": "Bank Secrecy Act, AML Act of 2020",
            "external_url": "https://www.fincen.gov/resources/statutes-and-regulations",
            "applies_to_countries": ["US"],
            "is_mandatory": True,
            "risk_weight": 0.8,
        },
        {
            "name": "FATF Recommendations Compliance",
            "description": "International standards on combating money laundering and terrorist financing.",
            "type": ConstraintType.REGULATION,
            "severity": ConstraintSeverity.HIGH,
            "reference_code": "FATF-40",
            "source_document": "FATF Recommendations",
            "external_url": "https://www.fatf-gafi.org/recommendations.html",
            "applies_to_countries": [],
            "is_mandatory": True,
            "risk_weight": 0.8,
        },
    ]
    return constraints


async def import_data(source: str = "all", limit: int = 1000, dry_run: bool = False):
    """Import sanctions data into CORTEX-CI database."""

    # Parse data based on source
    all_entities = []

    if source in ["ofac", "all"]:
        all_entities.extend(parse_ofac_sdn(limit))

    if source in ["opensanctions", "all"]:
        all_entities.extend(parse_opensanctions(limit))

    if source in ["un", "all"]:
        all_entities.extend(parse_un_sanctions(limit))

    constraints = create_sanctions_constraints()

    print(f"\nTotal entities to import: {len(all_entities)}")
    print(f"Total constraints to import: {len(constraints)}")

    if dry_run:
        print("\n[DRY RUN] Would import the following:")
        for e in all_entities[:5]:
            print(f"  - {e['name']} ({e['type']}) from {e['source']}")
        if len(all_entities) > 5:
            print(f"  ... and {len(all_entities) - 5} more entities")
        return

    # Connect to database
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Get default tenant
        result = await db.execute(select(Tenant).where(Tenant.slug == "default"))
        tenant = result.scalar_one_or_none()

        if not tenant:
            print("Error: Default tenant not found!")
            return

        print(f"\nImporting to tenant: {tenant.name} ({tenant.id})")

        # Import constraints first
        print("\nImporting constraints...")
        constraint_count = 0
        for c in constraints:
            # Check if exists
            existing = await db.execute(
                select(Constraint).where(
                    Constraint.tenant_id == tenant.id,
                    Constraint.reference_code == c["reference_code"],
                )
            )
            if existing.scalar_one_or_none():
                print(f"  Skipping existing constraint: {c['name']}")
                continue

            constraint = Constraint(
                id=uuid4(),
                tenant_id=tenant.id,
                name=c["name"],
                description=c["description"],
                type=c["type"],
                severity=c["severity"],
                reference_code=c["reference_code"],
                source_document=c["source_document"],
                external_url=c["external_url"],
                applies_to_entity_types=[],
                applies_to_countries=c["applies_to_countries"],
                applies_to_categories=[],
                risk_weight=c["risk_weight"],
                is_mandatory=c["is_mandatory"],
                is_active=True,
                tags=["sanctions", "compliance"],
                requirements={},
                custom_data={},
            )
            db.add(constraint)
            constraint_count += 1

        await db.commit()
        print(f"Imported {constraint_count} constraints")

        # Import entities
        print("\nImporting entities...")
        entity_count = 0
        batch_size = 100

        for i, e in enumerate(all_entities):
            # Check if exists by external_id
            if e.get("external_id"):
                existing = await db.execute(
                    select(Entity).where(
                        Entity.tenant_id == tenant.id,
                        Entity.external_id == e["external_id"],
                    )
                )
                if existing.scalar_one_or_none():
                    continue

            entity = Entity(
                id=uuid4(),
                tenant_id=tenant.id,
                type=e["type"],
                name=e["name"],
                aliases=e.get("aliases", []),
                external_id=e.get("external_id"),
                country_code=e.get("country_code"),
                category=e.get("category"),
                subcategory=e.get("subcategory"),
                tags=e.get("tags", []),
                criticality=e.get("criticality", 3),
                notes=e.get("notes"),
                is_active=True,
                custom_data={"source": e.get("source", "unknown")},
            )
            db.add(entity)
            entity_count += 1

            # Commit in batches
            if entity_count % batch_size == 0:
                await db.commit()
                print(f"  Imported {entity_count} entities...")

        await db.commit()
        print(
            f"\nTotal imported: {entity_count} entities, {constraint_count} constraints"
        )

    await engine.dispose()
    print("\nImport complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import sanctions data into CORTEX-CI")
    parser.add_argument(
        "--source",
        choices=["ofac", "opensanctions", "un", "all"],
        default="all",
        help="Data source to import",
    )
    parser.add_argument(
        "--limit", type=int, default=1000, help="Maximum entities to import per source"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse data without importing"
    )

    args = parser.parse_args()

    asyncio.run(import_data(source=args.source, limit=args.limit, dry_run=args.dry_run))
