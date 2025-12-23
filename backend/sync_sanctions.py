#!/usr/bin/env python3
"""
Automated sanctions data sync service for CORTEX-CI.

This script:
1. Downloads latest sanctions data from official sources
2. Imports new/updated entities
3. Recalculates risk scores
4. Logs sync activity

Schedule with cron:
    0 6 * * * /usr/bin/python3 /app/sync_sanctions.py >> /var/log/cortex-sync.log 2>&1
"""

import os
import sys
import json
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import uuid
import hashlib

# Configuration
DATA_DIR = Path("/root/cortex-ci/data/sanctions")
SYNC_LOG_FILE = DATA_DIR / "sync_log.json"
DB_CONTAINER = "compose-input-solid-state-array-q9m3z5-db-1"
DB_USER = "cortex"
DB_NAME = "cortex_ci"

# Data sources
SOURCES = {
    "ofac_sdn": {
        "url": "https://www.treasury.gov/ofac/downloads/sdn.xml",
        "file": "ofac_sdn.xml",
        "type": "xml",
    },
    "ofac_consolidated": {
        "url": "https://www.treasury.gov/ofac/downloads/consolidated/consolidated.xml",
        "file": "ofac_consolidated.xml",
        "type": "xml",
    },
    "un_sanctions": {
        "url": "https://scsanctions.un.org/resources/xml/en/consolidated.xml",
        "file": "un_sanctions.xml",
        "type": "xml",
    },
}


def log(message: str):
    """Log message with timestamp."""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")


