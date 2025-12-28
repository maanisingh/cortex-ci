"""
NIST OSCAL Controls Import Script
Downloads and imports NIST 800-53 Rev 5 controls from the official OSCAL GitHub repository.

Usage:
    docker compose exec -w /app backend python scripts/import_oscal.py
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import httpx
import json
from uuid import uuid4
from datetime import date
from typing import Optional

from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal
from app.models import Tenant
from app.models.compliance.framework import (
    Framework, Control, FrameworkType, ControlCategory
)

# NIST OSCAL Catalog URL
NIST_800_53_URL = "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json"

# Map NIST 800-53 families to our control categories
FAMILY_TO_CATEGORY = {
    "ac": ControlCategory.ACCESS_CONTROL,
    "at": ControlCategory.AWARENESS_TRAINING,
    "au": ControlCategory.AUDIT_LOGGING,
    "ca": ControlCategory.SECURITY_ASSESSMENT,
    "cm": ControlCategory.CONFIGURATION_MANAGEMENT,
    "cp": ControlCategory.BUSINESS_CONTINUITY,
    "ia": ControlCategory.IDENTIFICATION_AUTHENTICATION,
    "ir": ControlCategory.INCIDENT_RESPONSE,
    "ma": ControlCategory.MAINTENANCE,
    "mp": ControlCategory.MEDIA_PROTECTION,
    "pe": ControlCategory.PHYSICAL_SECURITY,
    "pl": ControlCategory.PLANNING,
    "pm": ControlCategory.PROGRAM_MANAGEMENT,
    "ps": ControlCategory.PERSONNEL_SECURITY,
    "pt": ControlCategory.PRIVACY,
    "ra": ControlCategory.RISK_ASSESSMENT,
    "sa": ControlCategory.SUPPLY_CHAIN,
    "sc": ControlCategory.COMMUNICATIONS,
    "si": ControlCategory.VULNERABILITY_MANAGEMENT,
    "sr": ControlCategory.SUPPLY_CHAIN,
}

# Map baseline impact levels
BASELINE_PRIORITY = {
    "LOW": 3,
    "MODERATE": 2,
    "HIGH": 1,
}


def extract_prose(parts: list, separator: str = "\n") -> str:
    """Extract prose text from OSCAL parts."""
    texts = []
    for part in parts:
        if "prose" in part:
            texts.append(part["prose"])
        if "parts" in part:
            texts.append(extract_prose(part["parts"], separator))
    return separator.join(texts)


def get_control_description(control: dict) -> str:
    """Extract control description from OSCAL control."""
    parts = control.get("parts", [])
    statement_parts = [p for p in parts if p.get("name") == "statement"]
    if statement_parts:
        return extract_prose(statement_parts[0].get("parts", []))
    return extract_prose(parts)


def get_supplemental_guidance(control: dict) -> Optional[str]:
    """Extract supplemental guidance from OSCAL control."""
    parts = control.get("parts", [])
    guidance_parts = [p for p in parts if p.get("name") == "guidance"]
    if guidance_parts:
        return extract_prose(guidance_parts, "\n\n")
    return None


def get_baseline_impact(control: dict) -> Optional[str]:
    """Determine baseline impact level from control props."""
    props = control.get("props", [])
    for prop in props:
        if prop.get("name") == "label":
            # Controls in HIGH baseline are typically more critical
            pass
    # Default to MODERATE if not specified
    return "MODERATE"


def parse_control_id(oscal_id: str) -> str:
    """Parse OSCAL control ID to readable format."""
    # OSCAL uses lowercase (e.g., ac-1), convert to uppercase (e.g., AC-1)
    return oscal_id.upper()


async def fetch_oscal_catalog() -> dict:
    """Download NIST 800-53 OSCAL catalog."""
    print(f"Downloading NIST 800-53 Rev 5 OSCAL catalog...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(NIST_800_53_URL)
        response.raise_for_status()
        return response.json()


async def import_nist_800_53():
    """Import NIST 800-53 controls from OSCAL catalog."""

    # Fetch the OSCAL catalog
    catalog_data = await fetch_oscal_catalog()
    catalog = catalog_data.get("catalog", {})

    async with AsyncSessionLocal() as session:
        # Get the first tenant (or create one)
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

        # Check if NIST 800-53 framework already exists
        existing_framework = await session.execute(
            select(Framework).where(
                Framework.tenant_id == tenant_id,
                Framework.type == FrameworkType.NIST_800_53,
                Framework.version == "Rev 5"
            )
        )
        existing = existing_framework.scalars().first()

        if existing:
            print(f"NIST 800-53 Rev 5 framework already exists. Deleting and recreating...")
            # Delete existing controls first
            await session.execute(
                delete(Control).where(Control.framework_id == existing.id)
            )
            await session.delete(existing)
            await session.commit()

        # Create the framework
        framework = Framework(
            id=uuid4(),
            tenant_id=tenant_id,
            type=FrameworkType.NIST_800_53,
            name="NIST SP 800-53 Rev 5",
            version="Rev 5",
            description="NIST Special Publication 800-53 Revision 5 - Security and Privacy Controls for Information Systems and Organizations",
            source_url="https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final",
            publisher="National Institute of Standards and Technology (NIST)",
            publication_date=date(2020, 9, 23),
            oscal_catalog_id=catalog.get("uuid"),
            is_active=True,
            is_custom=False,
        )
        session.add(framework)

        # Parse control families (groups)
        groups = catalog.get("groups", [])
        total_controls = 0
        categories_used = set()

        print(f"\nImporting controls from {len(groups)} control families...")

        for group in groups:
            family_id = group.get("id", "").lower()
            family_title = group.get("title", "")
            category = FAMILY_TO_CATEGORY.get(family_id, ControlCategory.GOVERNANCE)
            categories_used.add(category.value if hasattr(category, 'value') else category)

            print(f"  Processing family: {family_title} ({family_id.upper()})")

            controls = group.get("controls", [])
            family_count = 0

            for control in controls:
                control_id = parse_control_id(control.get("id", ""))
                title = control.get("title", "")
                description = get_control_description(control)
                guidance = get_supplemental_guidance(control)

                # Get parameters
                parameters = {}
                for param in control.get("params", []):
                    param_id = param.get("id", "")
                    param_label = param.get("label", "")
                    param_select = param.get("select", {})
                    parameters[param_id] = {
                        "label": param_label,
                        "choices": param_select.get("choice", []) if param_select else []
                    }

                # Get references
                references = []
                for link in control.get("links", []):
                    if link.get("rel") == "reference":
                        references.append(link.get("href", ""))

                # Create control
                db_control = Control(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    framework_id=framework.id,
                    control_id=control_id,
                    title=title,
                    description=description or f"Control {control_id}",
                    family=family_title,
                    category=category,
                    guidance=guidance,
                    baseline_impact=get_baseline_impact(control),
                    priority=BASELINE_PRIORITY.get(get_baseline_impact(control), 2),
                    parameters=parameters if parameters else None,
                    references=references if references else None,
                    oscal_control_id=control.get("id"),
                    oscal_data=control,
                )
                session.add(db_control)
                family_count += 1
                total_controls += 1

                # Process control enhancements (sub-controls)
                for enhancement in control.get("controls", []):
                    enh_id = parse_control_id(enhancement.get("id", ""))
                    enh_title = enhancement.get("title", "")
                    enh_description = get_control_description(enhancement)
                    enh_guidance = get_supplemental_guidance(enhancement)

                    enh_params = {}
                    for param in enhancement.get("params", []):
                        param_id = param.get("id", "")
                        param_label = param.get("label", "")
                        enh_params[param_id] = {"label": param_label}

                    db_enhancement = Control(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        framework_id=framework.id,
                        control_id=enh_id,
                        title=enh_title,
                        description=enh_description or f"Control Enhancement {enh_id}",
                        family=family_title,
                        category=category,
                        guidance=enh_guidance,
                        parent_id=db_control.id,
                        baseline_impact="HIGH",  # Enhancements are typically for higher baselines
                        priority=1,
                        parameters=enh_params if enh_params else None,
                        oscal_control_id=enhancement.get("id"),
                        oscal_data=enhancement,
                    )
                    session.add(db_enhancement)
                    family_count += 1
                    total_controls += 1

            print(f"    -> {family_count} controls imported")

        # Update framework totals
        framework.total_controls = total_controls
        framework.categories = list(categories_used)

        await session.commit()

        print(f"\n{'='*60}")
        print(f"NIST 800-53 Rev 5 Import Complete!")
        print(f"{'='*60}")
        print(f"Total controls imported: {total_controls}")
        print(f"Control families: {len(groups)}")
        print(f"Categories mapped: {len(categories_used)}")
        print(f"Framework ID: {framework.id}")


async def main():
    """Main entry point."""
    print("="*60)
    print("NIST OSCAL Controls Import Script")
    print("="*60)

    try:
        await import_nist_800_53()
    except httpx.HTTPError as e:
        print(f"Error downloading OSCAL catalog: {e}")
        raise
    except Exception as e:
        print(f"Error importing controls: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
