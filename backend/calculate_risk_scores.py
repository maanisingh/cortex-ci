#!/usr/bin/env python3
"""
Calculate risk scores for all entities in CORTEX-CI.

Risk factors:
- Country risk (based on sanctioned countries)
- Criticality level
- Source (OFAC = higher risk than generic)
- Entity type
"""

import subprocess
import uuid
from datetime import datetime

DB_CONTAINER = "compose-input-solid-state-array-q9m3z5-db-1"
DB_USER = "cortex"
DB_NAME = "cortex_ci"

# High-risk countries
HIGH_RISK_COUNTRIES = {
    "RU": 95,  # Russia
    "IR": 95,  # Iran
    "KP": 95,  # North Korea
    "SY": 90,  # Syria
    "CU": 85,  # Cuba
    "VE": 80,  # Venezuela
    "BY": 80,  # Belarus
    "MM": 75,  # Myanmar
    "AF": 70,  # Afghanistan
    "IQ": 65,  # Iraq
    "YE": 65,  # Yemen
    "LY": 65,  # Libya
    "SD": 65,  # Sudan
    "SO": 60,  # Somalia
    "CN": 50,  # China (elevated)
}

def run_sql(sql: str):
    """Execute SQL in the database container."""
    cmd = [
        "docker", "exec", "-i", DB_CONTAINER,
        "psql", "-U", DB_USER, "-d", DB_NAME, "-c", sql
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and "ERROR" in result.stderr:
        print(f"SQL Error: {result.stderr[:200]}")
    return result.stdout


def get_tenant_id():
    """Get the default tenant ID."""
    result = run_sql("SELECT id FROM tenants WHERE slug = 'default';")
    for line in result.split('\n'):
        line = line.strip()
        if line and '-' in line and len(line) == 36:
            return line
    return None


def calculate_scores():
    """Calculate risk scores for all entities without scores."""

    print("=" * 60)
    print("CORTEX-CI Risk Score Calculation")
    print("=" * 60)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("Error: Could not find tenant!")
        return

    print(f"Tenant: {tenant_id}")

    # Get entities without risk scores
    print("\nFetching entities without risk scores...")

    result = run_sql(f"""
        SELECT e.id, e.type, e.country_code, e.criticality, e.subcategory, e.tags
        FROM entities e
        LEFT JOIN risk_scores rs ON e.id = rs.entity_id
        WHERE rs.id IS NULL AND e.tenant_id = '{tenant_id}'
        LIMIT 20000;
    """)

    lines = result.strip().split('\n')
    if len(lines) < 3:
        print("No entities need scoring!")
        return

    # Parse results (skip header and separator)
    entities = []
    for line in lines[2:]:  # Skip header and ---
        if '|' not in line or line.strip().startswith('('):
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 6:
            entities.append({
                'id': parts[0],
                'type': parts[1],
                'country_code': parts[2] if parts[2] else None,
                'criticality': int(parts[3]) if parts[3].isdigit() else 3,
                'subcategory': parts[4],
                'tags': parts[5],
            })

    print(f"Found {len(entities)} entities to score")

    scored = 0
    for entity in entities:
        # Calculate base score
        base_score = 50.0

        # Country risk factor
        country_score = 0.0
        if entity['country_code'] and entity['country_code'] in HIGH_RISK_COUNTRIES:
            country_score = HIGH_RISK_COUNTRIES[entity['country_code']]

        # Criticality factor (1-5 scale -> 0-25 points)
        criticality_score = (entity['criticality'] / 5) * 25

        # Source factor
        source_score = 0.0
        if entity['subcategory'] == 'ofac_sdn':
            source_score = 30.0  # OFAC = high risk
        elif entity['subcategory'] == 'un_consolidated':
            source_score = 25.0  # UN = high risk
        elif entity['subcategory'] == 'opensanctions':
            source_score = 20.0  # OpenSanctions = elevated

        # Entity type factor
        type_score = 0.0
        if entity['type'] == 'INDIVIDUAL':
            type_score = 5.0  # Individuals slightly higher

        # Calculate composite score (weighted average)
        composite = (
            base_score * 0.10 +
            country_score * 0.35 +
            criticality_score * 0.15 +
            source_score * 0.30 +
            type_score * 0.10
        )

        # Normalize to 0-100
        composite = min(max(composite, 0), 100)

        # Determine risk level
        if composite >= 80:
            level = "CRITICAL"
        elif composite >= 60:
            level = "HIGH"
        elif composite >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"

        # Insert risk score
        sql = f"""
        INSERT INTO risk_scores (
            id, tenant_id, entity_id, score, level,
            direct_match_score, indirect_match_score,
            country_risk_score, dependency_risk_score,
            factors, calculated_at, calculation_version,
            created_at, updated_at
        ) VALUES (
            '{uuid.uuid4()}', '{tenant_id}', '{entity['id']}',
            {composite:.2f}, '{level}',
            {source_score:.2f}, 0.0,
            {country_score:.2f}, 0.0,
            '{{"country": {country_score:.2f}, "source": {source_score:.2f}, "criticality": {criticality_score:.2f}}}'::jsonb,
            NOW(), 'v1.0',
            NOW(), NOW()
        ) ON CONFLICT DO NOTHING;
        """
        run_sql(sql)
        scored += 1

        if scored % 1000 == 0:
            print(f"  Scored {scored} entities...")

    print(f"\nScored {scored} entities")

    # Show distribution
    print("\nRisk Score Distribution:")
    print(run_sql("""
        SELECT level, COUNT(*) as count,
               ROUND(AVG(score)::numeric, 2) as avg_score
        FROM risk_scores
        GROUP BY level
        ORDER BY avg_score DESC;
    """))

    # Show top 10 highest risk
    print("\nTop 10 Highest Risk Entities:")
    print(run_sql("""
        SELECT e.name, rs.score, rs.level, e.country_code
        FROM risk_scores rs
        JOIN entities e ON rs.entity_id = e.id
        ORDER BY rs.score DESC
        LIMIT 10;
    """))


if __name__ == "__main__":
    calculate_scores()
