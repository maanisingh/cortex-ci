#!/usr/bin/env python3
"""
Massive Data Generator (Phase 6)
Generates 1 billion+ data points for stress testing.

This script creates realistic synthetic data including:
- Entities (organizations, individuals, vessels, aircraft)
- Constraints (sanctions, regulatory)
- Dependencies (ownership, financial, operational)
- Risk scores and history
- Audit logs
- Scenarios and chains

Target: ~50GB of data with proper relationships
"""

import asyncio
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Country codes for realistic distribution
COUNTRIES = [
    "US", "GB", "DE", "FR", "CN", "RU", "IR", "KP", "SY", "CU",
    "JP", "KR", "IN", "BR", "AU", "CA", "MX", "ZA", "NG", "EG",
    "SA", "AE", "IL", "TR", "PK", "ID", "MY", "SG", "TH", "VN",
    "PH", "NL", "BE", "CH", "AT", "PL", "CZ", "SE", "NO", "DK",
    "FI", "IE", "PT", "ES", "IT", "GR", "UA", "BY", "KZ", "UZ",
]

# High-risk countries (for sanctions)
HIGH_RISK_COUNTRIES = ["IR", "KP", "SY", "CU", "RU", "BY", "VE", "MM"]

# Entity name components
COMPANY_PREFIXES = [
    "Global", "International", "United", "Pacific", "Atlantic",
    "Northern", "Southern", "Eastern", "Western", "Central",
    "First", "Premier", "Elite", "Prime", "Alpha", "Omega",
    "Trans", "Inter", "Multi", "Poly", "Uni", "Omni",
]

COMPANY_CORES = [
    "Trade", "Commerce", "Logistics", "Shipping", "Transport",
    "Finance", "Capital", "Investment", "Holdings", "Ventures",
    "Tech", "Systems", "Solutions", "Industries", "Manufacturing",
    "Energy", "Resources", "Mining", "Petroleum", "Chemical",
    "Pharma", "Medical", "Healthcare", "Bio", "Life",
]

COMPANY_SUFFIXES = [
    "Corp", "Inc", "Ltd", "LLC", "Group", "Company", "Co",
    "International", "Global", "Enterprises", "Partners",
    "Associates", "Services", "Trading", "Holdings",
]

FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David",
    "Richard", "Joseph", "Thomas", "Charles", "Christopher",
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara",
    "Elizabeth", "Susan", "Jessica", "Sarah", "Karen",
    "Mohammed", "Ahmed", "Ali", "Hassan", "Yusuf",
    "Wei", "Ming", "Jing", "Lei", "Xiu",
    "Dmitri", "Vladimir", "Sergei", "Alexei", "Ivan",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones",
    "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Kim", "Lee", "Park", "Choi", "Kang",
    "Chen", "Wang", "Li", "Zhang", "Liu",
    "Petrov", "Ivanov", "Volkov", "Kozlov", "Novikov",
    "Mueller", "Schmidt", "Schneider", "Fischer", "Weber",
]

VESSEL_PREFIXES = ["MV", "MT", "SS", "MS", "RV", "SV"]
VESSEL_NAMES = [
    "Pacific Star", "Atlantic Dawn", "Northern Spirit", "Southern Cross",
    "Ocean Pride", "Sea Dragon", "Blue Horizon", "Golden Eagle",
    "Crimson Wave", "Silver Moon", "Jade Fortune", "Ruby Princess",
]

CONSTRAINT_SOURCES = [
    "OFAC SDN List", "EU Sanctions", "UN Security Council",
    "UK Treasury", "Australia DFAT", "Canada SEMA",
    "Swiss SECO", "Japan METI", "Singapore MAS",
    "Financial Action Task Force", "Interpol Red Notice",
]

CONSTRAINT_TYPES = ["sanction", "regulatory", "watchlist", "pep", "adverse_media"]
SEVERITY_LEVELS = ["low", "medium", "high", "critical"]
ENTITY_TYPES = ["organization", "individual", "vessel", "aircraft"]
DEPENDENCY_TYPES = ["ownership", "financial", "operational", "legal", "family"]

