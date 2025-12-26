#!/usr/bin/env python3
"""
Master Compliance Data Import Script

Imports all compliance data from open source sources:
1. NIST 800-53 Rev 5 (via OSCAL)
2. NIST CSF 2.0
3. CIS Controls v8
4. MITRE ATT&CK
5. ISO 27001:2022 (mapped)
6. SOC 2 Trust Services Criteria
7. PCI-DSS v4.0
8. HIPAA
9. GDPR
10. Country Risk Data (Transparency International CPI)
11. High-Risk Country Lists (FATF)
12. Industry Codes (NAICS)
"""
import asyncio
import json
import httpx
from datetime import datetime, date
from uuid import uuid4
from typing import Optional
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text


# ============================================================================
# DATA SOURCE URLs
# ============================================================================

DATA_SOURCES = {
    # NIST OSCAL Catalogs
    "nist_800_53_r5": "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json",
    "nist_csf_2": "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/CSF/2.0/json/CSF_catalog.json",

    # MITRE ATT&CK
    "mitre_attack_enterprise": "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",

    # CIS Controls
    "cis_controls_v8": "https://raw.githubusercontent.com/CISecurity/CISControlsMapping/main/CIS_Controls_Version_8.json",

    # Country Risk
    "transparency_cpi": "https://www.transparency.org/cpi2023/results",  # Will need scraping
    "fatf_high_risk": "https://www.fatf-gafi.org/en/publications/High-risk-and-other-monitored-jurisdictions.html",

    # OpenSanctions Datasets Info
    "opensanctions_datasets": "https://data.opensanctions.org/datasets/latest/index.json",
}


# ============================================================================
# NIST 800-53 Rev 5 Import
# ============================================================================

async def import_nist_800_53(session: AsyncSession, tenant_id: str):
    """Import NIST 800-53 Rev 5 controls from OSCAL."""
    print("\n[NIST 800-53 Rev 5] Starting import...")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(DATA_SOURCES["nist_800_53_r5"])
        response.raise_for_status()
        catalog = response.json()

    framework_id = str(uuid4())

    # Create framework
    await session.execute(text("""
        INSERT INTO frameworks (id, tenant_id, type, name, version, description, source_url, publisher, is_active, created_at, updated_at)
        VALUES (:id, :tenant_id, 'NIST_800_53', 'NIST SP 800-53 Rev 5', '5.0',
                'Security and Privacy Controls for Information Systems and Organizations',
                :source_url, 'National Institute of Standards and Technology', true, NOW(), NOW())
        ON CONFLICT DO NOTHING
    """), {
        "id": framework_id,
        "tenant_id": tenant_id,
        "source_url": DATA_SOURCES["nist_800_53_r5"]
    })

    control_count = 0
    catalog_data = catalog.get("catalog", {})

    # Process control families (groups)
    for group in catalog_data.get("groups", []):
        family_id = group.get("id", "")
        family_title = group.get("title", "")

        # Process controls in family
        for control in group.get("controls", []):
            control_id = control.get("id", "")
            title = control.get("title", "")

            # Get prose from parts
            description_parts = []
            for part in control.get("parts", []):
                if part.get("name") == "statement":
                    prose = part.get("prose", "")
                    if prose:
                        description_parts.append(prose)

            description = "\n".join(description_parts) or f"Control {control_id}"

            # Get guidance
            guidance = ""
            for part in control.get("parts", []):
                if part.get("name") == "guidance":
                    guidance = part.get("prose", "")

            # Determine baseline impact
            props = {p.get("name"): p.get("value") for p in control.get("props", [])}
            baseline = props.get("baseline", "")

            await session.execute(text("""
                INSERT INTO controls (id, tenant_id, framework_id, control_id, title, description,
                    family, guidance, baseline_impact, implementation_status, created_at, updated_at)
                VALUES (:id, :tenant_id, :framework_id, :control_id, :title, :description,
                    :family, :guidance, :baseline, 'NOT_ASSESSED', NOW(), NOW())
                ON CONFLICT DO NOTHING
            """), {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "framework_id": framework_id,
                "control_id": control_id.upper(),
                "title": title,
                "description": description[:5000],
                "family": family_title,
                "guidance": guidance[:5000] if guidance else None,
                "baseline": baseline if baseline else None
            })
            control_count += 1

            # Process control enhancements
            for enhancement in control.get("controls", []):
                enh_id = enhancement.get("id", "")
                enh_title = enhancement.get("title", "")

                enh_parts = []
                for part in enhancement.get("parts", []):
                    if part.get("name") == "statement":
                        prose = part.get("prose", "")
                        if prose:
                            enh_parts.append(prose)

                enh_description = "\n".join(enh_parts) or f"Enhancement {enh_id}"

                await session.execute(text("""
                    INSERT INTO controls (id, tenant_id, framework_id, control_id, title, description,
                        family, implementation_status, created_at, updated_at)
                    VALUES (:id, :tenant_id, :framework_id, :control_id, :title, :description,
                        :family, 'NOT_ASSESSED', NOW(), NOW())
                    ON CONFLICT DO NOTHING
                """), {
                    "id": str(uuid4()),
                    "tenant_id": tenant_id,
                    "framework_id": framework_id,
                    "control_id": enh_id.upper(),
                    "title": enh_title,
                    "description": enh_description[:5000],
                    "family": family_title
                })
                control_count += 1

    # Update framework control count
    await session.execute(text("""
        UPDATE frameworks SET total_controls = :count WHERE id = :id
    """), {"count": control_count, "id": framework_id})

    await session.commit()
    print(f"[NIST 800-53 Rev 5] Imported {control_count} controls")
    return control_count


