"""
MITRE ATT&CK Framework Import Script
Downloads and imports MITRE ATT&CK Enterprise techniques from the official STIX data repository.

Usage:
    docker compose exec -w /app backend python scripts/import_mitre.py
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import httpx
from uuid import uuid4
from datetime import date
from typing import Optional, Dict, List

from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal
from app.models import Tenant
from app.models.compliance.framework import (
    Framework, Control, FrameworkType, ControlCategory
)

# MITRE ATT&CK STIX Data URL (Enterprise Matrix)
MITRE_ATTACK_URL = "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json"

# Map ATT&CK tactics to our control categories
TACTIC_TO_CATEGORY = {
    "reconnaissance": ControlCategory.RISK_ASSESSMENT,
    "resource-development": ControlCategory.SUPPLY_CHAIN,
    "initial-access": ControlCategory.ACCESS_CONTROL,
    "execution": ControlCategory.VULNERABILITY_MANAGEMENT,
    "persistence": ControlCategory.CONFIGURATION_MANAGEMENT,
    "privilege-escalation": ControlCategory.ACCESS_CONTROL,
    "defense-evasion": ControlCategory.VULNERABILITY_MANAGEMENT,
    "credential-access": ControlCategory.IDENTIFICATION_AUTHENTICATION,
    "discovery": ControlCategory.AUDIT_LOGGING,
    "lateral-movement": ControlCategory.COMMUNICATIONS,
    "collection": ControlCategory.DATA_PROTECTION,
    "command-and-control": ControlCategory.COMMUNICATIONS,
    "exfiltration": ControlCategory.DATA_PROTECTION,
    "impact": ControlCategory.BUSINESS_CONTINUITY,
}


def extract_external_id(obj: dict) -> Optional[str]:
    """Extract external reference ID (T####) from STIX object."""
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")
    return None


def extract_url(obj: dict) -> Optional[str]:
    """Extract MITRE ATT&CK URL from STIX object."""
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("url")
    return None


def get_tactic_shortname(tactic_ref: str) -> str:
    """Extract tactic shortname from kill-chain-phase reference."""
    # tactic_ref format: "mitre-attack:tactic-name"
    return tactic_ref.split(":")[-1] if ":" in tactic_ref else tactic_ref


def parse_techniques(stix_data: dict) -> tuple:
    """Parse STIX data into techniques, tactics, and mitigations."""
    techniques = []
    tactics = {}
    mitigations = {}
    relationships = []

    for obj in stix_data.get("objects", []):
        obj_type = obj.get("type")

        if obj_type == "attack-pattern" and not obj.get("revoked", False):
            # This is a technique
            techniques.append(obj)

        elif obj_type == "x-mitre-tactic":
            # This is a tactic
            shortname = obj.get("x_mitre_shortname")
            if shortname:
                tactics[shortname] = obj

        elif obj_type == "course-of-action" and not obj.get("revoked", False):
            # This is a mitigation
            mitigations[obj.get("id")] = obj

        elif obj_type == "relationship" and obj.get("relationship_type") == "mitigates":
            # Mitigation relationship
            relationships.append(obj)

    return techniques, tactics, mitigations, relationships


async def fetch_mitre_data() -> dict:
    """Download MITRE ATT&CK STIX data."""
    print(f"Downloading MITRE ATT&CK Enterprise data...")
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(MITRE_ATTACK_URL)
        response.raise_for_status()
        return response.json()


async def import_mitre_attack():
    """Import MITRE ATT&CK framework from STIX data."""

    # Fetch the STIX data
    stix_data = await fetch_mitre_data()

    # Parse the data
    techniques, tactics, mitigations, relationships = parse_techniques(stix_data)

    print(f"Found {len(techniques)} techniques, {len(tactics)} tactics, {len(mitigations)} mitigations")

    # Build technique -> mitigations mapping
    technique_mitigations: Dict[str, List[str]] = {}
    for rel in relationships:
        source_id = rel.get("source_ref")
        target_id = rel.get("target_ref")
        if source_id in mitigations and target_id:
            if target_id not in technique_mitigations:
                technique_mitigations[target_id] = []
            mitigation_obj = mitigations[source_id]
            mit_id = extract_external_id(mitigation_obj)
            if mit_id:
                technique_mitigations[target_id].append(mit_id)

    async with AsyncSessionLocal() as session:
        # Get the first tenant
        result = await session.execute(select(Tenant))
        tenant = result.scalars().first()

        if not tenant:
            print("No tenant found. Creating default tenant...")
            tenant = Tenant(
                id=uuid4(),
                name="Default Organization",
                slug="default"
            )
            session.add(tenant)
            await session.commit()

        tenant_id = tenant.id
        print(f"Using tenant: {tenant.name} ({tenant_id})")

        # Check if MITRE ATT&CK framework already exists
        existing_framework = await session.execute(
            select(Framework).where(
                Framework.tenant_id == tenant_id,
                Framework.type == FrameworkType.MITRE_ATTACK
            )
        )
        existing = existing_framework.scalars().first()

        if existing:
            print(f"MITRE ATT&CK framework already exists. Deleting and recreating...")
            await session.execute(
                delete(Control).where(Control.framework_id == existing.id)
            )
            await session.delete(existing)
            await session.commit()

        # Create the framework
        framework = Framework(
            id=uuid4(),
            tenant_id=tenant_id,
            type=FrameworkType.MITRE_ATTACK,
            name="MITRE ATT&CK Enterprise",
            version="v15.0",
            description="MITRE ATT&CK is a globally-accessible knowledge base of adversary tactics and techniques based on real-world observations.",
            source_url="https://attack.mitre.org/",
            publisher="The MITRE Corporation",
            publication_date=date(2024, 10, 31),  # v15.0 release date
            is_active=True,
            is_custom=False,
        )
        session.add(framework)

        # Process techniques by tactic
        total_controls = 0
        categories_used = set()
        tactic_counts = {}

        print(f"\nImporting techniques by tactic...")

        for technique in techniques:
            technique_id = extract_external_id(technique)
            if not technique_id:
                continue

            name = technique.get("name", "")
            description = technique.get("description", "")
            url = extract_url(technique)

            # Get tactics for this technique
            kill_chain_phases = technique.get("kill_chain_phases", [])
            technique_tactics = []
            primary_category = ControlCategory.VULNERABILITY_MANAGEMENT

            for phase in kill_chain_phases:
                if phase.get("kill_chain_name") == "mitre-attack":
                    tactic_name = phase.get("phase_name", "")
                    technique_tactics.append(tactic_name)

                    # Use first tactic's category as primary
                    if tactic_name in TACTIC_TO_CATEGORY:
                        primary_category = TACTIC_TO_CATEGORY[tactic_name]
                        break

            categories_used.add(primary_category.value if hasattr(primary_category, 'value') else primary_category)

            # Get tactic display name
            tactic_display = technique_tactics[0] if technique_tactics else "Unknown"
            tactic_display = tactic_display.replace("-", " ").title()

            if tactic_display not in tactic_counts:
                tactic_counts[tactic_display] = 0
            tactic_counts[tactic_display] += 1

            # Get platforms
            platforms = technique.get("x_mitre_platforms", [])

            # Get data sources
            data_sources = technique.get("x_mitre_data_sources", [])

            # Get mitigations for this technique
            stix_id = technique.get("id")
            technique_mit_ids = technique_mitigations.get(stix_id, [])

            # Check if this is a sub-technique
            is_subtechnique = technique.get("x_mitre_is_subtechnique", False)
            parent_id = None

            if is_subtechnique and "." in technique_id:
                parent_tech_id = technique_id.split(".")[0]
                # We'll link parents after creating all controls

            # Determine priority based on detection difficulty
            detection = technique.get("x_mitre_detection", "")
            priority = 2  # Default moderate
            if any(word in description.lower() for word in ["difficult", "hard", "advanced", "sophisticated"]):
                priority = 1  # High priority (harder to detect)
            elif any(word in description.lower() for word in ["easily", "simple", "basic"]):
                priority = 3  # Lower priority (easier to detect)

            # Create control
            control = Control(
                id=uuid4(),
                tenant_id=tenant_id,
                framework_id=framework.id,
                control_id=technique_id,
                title=name,
                description=description[:4000] if description else f"Technique {technique_id}",
                family=tactic_display,
                category=primary_category,
                guidance=detection[:2000] if detection else None,
                baseline_impact="HIGH",  # ATT&CK techniques are inherently high impact
                priority=priority,
                tactics=technique_tactics,
                techniques=[technique_id],
                mitigations=technique_mit_ids if technique_mit_ids else None,
                references=[url] if url else None,
                oscal_data={
                    "platforms": platforms,
                    "data_sources": data_sources,
                    "is_subtechnique": is_subtechnique,
                    "stix_id": stix_id,
                },
            )
            session.add(control)
            total_controls += 1

        # Update framework totals
        framework.total_controls = total_controls
        framework.categories = list(categories_used)

        await session.commit()

        print(f"\nTechniques by tactic:")
        for tactic, count in sorted(tactic_counts.items()):
            print(f"  {tactic}: {count}")

        print(f"\n{'='*60}")
        print(f"MITRE ATT&CK Import Complete!")
        print(f"{'='*60}")
        print(f"Total techniques imported: {total_controls}")
        print(f"Tactics covered: {len(tactic_counts)}")
        print(f"Categories mapped: {len(categories_used)}")
        print(f"Framework ID: {framework.id}")


async def main():
    """Main entry point."""
    print("="*60)
    print("MITRE ATT&CK Framework Import Script")
    print("="*60)

    try:
        await import_mitre_attack()
    except httpx.HTTPError as e:
        print(f"Error downloading MITRE data: {e}")
        raise
    except Exception as e:
        print(f"Error importing techniques: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