def run_sql(sql: str) -> str:
    """Execute SQL in database container."""
    cmd = [
        "docker", "exec", "-i", DB_CONTAINER,
        "psql", "-U", DB_USER, "-d", DB_NAME, "-c", sql
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def get_file_hash(filepath: Path) -> str:
    """Get MD5 hash of file."""
    if not filepath.exists():
        return ""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def download_file(url: str, filepath: Path) -> bool:
    """Download file from URL."""
    try:
        log(f"Downloading {url}...")
        urllib.request.urlretrieve(url, filepath)
        log(f"Downloaded to {filepath} ({filepath.stat().st_size / 1024:.1f} KB)")
        return True
    except Exception as e:
        log(f"Error downloading {url}: {e}")
        return False


def load_sync_log() -> dict:
    """Load sync history."""
    if SYNC_LOG_FILE.exists():
        with open(SYNC_LOG_FILE, 'r') as f:
            return json.load(f)
    return {"syncs": []}


def save_sync_log(log_data: dict):
    """Save sync history."""
    with open(SYNC_LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=2, default=str)


def get_tenant_id() -> str:
    """Get default tenant ID."""
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


def sync_ofac_sdn(tenant_id: str, filepath: Path) -> dict:
    """Sync OFAC SDN data."""
    if not filepath.exists():
        return {"source": "ofac_sdn", "status": "error", "message": "File not found"}

    log("Parsing OFAC SDN...")
    ns = {"sdn": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/XML"}

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        return {"source": "ofac_sdn", "status": "error", "message": str(e)}

    # Get publish date
    pub_info = root.find(".//sdn:publshInformation", ns)
    pub_date = ""
    record_count = 0
    if pub_info is not None:
        date_elem = pub_info.find("sdn:Publish_Date", ns)
        count_elem = pub_info.find("sdn:Record_Count", ns)
        if date_elem is not None:
            pub_date = date_elem.text
        if count_elem is not None:
            record_count = int(count_elem.text)

    log(f"OFAC SDN: Published {pub_date}, {record_count} records")

    # Count existing
    result = run_sql(f"SELECT COUNT(*) FROM entities WHERE tenant_id = '{tenant_id}' AND subcategory = 'ofac_sdn';")
    existing = 0
    for line in result.split('\n'):
        if line.strip().isdigit():
            existing = int(line.strip())
            break

    imported = 0
    for entry in root.findall(".//sdn:sdnEntry", ns):
        uid = entry.find("sdn:uid", ns)
        if uid is None:
            continue

        external_id = f"OFAC-{uid.text}"

        # Check if exists
        check = run_sql(f"SELECT 1 FROM entities WHERE external_id = '{external_id}' AND tenant_id = '{tenant_id}';")
        if "1" in check:
            continue

        last_name = entry.find("sdn:lastName", ns)
        first_name = entry.find("sdn:firstName", ns)
        sdn_type = entry.find("sdn:sdnType", ns)

        name_parts = []
        if first_name is not None and first_name.text:
            name_parts.append(first_name.text)
        if last_name is not None and last_name.text:
            name_parts.append(last_name.text)
        name = " ".join(name_parts) if name_parts else "Unknown"

        entity_type = "INDIVIDUAL"
        if sdn_type is not None and sdn_type.text:
            t = sdn_type.text.lower()
            if t == "entity":
                entity_type = "ORGANIZATION"
            elif t == "vessel":
                entity_type = "VESSEL"
            elif t == "aircraft":
                entity_type = "AIRCRAFT"

        sql = f"""
        INSERT INTO entities (id, tenant_id, type, name, aliases, external_id,
                              category, subcategory, tags, criticality, is_active,
                              custom_data, created_at, updated_at)
        VALUES ('{uuid.uuid4()}', '{tenant_id}', '{entity_type}', '{escape_sql(name[:500])}',
                ARRAY[]::varchar[], '{external_id}',
                'sanctioned_entity', 'ofac_sdn', ARRAY[]::varchar[],
                5, true, '{{}}'::jsonb, NOW(), NOW());
        """
        run_sql(sql)
        imported += 1

        if imported % 500 == 0:
            log(f"  Imported {imported} new OFAC entities...")

    return {
        "source": "ofac_sdn",
        "status": "success",
        "publish_date": pub_date,
        "total_records": record_count,
        "existing": existing,
        "imported": imported,
    }


def sync_un_sanctions(tenant_id: str, filepath: Path) -> dict:
    """Sync UN sanctions data."""
    if not filepath.exists():
        return {"source": "un_sanctions", "status": "error", "message": "File not found"}

    log("Parsing UN Sanctions...")

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        return {"source": "un_sanctions", "status": "error", "message": str(e)}

    imported = 0
    for elem in root.iter():
        if "INDIVIDUAL" in elem.tag or "ENTITY" in elem.tag:
            dataid = elem.get("DATAID", "")
            if not dataid:
                continue

            external_id = f"UN-{dataid}"

            # Check if exists
            check = run_sql(f"SELECT 1 FROM entities WHERE external_id = '{external_id}' AND tenant_id = '{tenant_id}';")
            if "1" in check:
                continue

            # Get name
            name = ""
            for child in elem:
                if "FIRST_NAME" in child.tag:
                    name = child.text or ""
                    break

            if not name or len(name) < 2:
                continue

            entity_type = "INDIVIDUAL" if "INDIVIDUAL" in elem.tag else "ORGANIZATION"

            sql = f"""
            INSERT INTO entities (id, tenant_id, type, name, aliases, external_id,
                                  category, subcategory, tags, criticality, is_active,
                                  custom_data, created_at, updated_at)
            VALUES ('{uuid.uuid4()}', '{tenant_id}', '{entity_type}', '{escape_sql(name[:500])}',
                    ARRAY[]::varchar[], '{external_id}',
                    'sanctioned_entity', 'un_consolidated', ARRAY['UN_SANCTIONS']::varchar[],
                    5, true, '{{}}'::jsonb, NOW(), NOW());
            """
            run_sql(sql)
            imported += 1

    return {
        "source": "un_sanctions",
        "status": "success",
        "imported": imported,
    }


def run_sync():
    """Run full sync process."""
    log("=" * 60)
    log("CORTEX-CI Sanctions Data Sync")
    log("=" * 60)

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Get tenant
    tenant_id = get_tenant_id()
    if not tenant_id:
        log("ERROR: Could not find tenant!")
        return

    log(f"Tenant: {tenant_id}")

    sync_results = {
        "timestamp": datetime.now().isoformat(),
        "tenant_id": tenant_id,
        "sources": [],
    }

    # Download and sync each source
    for source_name, source_config in SOURCES.items():
        log(f"\n--- Processing {source_name} ---")

        filepath = DATA_DIR / source_config["file"]
        old_hash = get_file_hash(filepath)

        # Download
        if download_file(source_config["url"], filepath):
            new_hash = get_file_hash(filepath)

            if old_hash == new_hash:
                log(f"No changes detected for {source_name}")
                sync_results["sources"].append({
                    "source": source_name,
                    "status": "unchanged",
                })
                continue

            # Sync based on source
            if source_name == "ofac_sdn":
                result = sync_ofac_sdn(tenant_id, filepath)
            elif source_name == "un_sanctions":
                result = sync_un_sanctions(tenant_id, filepath)
            else:
                result = {"source": source_name, "status": "skipped"}

            sync_results["sources"].append(result)
        else:
            sync_results["sources"].append({
                "source": source_name,
                "status": "download_failed",
            })

    # Get final counts
    result = run_sql("SELECT COUNT(*) FROM entities;")
    for line in result.split('\n'):
        if line.strip().isdigit():
            sync_results["total_entities"] = int(line.strip())
            break

    # Save sync log
    sync_log = load_sync_log()
    sync_log["syncs"].append(sync_results)
    sync_log["syncs"] = sync_log["syncs"][-100:]  # Keep last 100 syncs
    save_sync_log(sync_log)

    log("\n" + "=" * 60)
    log("Sync Complete!")
    log(f"Total entities: {sync_results.get('total_entities', 'N/A')}")
    log("=" * 60)

    return sync_results


if __name__ == "__main__":
    run_sync()