# ============================================================================
# MITRE ATT&CK Import
# ============================================================================

async def import_mitre_attack(session: AsyncSession, tenant_id: str):
    """Import MITRE ATT&CK Enterprise framework."""
    print("\n[MITRE ATT&CK] Starting import...")

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.get(DATA_SOURCES["mitre_attack_enterprise"])
        response.raise_for_status()
        attack_data = response.json()

    framework_id = str(uuid4())

    # Create framework
    await session.execute(text("""
        INSERT INTO frameworks (id, tenant_id, type, name, version, description, source_url, publisher, is_active, created_at, updated_at)
        VALUES (:id, :tenant_id, 'MITRE_ATTACK', 'MITRE ATT&CK Enterprise', '14.0',
                'Adversarial Tactics, Techniques, and Common Knowledge',
                :source_url, 'The MITRE Corporation', true, NOW(), NOW())
        ON CONFLICT DO NOTHING
    """), {
        "id": framework_id,
        "tenant_id": tenant_id,
        "source_url": DATA_SOURCES["mitre_attack_enterprise"]
    })

    # Extract tactics and techniques
    objects = attack_data.get("objects", [])

    tactics = {}
    techniques = []
    mitigations = []

    for obj in objects:
        obj_type = obj.get("type", "")

        if obj_type == "x-mitre-tactic":
            tactic_id = obj.get("external_references", [{}])[0].get("external_id", "")
            tactics[obj.get("x_mitre_shortname", "")] = {
                "id": tactic_id,
                "name": obj.get("name", "")
            }

        elif obj_type == "attack-pattern":
            ext_refs = obj.get("external_references", [])
            technique_id = next((r.get("external_id") for r in ext_refs if r.get("source_name") == "mitre-attack"), "")

            if technique_id:
                techniques.append({
                    "id": technique_id,
                    "name": obj.get("name", ""),
                    "description": obj.get("description", ""),
                    "tactics": [p.get("phase_name") for p in obj.get("kill_chain_phases", [])],
                    "platforms": obj.get("x_mitre_platforms", []),
                    "is_subtechnique": obj.get("x_mitre_is_subtechnique", False)
                })

        elif obj_type == "course-of-action":
            ext_refs = obj.get("external_references", [])
            mitigation_id = next((r.get("external_id") for r in ext_refs if r.get("source_name") == "mitre-attack"), "")

            if mitigation_id:
                mitigations.append({
                    "id": mitigation_id,
                    "name": obj.get("name", ""),
                    "description": obj.get("description", "")
                })

    control_count = 0

    # Insert techniques as controls
    for tech in techniques:
        tactic_names = [tactics.get(t, {}).get("name", t) for t in tech["tactics"]]

        await session.execute(text("""
            INSERT INTO controls (id, tenant_id, framework_id, control_id, title, description,
                family, tactics, implementation_status, created_at, updated_at)
            VALUES (:id, :tenant_id, :framework_id, :control_id, :title, :description,
                :family, :tactics, 'NOT_ASSESSED', NOW(), NOW())
            ON CONFLICT DO NOTHING
        """), {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "framework_id": framework_id,
            "control_id": tech["id"],
            "title": tech["name"],
            "description": tech["description"][:5000] if tech["description"] else f"Technique {tech['id']}",
            "family": ", ".join(tactic_names) if tactic_names else "Unknown",
            "tactics": tactic_names
        })
        control_count += 1

    # Insert mitigations
    for mit in mitigations:
        await session.execute(text("""
            INSERT INTO controls (id, tenant_id, framework_id, control_id, title, description,
                category, implementation_status, created_at, updated_at)
            VALUES (:id, :tenant_id, :framework_id, :control_id, :title, :description,
                'MITIGATION', 'NOT_ASSESSED', NOW(), NOW())
            ON CONFLICT DO NOTHING
        """), {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "framework_id": framework_id,
            "control_id": mit["id"],
            "title": mit["name"],
            "description": mit["description"][:5000] if mit["description"] else f"Mitigation {mit['id']}"
        })
        control_count += 1

    await session.execute(text("""
        UPDATE frameworks SET total_controls = :count WHERE id = :id
    """), {"count": control_count, "id": framework_id})

    await session.commit()
    print(f"[MITRE ATT&CK] Imported {len(techniques)} techniques and {len(mitigations)} mitigations")
    return control_count


# ============================================================================
# CIS Controls v8 Import
# ============================================================================