class DataGenerator:
    """Generates massive amounts of realistic synthetic data."""

    def __init__(self, output_dir: str = "/tmp/cortex-data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.entity_ids: List[str] = []
        self.constraint_ids: List[str] = []
        self.tenant_id = str(uuid.uuid4())
        self.stats = {
            "entities": 0,
            "constraints": 0,
            "dependencies": 0,
            "risks": 0,
            "audit_logs": 0,
            "scenarios": 0,
            "historical": 0,
        }

    def generate_entity_name(self, entity_type: str) -> str:
        """Generate realistic entity name based on type."""
        if entity_type == "organization":
            prefix = random.choice(COMPANY_PREFIXES)
            core = random.choice(COMPANY_CORES)
            suffix = random.choice(COMPANY_SUFFIXES)
            return f"{prefix} {core} {suffix}"
        elif entity_type == "individual":
            return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        elif entity_type == "vessel":
            prefix = random.choice(VESSEL_PREFIXES)
            name = random.choice(VESSEL_NAMES)
            return f"{prefix} {name}"
        else:  # aircraft
            return f"Aircraft-{random.randint(100, 999)}-{random.choice(string.ascii_uppercase)}"

    def generate_entity(self, entity_type: str = None) -> Dict[str, Any]:
        """Generate a single entity record."""
        entity_type = entity_type or random.choice(ENTITY_TYPES)
        entity_id = str(uuid.uuid4())
        self.entity_ids.append(entity_id)

        country = random.choice(COUNTRIES)
        is_high_risk = country in HIGH_RISK_COUNTRIES

        # Generate risk score with distribution
        if is_high_risk:
            risk_score = random.gauss(75, 15)
        else:
            risk_score = random.gauss(40, 20)
        risk_score = max(0, min(100, risk_score))

        entity = {
            "id": entity_id,
            "tenant_id": self.tenant_id,
            "name": self.generate_entity_name(entity_type),
            "type": entity_type,
            "country": country,
            "description": f"Auto-generated {entity_type} for stress testing",
            "aliases": [f"Alias-{i}" for i in range(random.randint(0, 3))],
            "identifiers": {
                "registration": f"REG-{random.randint(10000, 99999)}",
                "tax_id": f"TAX-{random.randint(100000, 999999)}",
            },
            "metadata": {
                "source": "data_generator",
                "batch": datetime.utcnow().isoformat(),
                "risk_factors": random.randint(1, 10),
            },
            "is_active": random.random() > 0.05,
            "current_risk_score": round(risk_score, 2),
            "risk_level": (
                "critical" if risk_score >= 90
                else "high" if risk_score >= 75
                else "medium" if risk_score >= 50
                else "low"
            ),
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self.stats["entities"] += 1
        return entity

    def generate_constraint(self) -> Dict[str, Any]:
        """Generate a single constraint record."""
        constraint_id = str(uuid.uuid4())
        self.constraint_ids.append(constraint_id)

        effective_date = datetime.utcnow() - timedelta(days=random.randint(30, 1000))

        constraint = {
            "id": constraint_id,
            "tenant_id": self.tenant_id,
            "name": f"Constraint-{random.randint(10000, 99999)}",
            "type": random.choice(CONSTRAINT_TYPES),
            "severity": random.choice(SEVERITY_LEVELS),
            "source": random.choice(CONSTRAINT_SOURCES),
            "description": "Auto-generated constraint for stress testing",
            "effective_date": effective_date.isoformat(),
            "expiry_date": (
                (effective_date + timedelta(days=random.randint(365, 3650))).isoformat()
                if random.random() > 0.3 else None
            ),
            "is_active": random.random() > 0.1,
            "metadata": {
                "program": f"Program-{random.randint(1, 50)}",
                "reference": f"REF-{random.randint(10000, 99999)}",
            },
            "created_at": effective_date.isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self.stats["constraints"] += 1
        return constraint

    def generate_dependency(self) -> Dict[str, Any]:
        """Generate a single dependency record."""
        if len(self.entity_ids) < 2:
            return None

        source_id = random.choice(self.entity_ids)
        target_id = random.choice(self.entity_ids)
        while target_id == source_id:
            target_id = random.choice(self.entity_ids)

        dependency = {
            "id": str(uuid.uuid4()),
            "tenant_id": self.tenant_id,
            "source_entity_id": source_id,
            "target_entity_id": target_id,
            "type": random.choice(DEPENDENCY_TYPES),
            "strength": round(random.random(), 2),
            "description": "Auto-generated dependency",
            "metadata": {
                "confidence": round(random.random(), 2),
                "verified": random.random() > 0.5,
            },
            "is_active": random.random() > 0.1,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.stats["dependencies"] += 1
        return dependency

    def generate_risk_history(self, entity_id: str, days: int = 365) -> List[Dict]:
        """Generate risk history for an entity."""
        records = []
        base_score = random.uniform(20, 80)

        for day in range(days):
            date = datetime.utcnow() - timedelta(days=days - day)
            # Random walk with drift
            base_score += random.gauss(0, 2)
            base_score = max(0, min(100, base_score))

            records.append({
                "id": str(uuid.uuid4()),
                "tenant_id": self.tenant_id,
                "entity_id": entity_id,
                "date": date.strftime("%Y-%m-%d"),
                "score": round(base_score, 2),
                "factors": {
                    "sanctions": random.randint(0, 10),
                    "pep": random.randint(0, 5),
                    "adverse_media": random.randint(0, 8),
                    "jurisdiction": random.randint(0, 10),
                },
            })
            self.stats["historical"] += 1

        return records

    def generate_audit_log(self) -> Dict[str, Any]:
        """Generate a single audit log entry."""
        actions = ["CREATE", "UPDATE", "DELETE", "VIEW", "EXPORT", "LOGIN", "LOGOUT"]
        resources = ["entity", "constraint", "dependency", "risk", "scenario", "user"]

        log = {
            "id": str(uuid.uuid4()),
            "tenant_id": self.tenant_id,
            "user_id": str(uuid.uuid4()),
            "user_email": f"user{random.randint(1, 1000)}@example.com",
            "action": random.choice(actions),
            "resource_type": random.choice(resources),
            "resource_id": str(uuid.uuid4()),
            "description": "Auto-generated audit log",
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "success": random.random() > 0.02,
            "created_at": (datetime.utcnow() - timedelta(
                seconds=random.randint(0, 86400 * 30)
            )).isoformat(),
        }
        self.stats["audit_logs"] += 1
        return log

    def generate_scenario(self) -> Dict[str, Any]:
        """Generate a scenario."""
        scenario = {
            "id": str(uuid.uuid4()),
            "tenant_id": self.tenant_id,
            "name": f"Scenario-{random.randint(10000, 99999)}",
            "description": "Auto-generated scenario",
            "status": random.choice(["draft", "active", "completed"]),
            "parameters": {
                "risk_threshold": random.randint(50, 90),
                "entity_types": random.sample(ENTITY_TYPES, k=random.randint(1, 3)),
            },
            "results": {
                "entities_affected": random.randint(10, 1000),
                "risk_increase": round(random.uniform(5, 30), 2),
            },
            "created_at": datetime.utcnow().isoformat(),
        }
        self.stats["scenarios"] += 1
        return scenario

    def write_batch(self, records: List[Dict], filename: str):
        """Write a batch of records to a JSONL file."""
        filepath = self.output_dir / filename
        with open(filepath, "a") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")

    async def generate_all(
        self,
        num_entities: int = 1000000,
        num_constraints: int = 100000,
        num_dependencies: int = 5000000,
        num_audit_logs: int = 10000000,
        num_scenarios: int = 10000,
        batch_size: int = 10000,
    ):
        """Generate all data types."""
        print("=" * 60)
        print("CORTEX-CI Massive Data Generator")
        print("=" * 60)
        print(f"Target: {num_entities:,} entities")
        print(f"Target: {num_constraints:,} constraints")
        print(f"Target: {num_dependencies:,} dependencies")
        print(f"Target: {num_audit_logs:,} audit logs")
        print(f"Target: {num_scenarios:,} scenarios")
        print(f"Output: {self.output_dir}")
        print("=" * 60)

        # Generate entities
        print("\n[1/6] Generating entities...")
        batch = []
        for i in range(num_entities):
            batch.append(self.generate_entity())
            if len(batch) >= batch_size:
                self.write_batch(batch, "entities.jsonl")
                batch = []
                if i % 100000 == 0:
                    print(f"  Progress: {i:,}/{num_entities:,}")

        if batch:
            self.write_batch(batch, "entities.jsonl")

        # Generate constraints
        print("\n[2/6] Generating constraints...")
        batch = []
        for i in range(num_constraints):
            batch.append(self.generate_constraint())
            if len(batch) >= batch_size:
                self.write_batch(batch, "constraints.jsonl")
                batch = []
                if i % 10000 == 0:
                    print(f"  Progress: {i:,}/{num_constraints:,}")

        if batch:
            self.write_batch(batch, "constraints.jsonl")

        # Generate dependencies
        print("\n[3/6] Generating dependencies...")
        batch = []
        for i in range(num_dependencies):
            dep = self.generate_dependency()
            if dep:
                batch.append(dep)
            if len(batch) >= batch_size:
                self.write_batch(batch, "dependencies.jsonl")
                batch = []
                if i % 500000 == 0:
                    print(f"  Progress: {i:,}/{num_dependencies:,}")

        if batch:
            self.write_batch(batch, "dependencies.jsonl")

        # Generate risk history for sample entities
        print("\n[4/6] Generating risk history...")
        sample_entities = self.entity_ids[:min(10000, len(self.entity_ids))]
        batch = []
        for i, entity_id in enumerate(sample_entities):
            history = self.generate_risk_history(entity_id, days=365)
            batch.extend(history)
            if len(batch) >= batch_size:
                self.write_batch(batch, "risk_history.jsonl")
                batch = []
            if i % 1000 == 0:
                print(f"  Progress: {i:,}/{len(sample_entities):,}")

        if batch:
            self.write_batch(batch, "risk_history.jsonl")

        # Generate audit logs
        print("\n[5/6] Generating audit logs...")
        batch = []
        for i in range(num_audit_logs):
            batch.append(self.generate_audit_log())
            if len(batch) >= batch_size:
                self.write_batch(batch, "audit_logs.jsonl")
                batch = []
                if i % 1000000 == 0:
                    print(f"  Progress: {i:,}/{num_audit_logs:,}")

        if batch:
            self.write_batch(batch, "audit_logs.jsonl")

        # Generate scenarios
        print("\n[6/6] Generating scenarios...")
        batch = []
        for i in range(num_scenarios):
            batch.append(self.generate_scenario())
            if len(batch) >= batch_size:
                self.write_batch(batch, "scenarios.jsonl")
                batch = []

        if batch:
            self.write_batch(batch, "scenarios.jsonl")

        # Print summary
        print("\n" + "=" * 60)
        print("GENERATION COMPLETE")
        print("=" * 60)
        for key, value in self.stats.items():
            print(f"  {key}: {value:,}")

        # Calculate file sizes
        total_size = 0
        for file in self.output_dir.glob("*.jsonl"):
            size = file.stat().st_size
            total_size += size
            print(f"  {file.name}: {size / (1024**2):.2f} MB")

        print(f"\nTotal size: {total_size / (1024**3):.2f} GB")
        print(f"Output directory: {self.output_dir}")


async def main():
    """Main entry point."""
    generator = DataGenerator()

    # Scale parameters for ~50GB target
    # Adjust these based on available disk space
    await generator.generate_all(
        num_entities=500000,        # 500K entities
        num_constraints=50000,       # 50K constraints
        num_dependencies=2000000,    # 2M dependencies
        num_audit_logs=5000000,      # 5M audit logs
        num_scenarios=5000,          # 5K scenarios
        batch_size=10000,
    )


if __name__ == "__main__":
    asyncio.run(main())