async def import_cis_controls(session: AsyncSession, tenant_id: str):
    """Import CIS Controls v8 - hardcoded since JSON not always available."""
    print("\n[CIS Controls v8] Starting import...")

    framework_id = str(uuid4())

    # CIS Controls v8 structure
    cis_controls = [
        {"id": "CIS.1", "title": "Inventory and Control of Enterprise Assets", "ig": ["IG1", "IG2", "IG3"], "safeguards": 5},
        {"id": "CIS.2", "title": "Inventory and Control of Software Assets", "ig": ["IG1", "IG2", "IG3"], "safeguards": 7},
        {"id": "CIS.3", "title": "Data Protection", "ig": ["IG1", "IG2", "IG3"], "safeguards": 14},
        {"id": "CIS.4", "title": "Secure Configuration of Enterprise Assets and Software", "ig": ["IG1", "IG2", "IG3"], "safeguards": 12},
        {"id": "CIS.5", "title": "Account Management", "ig": ["IG1", "IG2", "IG3"], "safeguards": 6},
        {"id": "CIS.6", "title": "Access Control Management", "ig": ["IG1", "IG2", "IG3"], "safeguards": 8},
        {"id": "CIS.7", "title": "Continuous Vulnerability Management", "ig": ["IG2", "IG3"], "safeguards": 7},
        {"id": "CIS.8", "title": "Audit Log Management", "ig": ["IG1", "IG2", "IG3"], "safeguards": 12},
        {"id": "CIS.9", "title": "Email and Web Browser Protections", "ig": ["IG1", "IG2", "IG3"], "safeguards": 7},
        {"id": "CIS.10", "title": "Malware Defenses", "ig": ["IG1", "IG2", "IG3"], "safeguards": 7},
        {"id": "CIS.11", "title": "Data Recovery", "ig": ["IG1", "IG2", "IG3"], "safeguards": 5},
        {"id": "CIS.12", "title": "Network Infrastructure Management", "ig": ["IG1", "IG2", "IG3"], "safeguards": 8},
        {"id": "CIS.13", "title": "Network Monitoring and Defense", "ig": ["IG2", "IG3"], "safeguards": 11},
        {"id": "CIS.14", "title": "Security Awareness and Skills Training", "ig": ["IG1", "IG2", "IG3"], "safeguards": 9},
        {"id": "CIS.15", "title": "Service Provider Management", "ig": ["IG2", "IG3"], "safeguards": 7},
        {"id": "CIS.16", "title": "Application Software Security", "ig": ["IG2", "IG3"], "safeguards": 14},
        {"id": "CIS.17", "title": "Incident Response Management", "ig": ["IG2", "IG3"], "safeguards": 9},
        {"id": "CIS.18", "title": "Penetration Testing", "ig": ["IG3"], "safeguards": 5},
    ]

    await session.execute(text("""
        INSERT INTO frameworks (id, tenant_id, type, name, version, description, source_url, publisher, is_active, created_at, updated_at)
        VALUES (:id, :tenant_id, 'CIS_CONTROLS', 'CIS Controls', 'v8',
                'Critical Security Controls for Effective Cyber Defense',
                'https://www.cisecurity.org/controls/v8', 'Center for Internet Security', true, NOW(), NOW())
        ON CONFLICT DO NOTHING
    """), {"id": framework_id, "tenant_id": tenant_id})

    control_count = 0
    for ctrl in cis_controls:
        await session.execute(text("""
            INSERT INTO controls (id, tenant_id, framework_id, control_id, title, description,
                family, baseline_impact, implementation_status, created_at, updated_at)
            VALUES (:id, :tenant_id, :framework_id, :control_id, :title, :description,
                :family, :baseline, 'NOT_ASSESSED', NOW(), NOW())
            ON CONFLICT DO NOTHING
        """), {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "framework_id": framework_id,
            "control_id": ctrl["id"],
            "title": ctrl["title"],
            "description": f"{ctrl['title']} - Contains {ctrl['safeguards']} safeguards",
            "family": "CIS Controls v8",
            "baseline": ", ".join(ctrl["ig"])
        })
        control_count += 1

    await session.execute(text("""
        UPDATE frameworks SET total_controls = :count WHERE id = :id
    """), {"count": control_count, "id": framework_id})

    await session.commit()
    print(f"[CIS Controls v8] Imported {control_count} controls")
    return control_count


# ============================================================================
# ISO 27001:2022 Import
# ============================================================================

async def import_iso_27001(session: AsyncSession, tenant_id: str):
    """Import ISO 27001:2022 controls."""
    print("\n[ISO 27001:2022] Starting import...")

    framework_id = str(uuid4())

    # ISO 27001:2022 Annex A controls (93 controls in 4 themes)
    iso_controls = [
        # Organizational controls (37)
        {"id": "A.5.1", "title": "Policies for information security", "theme": "Organizational"},
        {"id": "A.5.2", "title": "Information security roles and responsibilities", "theme": "Organizational"},
        {"id": "A.5.3", "title": "Segregation of duties", "theme": "Organizational"},
        {"id": "A.5.4", "title": "Management responsibilities", "theme": "Organizational"},
        {"id": "A.5.5", "title": "Contact with authorities", "theme": "Organizational"},
        {"id": "A.5.6", "title": "Contact with special interest groups", "theme": "Organizational"},
        {"id": "A.5.7", "title": "Threat intelligence", "theme": "Organizational"},
        {"id": "A.5.8", "title": "Information security in project management", "theme": "Organizational"},
        {"id": "A.5.9", "title": "Inventory of information and other associated assets", "theme": "Organizational"},
        {"id": "A.5.10", "title": "Acceptable use of information and other associated assets", "theme": "Organizational"},
        {"id": "A.5.11", "title": "Return of assets", "theme": "Organizational"},
        {"id": "A.5.12", "title": "Classification of information", "theme": "Organizational"},
        {"id": "A.5.13", "title": "Labelling of information", "theme": "Organizational"},
        {"id": "A.5.14", "title": "Information transfer", "theme": "Organizational"},
        {"id": "A.5.15", "title": "Access control", "theme": "Organizational"},
        {"id": "A.5.16", "title": "Identity management", "theme": "Organizational"},
        {"id": "A.5.17", "title": "Authentication information", "theme": "Organizational"},
        {"id": "A.5.18", "title": "Access rights", "theme": "Organizational"},
        {"id": "A.5.19", "title": "Information security in supplier relationships", "theme": "Organizational"},
        {"id": "A.5.20", "title": "Addressing information security within supplier agreements", "theme": "Organizational"},
        {"id": "A.5.21", "title": "Managing information security in the ICT supply chain", "theme": "Organizational"},
        {"id": "A.5.22", "title": "Monitoring, review and change management of supplier services", "theme": "Organizational"},
        {"id": "A.5.23", "title": "Information security for use of cloud services", "theme": "Organizational"},
        {"id": "A.5.24", "title": "Information security incident management planning and preparation", "theme": "Organizational"},
        {"id": "A.5.25", "title": "Assessment and decision on information security events", "theme": "Organizational"},
        {"id": "A.5.26", "title": "Response to information security incidents", "theme": "Organizational"},
        {"id": "A.5.27", "title": "Learning from information security incidents", "theme": "Organizational"},
        {"id": "A.5.28", "title": "Collection of evidence", "theme": "Organizational"},
        {"id": "A.5.29", "title": "Information security during disruption", "theme": "Organizational"},
        {"id": "A.5.30", "title": "ICT readiness for business continuity", "theme": "Organizational"},
        {"id": "A.5.31", "title": "Legal, statutory, regulatory and contractual requirements", "theme": "Organizational"},
        {"id": "A.5.32", "title": "Intellectual property rights", "theme": "Organizational"},
        {"id": "A.5.33", "title": "Protection of records", "theme": "Organizational"},
        {"id": "A.5.34", "title": "Privacy and protection of PII", "theme": "Organizational"},
        {"id": "A.5.35", "title": "Independent review of information security", "theme": "Organizational"},
        {"id": "A.5.36", "title": "Compliance with policies, rules and standards for information security", "theme": "Organizational"},
        {"id": "A.5.37", "title": "Documented operating procedures", "theme": "Organizational"},
        # People controls (8)
        {"id": "A.6.1", "title": "Screening", "theme": "People"},
        {"id": "A.6.2", "title": "Terms and conditions of employment", "theme": "People"},
        {"id": "A.6.3", "title": "Information security awareness, education and training", "theme": "People"},
        {"id": "A.6.4", "title": "Disciplinary process", "theme": "People"},
        {"id": "A.6.5", "title": "Responsibilities after termination or change of employment", "theme": "People"},
        {"id": "A.6.6", "title": "Confidentiality or non-disclosure agreements", "theme": "People"},
        {"id": "A.6.7", "title": "Remote working", "theme": "People"},
        {"id": "A.6.8", "title": "Information security event reporting", "theme": "People"},
        # Physical controls (14)
        {"id": "A.7.1", "title": "Physical security perimeters", "theme": "Physical"},
        {"id": "A.7.2", "title": "Physical entry", "theme": "Physical"},
        {"id": "A.7.3", "title": "Securing offices, rooms and facilities", "theme": "Physical"},
        {"id": "A.7.4", "title": "Physical security monitoring", "theme": "Physical"},
        {"id": "A.7.5", "title": "Protecting against physical and environmental threats", "theme": "Physical"},
        {"id": "A.7.6", "title": "Working in secure areas", "theme": "Physical"},
        {"id": "A.7.7", "title": "Clear desk and clear screen", "theme": "Physical"},
        {"id": "A.7.8", "title": "Equipment siting and protection", "theme": "Physical"},
        {"id": "A.7.9", "title": "Security of assets off-premises", "theme": "Physical"},
        {"id": "A.7.10", "title": "Storage media", "theme": "Physical"},
        {"id": "A.7.11", "title": "Supporting utilities", "theme": "Physical"},
        {"id": "A.7.12", "title": "Cabling security", "theme": "Physical"},
        {"id": "A.7.13", "title": "Equipment maintenance", "theme": "Physical"},
        {"id": "A.7.14", "title": "Secure disposal or re-use of equipment", "theme": "Physical"},
        # Technological controls (34)
        {"id": "A.8.1", "title": "User endpoint devices", "theme": "Technological"},
        {"id": "A.8.2", "title": "Privileged access rights", "theme": "Technological"},
        {"id": "A.8.3", "title": "Information access restriction", "theme": "Technological"},
        {"id": "A.8.4", "title": "Access to source code", "theme": "Technological"},
        {"id": "A.8.5", "title": "Secure authentication", "theme": "Technological"},
        {"id": "A.8.6", "title": "Capacity management", "theme": "Technological"},
        {"id": "A.8.7", "title": "Protection against malware", "theme": "Technological"},
        {"id": "A.8.8", "title": "Management of technical vulnerabilities", "theme": "Technological"},
        {"id": "A.8.9", "title": "Configuration management", "theme": "Technological"},
        {"id": "A.8.10", "title": "Information deletion", "theme": "Technological"},
        {"id": "A.8.11", "title": "Data masking", "theme": "Technological"},
        {"id": "A.8.12", "title": "Data leakage prevention", "theme": "Technological"},
        {"id": "A.8.13", "title": "Information backup", "theme": "Technological"},
        {"id": "A.8.14", "title": "Redundancy of information processing facilities", "theme": "Technological"},
        {"id": "A.8.15", "title": "Logging", "theme": "Technological"},
        {"id": "A.8.16", "title": "Monitoring activities", "theme": "Technological"},
        {"id": "A.8.17", "title": "Clock synchronization", "theme": "Technological"},
        {"id": "A.8.18", "title": "Use of privileged utility programs", "theme": "Technological"},
        {"id": "A.8.19", "title": "Installation of software on operational systems", "theme": "Technological"},
        {"id": "A.8.20", "title": "Networks security", "theme": "Technological"},
        {"id": "A.8.21", "title": "Security of network services", "theme": "Technological"},
        {"id": "A.8.22", "title": "Segregation of networks", "theme": "Technological"},
        {"id": "A.8.23", "title": "Web filtering", "theme": "Technological"},
        {"id": "A.8.24", "title": "Use of cryptography", "theme": "Technological"},
        {"id": "A.8.25", "title": "Secure development life cycle", "theme": "Technological"},
        {"id": "A.8.26", "title": "Application security requirements", "theme": "Technological"},
        {"id": "A.8.27", "title": "Secure system architecture and engineering principles", "theme": "Technological"},
        {"id": "A.8.28", "title": "Secure coding", "theme": "Technological"},
        {"id": "A.8.29", "title": "Security testing in development and acceptance", "theme": "Technological"},
        {"id": "A.8.30", "title": "Outsourced development", "theme": "Technological"},
        {"id": "A.8.31", "title": "Separation of development, test and production environments", "theme": "Technological"},
        {"id": "A.8.32", "title": "Change management", "theme": "Technological"},
        {"id": "A.8.33", "title": "Test information", "theme": "Technological"},
        {"id": "A.8.34", "title": "Protection of information systems during audit testing", "theme": "Technological"},
    ]

    await session.execute(text("""
        INSERT INTO frameworks (id, tenant_id, type, name, version, description, source_url, publisher, is_active, created_at, updated_at)
        VALUES (:id, :tenant_id, 'ISO_27001', 'ISO/IEC 27001:2022', '2022',
                'Information security, cybersecurity and privacy protection - Information security management systems',
                'https://www.iso.org/standard/27001', 'ISO/IEC', true, NOW(), NOW())
        ON CONFLICT DO NOTHING
    """), {"id": framework_id, "tenant_id": tenant_id})

    control_count = 0
    for ctrl in iso_controls:
        await session.execute(text("""
            INSERT INTO controls (id, tenant_id, framework_id, control_id, title, description,
                family, implementation_status, created_at, updated_at)
            VALUES (:id, :tenant_id, :framework_id, :control_id, :title, :description,
                :family, 'NOT_ASSESSED', NOW(), NOW())
            ON CONFLICT DO NOTHING
        """), {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "framework_id": framework_id,
            "control_id": ctrl["id"],
            "title": ctrl["title"],
            "description": ctrl["title"],
            "family": ctrl["theme"]
        })
        control_count += 1

    await session.execute(text("""
        UPDATE frameworks SET total_controls = :count WHERE id = :id
    """), {"count": control_count, "id": framework_id})

    await session.commit()
    print(f"[ISO 27001:2022] Imported {control_count} controls")
    return control_count


# ============================================================================
# SOC 2 Trust Services Criteria Import
# ============================================================================

async def import_soc2(session: AsyncSession, tenant_id: str):
    """Import SOC 2 Trust Services Criteria."""
    print("\n[SOC 2] Starting import...")

    framework_id = str(uuid4())

    soc2_criteria = [
        # Common Criteria (CC)
        {"id": "CC1.1", "title": "COSO Principle 1", "category": "Control Environment", "description": "The entity demonstrates a commitment to integrity and ethical values."},
        {"id": "CC1.2", "title": "COSO Principle 2", "category": "Control Environment", "description": "The board of directors demonstrates independence from management and exercises oversight."},
        {"id": "CC1.3", "title": "COSO Principle 3", "category": "Control Environment", "description": "Management establishes structures, reporting lines, and authorities."},
        {"id": "CC1.4", "title": "COSO Principle 4", "category": "Control Environment", "description": "The entity demonstrates a commitment to attract, develop, and retain competent individuals."},
        {"id": "CC1.5", "title": "COSO Principle 5", "category": "Control Environment", "description": "The entity holds individuals accountable for their internal control responsibilities."},
        {"id": "CC2.1", "title": "COSO Principle 13", "category": "Communication and Information", "description": "The entity obtains or generates and uses relevant, quality information."},
        {"id": "CC2.2", "title": "COSO Principle 14", "category": "Communication and Information", "description": "The entity internally communicates information necessary to support the functioning of internal control."},
        {"id": "CC2.3", "title": "COSO Principle 15", "category": "Communication and Information", "description": "The entity communicates with external parties regarding matters affecting the functioning of internal control."},
        {"id": "CC3.1", "title": "COSO Principle 6", "category": "Risk Assessment", "description": "The entity specifies objectives with sufficient clarity to enable the identification and assessment of risks."},
        {"id": "CC3.2", "title": "COSO Principle 7", "category": "Risk Assessment", "description": "The entity identifies risks to the achievement of its objectives and analyzes risks."},
        {"id": "CC3.3", "title": "COSO Principle 8", "category": "Risk Assessment", "description": "The entity considers the potential for fraud in assessing risks."},
        {"id": "CC3.4", "title": "COSO Principle 9", "category": "Risk Assessment", "description": "The entity identifies and assesses changes that could significantly impact the system of internal control."},
        {"id": "CC4.1", "title": "COSO Principle 16", "category": "Monitoring Activities", "description": "The entity selects, develops, and performs ongoing or separate evaluations."},
        {"id": "CC4.2", "title": "COSO Principle 17", "category": "Monitoring Activities", "description": "The entity evaluates and communicates internal control deficiencies."},
        {"id": "CC5.1", "title": "COSO Principle 10", "category": "Control Activities", "description": "The entity selects and develops control activities that contribute to the mitigation of risks."},
        {"id": "CC5.2", "title": "COSO Principle 11", "category": "Control Activities", "description": "The entity selects and develops general control activities over technology."},
        {"id": "CC5.3", "title": "COSO Principle 12", "category": "Control Activities", "description": "The entity deploys control activities through policies and procedures."},
        {"id": "CC6.1", "title": "Logical and Physical Access Controls", "category": "Logical and Physical Access", "description": "The entity implements logical access security measures."},
        {"id": "CC6.2", "title": "System Component Registration", "category": "Logical and Physical Access", "description": "Prior to issuing system credentials, the entity registers authorized users."},
        {"id": "CC6.3", "title": "Authorization and Authentication", "category": "Logical and Physical Access", "description": "The entity authorizes, modifies, or removes access based on roles."},
        {"id": "CC6.4", "title": "Access Review", "category": "Logical and Physical Access", "description": "The entity restricts physical access to facilities and protected information assets."},
        {"id": "CC6.5", "title": "Asset Disposal", "category": "Logical and Physical Access", "description": "The entity discontinues logical and physical protections over physical assets only after disposal."},
        {"id": "CC6.6", "title": "External Access", "category": "Logical and Physical Access", "description": "The entity implements logical access security measures to protect against threats from sources outside its system boundaries."},
        {"id": "CC6.7", "title": "Data Transmission", "category": "Logical and Physical Access", "description": "The entity restricts the transmission, movement, and removal of information."},
        {"id": "CC6.8", "title": "Malware Prevention", "category": "Logical and Physical Access", "description": "The entity implements controls to prevent or detect and act upon malware."},
        {"id": "CC7.1", "title": "Configuration Management", "category": "System Operations", "description": "The entity manages the configuration of system components."},
        {"id": "CC7.2", "title": "Change Management", "category": "System Operations", "description": "The entity monitors system components and the operation of those components."},
        {"id": "CC7.3", "title": "Vulnerability Management", "category": "System Operations", "description": "The entity evaluates security events to determine whether they could impact the achievement of objectives."},
        {"id": "CC7.4", "title": "Incident Response", "category": "System Operations", "description": "The entity responds to identified security incidents."},
        {"id": "CC7.5", "title": "Incident Recovery", "category": "System Operations", "description": "The entity identifies, develops, and implements activities to recover from security incidents."},
        {"id": "CC8.1", "title": "Change Authorization", "category": "Change Management", "description": "The entity authorizes, designs, develops, and implements changes."},
        {"id": "CC9.1", "title": "Risk Mitigation for Business Disruption", "category": "Risk Mitigation", "description": "The entity identifies, selects, and develops risk mitigation activities for risks from business disruption."},
        {"id": "CC9.2", "title": "Vendor Risk Management", "category": "Risk Mitigation", "description": "The entity assesses and manages risks associated with vendors and business partners."},
        # Availability criteria
        {"id": "A1.1", "title": "Capacity Planning", "category": "Availability", "description": "The entity maintains, monitors, and evaluates current processing capacity and use."},
        {"id": "A1.2", "title": "System Recovery", "category": "Availability", "description": "The entity authorizes, designs, develops, and implements activities to recover."},
        {"id": "A1.3", "title": "Recovery Testing", "category": "Availability", "description": "The entity tests recovery plan procedures supporting system recovery."},
        # Confidentiality criteria
        {"id": "C1.1", "title": "Confidential Information", "category": "Confidentiality", "description": "The entity identifies and maintains confidential information."},
        {"id": "C1.2", "title": "Confidential Information Disposal", "category": "Confidentiality", "description": "The entity disposes of confidential information."},
        # Processing Integrity criteria
        {"id": "PI1.1", "title": "Processing Accuracy", "category": "Processing Integrity", "description": "The entity implements policies and procedures over system processing."},
        {"id": "PI1.2", "title": "Input Accuracy", "category": "Processing Integrity", "description": "System input is complete, accurate, and recorded timely."},
        {"id": "PI1.3", "title": "Processing Accuracy Validation", "category": "Processing Integrity", "description": "System processing is complete, accurate, timely, and authorized."},
        {"id": "PI1.4", "title": "Output Accuracy", "category": "Processing Integrity", "description": "System output is complete, accurate, and distributed timely."},
        {"id": "PI1.5", "title": "Data Storage", "category": "Processing Integrity", "description": "Data stored by the entity is complete, accurate, and protected."},
        # Privacy criteria
        {"id": "P1.1", "title": "Privacy Notice", "category": "Privacy", "description": "The entity provides notice about its privacy practices."},
        {"id": "P2.1", "title": "Choice and Consent", "category": "Privacy", "description": "The entity communicates choices available regarding personal information."},
        {"id": "P3.1", "title": "Collection", "category": "Privacy", "description": "Personal information is collected consistent with the entity's objectives."},
        {"id": "P3.2", "title": "Explicit Consent for Sensitive Information", "category": "Privacy", "description": "Explicit consent for the collection of sensitive personal information."},
        {"id": "P4.1", "title": "Limited Use", "category": "Privacy", "description": "The entity limits the use of personal information to specified purposes."},
        {"id": "P4.2", "title": "Retention", "category": "Privacy", "description": "The entity retains personal information consistent with objectives."},
        {"id": "P4.3", "title": "Disposal", "category": "Privacy", "description": "The entity securely disposes of personal information."},
        {"id": "P5.1", "title": "Data Subject Access", "category": "Privacy", "description": "The entity grants identified and authenticated data subjects access."},
        {"id": "P5.2", "title": "Correction", "category": "Privacy", "description": "The entity corrects, amends, or appends personal information."},
        {"id": "P6.1", "title": "Disclosure", "category": "Privacy", "description": "The entity discloses personal information to third parties with consent."},
        {"id": "P6.2", "title": "Disclosed Information Protection", "category": "Privacy", "description": "The entity creates and retains a record of disclosures."},
        {"id": "P6.3", "title": "Third-Party Obligations", "category": "Privacy", "description": "The entity ensures third-party obligations for information protection."},
        {"id": "P6.4", "title": "Notice of Third-Party Changes", "category": "Privacy", "description": "The entity notifies data subjects of changes in third parties."},
        {"id": "P6.5", "title": "Dispute Resolution", "category": "Privacy", "description": "The entity provides mechanisms for dispute resolution."},
        {"id": "P6.6", "title": "Unauthorized Disclosure", "category": "Privacy", "description": "The entity notifies affected parties of unauthorized disclosure."},
        {"id": "P6.7", "title": "Third-Party Compliance", "category": "Privacy", "description": "The entity provides required information to third parties."},
        {"id": "P7.1", "title": "Quality of Personal Information", "category": "Privacy", "description": "The entity collects and maintains accurate personal information."},
        {"id": "P8.1", "title": "Privacy Complaints", "category": "Privacy", "description": "The entity implements a process for handling privacy complaints."},
    ]

    await session.execute(text("""
        INSERT INTO frameworks (id, tenant_id, type, name, version, description, source_url, publisher, is_active, created_at, updated_at)
        VALUES (:id, :tenant_id, 'SOC_2', 'SOC 2 Trust Services Criteria', '2017',
                'Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy',
                'https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aaborservice-organizations',
                'AICPA', true, NOW(), NOW())
        ON CONFLICT DO NOTHING
    """), {"id": framework_id, "tenant_id": tenant_id})

    control_count = 0
    for ctrl in soc2_criteria:
        await session.execute(text("""
            INSERT INTO controls (id, tenant_id, framework_id, control_id, title, description,
                family, category, implementation_status, created_at, updated_at)
            VALUES (:id, :tenant_id, :framework_id, :control_id, :title, :description,
                :family, :category, 'NOT_ASSESSED', NOW(), NOW())
            ON CONFLICT DO NOTHING
        """), {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "framework_id": framework_id,
            "control_id": ctrl["id"],
            "title": ctrl["title"],
            "description": ctrl["description"],
            "family": "Trust Services Criteria",
            "category": ctrl["category"]
        })
        control_count += 1

    await session.execute(text("""
        UPDATE frameworks SET total_controls = :count WHERE id = :id
    """), {"count": control_count, "id": framework_id})

    await session.commit()
    print(f"[SOC 2] Imported {control_count} criteria")
    return control_count


# ============================================================================
# Country Risk Data Import
# ============================================================================

async def import_country_risk(session: AsyncSession, tenant_id: str):
    """Import country risk data from various sources."""
    print("\n[Country Risk] Starting import...")

    # FATF High-Risk and Other Monitored Jurisdictions (as of 2024)
    # Black list - Call for Action
    fatf_black_list = ["KP", "IR", "MM"]  # North Korea, Iran, Myanmar

    # Grey list - Increased Monitoring
    fatf_grey_list = [
        "BF", "CM", "CD", "HT", "KE", "ML", "MZ", "NG", "SN", "ZA",  # Africa
        "PH", "VN", "SY",  # Asia
        "AL", "BA", "JO", "TZ",  # Others
        "VE", "YE"  # Americas/Middle East
    ]

    # Transparency International CPI 2023 - High corruption risk (score < 30)
    high_corruption_risk = [
        "SO", "SS", "VE", "SY", "YE", "LY", "KP", "HT", "GQ", "TD", "TM", "BI",
        "CF", "CG", "GN", "AF", "IQ", "ER", "LA", "ZW"
    ]

    # EU High-Risk Third Countries
    eu_high_risk = ["AF", "MM", "GY", "HT", "JM", "JO", "ML", "MZ", "NG", "PA", "PH",
                    "SN", "SS", "SY", "TZ", "TT", "UG", "AE", "VN", "YE", "ZA"]

    # Store in a reference table
    for country_code in set(fatf_black_list + fatf_grey_list + high_corruption_risk + eu_high_risk):
        risk_factors = []
        risk_level = "MEDIUM"

        if country_code in fatf_black_list:
            risk_factors.append("FATF_BLACK_LIST")
            risk_level = "VERY_HIGH"
        if country_code in fatf_grey_list:
            risk_factors.append("FATF_GREY_LIST")
            if risk_level != "VERY_HIGH":
                risk_level = "HIGH"
        if country_code in high_corruption_risk:
            risk_factors.append("HIGH_CORRUPTION")
            if risk_level not in ["VERY_HIGH", "HIGH"]:
                risk_level = "HIGH"
        if country_code in eu_high_risk:
            risk_factors.append("EU_HIGH_RISK")
            if risk_level not in ["VERY_HIGH", "HIGH"]:
                risk_level = "HIGH"

        # Store as custom_data in a simple reference format
        await session.execute(text("""
            INSERT INTO entities (id, tenant_id, type, name, country_code, category,
                custom_data, is_active, created_at, updated_at)
            VALUES (:id, :tenant_id, 'LOCATION', :name, :country_code, 'HIGH_RISK_JURISDICTION',
                :custom_data, true, NOW(), NOW())
            ON CONFLICT DO NOTHING
        """), {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "name": f"High-Risk Jurisdiction: {country_code}",
            "country_code": country_code,
            "custom_data": json.dumps({
                "risk_level": risk_level,
                "risk_factors": risk_factors
            })
        })

    await session.commit()
    print(f"[Country Risk] Imported risk data for {len(set(fatf_black_list + fatf_grey_list + high_corruption_risk + eu_high_risk))} countries")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Run all imports."""
    print("=" * 60)
    print("CORTEX COMPLIANCE DATA IMPORT")
    print("=" * 60)

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/cortex_ci")

    # Create engine
    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Get or create default tenant
    async with async_session() as session:
        result = await session.execute(text("SELECT id FROM tenants LIMIT 1"))
        row = result.fetchone()
        if row:
            tenant_id = str(row[0])
        else:
            tenant_id = str(uuid4())
            await session.execute(text("""
                INSERT INTO tenants (id, name, slug, is_active, created_at, updated_at)
                VALUES (:id, 'Default', 'default', true, NOW(), NOW())
            """), {"id": tenant_id})
            await session.commit()

    print(f"\nUsing tenant: {tenant_id}")

    total_controls = 0

    async with async_session() as session:
        try:
            # Import all frameworks
            total_controls += await import_nist_800_53(session, tenant_id)
            total_controls += await import_mitre_attack(session, tenant_id)
            total_controls += await import_cis_controls(session, tenant_id)
            total_controls += await import_iso_27001(session, tenant_id)
            total_controls += await import_soc2(session, tenant_id)
            await import_country_risk(session, tenant_id)

        except Exception as e:
            print(f"\nError during import: {e}")
            raise

    print("\n" + "=" * 60)
    print(f"IMPORT COMPLETE: {total_controls} total controls imported")
    print("=" * 60)

    # Summary
    async with async_session() as session:
        result = await session.execute(text("SELECT type, total_controls FROM frameworks ORDER BY type"))
        rows = result.fetchall()

        print("\nFrameworks imported:")
        for row in rows:
            print(f"  - {row[0]}: {row[1]} controls")


if __name__ == "__main__":
    asyncio.run(main())
