#!/usr/bin/env python3
"""
Create Default Transaction Monitoring Rules

Creates a comprehensive set of AML/CFT monitoring rules based on regulatory requirements:
- FATF Recommendations
- FinCEN guidance
- EU AML Directives
- Industry best practices
"""
import asyncio
import json
import os
import sys
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text


# ============================================================================
# MONITORING RULES DEFINITIONS
# ============================================================================

MONITORING_RULES = [
    # ==========================================================================
    # THRESHOLD-BASED RULES
    # ==========================================================================
    {
        "rule_code": "THR-001",
        "name": "Large Cash Transaction",
        "description": "Detect cash transactions exceeding CTR threshold ($10,000 USD)",
        "rule_type": "THRESHOLD",
        "category": "AML",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "threshold",
            "field": "amount_usd",
            "operator": ">=",
            "value": 10000,
            "transaction_types": ["CASH_DEPOSIT", "CASH_WITHDRAWAL"]
        },
        "threshold_value": 10000,
        "threshold_currency": "USD",
        "regulatory_reference": "31 CFR 1010.311 - Currency Transaction Report"
    },
    {
        "rule_code": "THR-002",
        "name": "Large Wire Transfer",
        "description": "Detect wire transfers exceeding reporting threshold ($3,000 USD)",
        "rule_type": "THRESHOLD",
        "category": "AML",
        "default_severity": "LOW",
        "conditions": {
            "type": "threshold",
            "field": "amount_usd",
            "operator": ">=",
            "value": 3000,
            "transaction_types": ["WIRE_TRANSFER"]
        },
        "threshold_value": 3000,
        "threshold_currency": "USD",
        "regulatory_reference": "31 CFR 1010.410 - Recordkeeping"
    },
    {
        "rule_code": "THR-003",
        "name": "Very Large Transaction",
        "description": "Detect any transaction exceeding $50,000 USD",
        "rule_type": "THRESHOLD",
        "category": "AML",
        "default_severity": "HIGH",
        "conditions": {
            "type": "threshold",
            "field": "amount_usd",
            "operator": ">=",
            "value": 50000
        },
        "threshold_value": 50000,
        "threshold_currency": "USD",
        "regulatory_reference": "BSA/AML Enhanced Due Diligence"
    },

    # ==========================================================================
    # STRUCTURING DETECTION
    # ==========================================================================
    {
        "rule_code": "STR-001",
        "name": "Potential Structuring - Just Below Threshold",
        "description": "Multiple transactions just below $10,000 within 24 hours",
        "rule_type": "VELOCITY",
        "category": "AML",
        "default_severity": "HIGH",
        "conditions": {
            "type": "structuring",
            "amount_range": {"min": 9000, "max": 9999},
            "count": 2,
            "period": "24h",
            "same_customer": True
        },
        "velocity_count": 2,
        "velocity_period": "1d",
        "velocity_amount": 9000,
        "regulatory_reference": "31 USC 5324 - Structuring transactions"
    },
    {
        "rule_code": "STR-002",
        "name": "Rapid Sequential Deposits",
        "description": "Multiple deposits within short timeframe suggesting structuring",
        "rule_type": "VELOCITY",
        "category": "AML",
        "default_severity": "HIGH",
        "conditions": {
            "type": "velocity",
            "count": 3,
            "period": "2h",
            "transaction_types": ["CASH_DEPOSIT"],
            "cumulative_threshold": 10000
        },
        "velocity_count": 3,
        "velocity_period": "2h",
        "velocity_amount": 10000,
        "regulatory_reference": "FinCEN Structuring Guidance"
    },

    # ==========================================================================
    # GEOGRAPHIC RISK
    # ==========================================================================
    {
        "rule_code": "GEO-001",
        "name": "FATF Black List Country",
        "description": "Transaction involving FATF high-risk jurisdiction (call for action)",
        "rule_type": "GEOGRAPHIC",
        "category": "SANCTIONS",
        "default_severity": "CRITICAL",
        "conditions": {
            "type": "geographic",
            "countries": ["KP", "IR", "MM"],
            "fields": ["originator_bank_country", "beneficiary_bank_country", "correspondent_country"]
        },
        "regulatory_reference": "FATF High-Risk Jurisdictions"
    },
    {
        "rule_code": "GEO-002",
        "name": "FATF Grey List Country",
        "description": "Transaction involving FATF monitored jurisdiction",
        "rule_type": "GEOGRAPHIC",
        "category": "AML",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "geographic",
            "countries": ["BF", "CM", "CD", "HT", "KE", "ML", "MZ", "NG", "SN", "ZA", "PH", "VN", "SY", "AL", "BA", "JO", "TZ", "VE", "YE"],
            "fields": ["originator_bank_country", "beneficiary_bank_country"]
        },
        "regulatory_reference": "FATF Grey List - Increased Monitoring"
    },
    {
        "rule_code": "GEO-003",
        "name": "High Corruption Risk Country",
        "description": "Transaction to/from country with high corruption risk (CPI < 30)",
        "rule_type": "GEOGRAPHIC",
        "category": "AML",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "geographic",
            "countries": ["SO", "SS", "VE", "SY", "YE", "LY", "HT", "GQ", "TD", "TM", "BI", "CF", "CG", "GN", "AF", "IQ", "ER", "LA", "ZW"],
            "fields": ["originator_bank_country", "beneficiary_bank_country"]
        },
        "regulatory_reference": "Transparency International CPI"
    },
    {
        "rule_code": "GEO-004",
        "name": "Tax Haven Transaction",
        "description": "Large transaction involving known tax haven jurisdiction",
        "rule_type": "GEOGRAPHIC",
        "category": "AML",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "geographic_with_threshold",
            "countries": ["KY", "VG", "BM", "PA", "BZ", "LI", "MC", "GG", "JE", "IM", "GI", "AN", "MT", "CY", "LU"],
            "threshold": 25000
        },
        "regulatory_reference": "EU Tax Haven List"
    },

    # ==========================================================================
    # VELOCITY RULES
    # ==========================================================================
    {
        "rule_code": "VEL-001",
        "name": "High Transaction Velocity",
        "description": "Unusually high number of transactions in 24 hours",
        "rule_type": "VELOCITY",
        "category": "AML",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "velocity",
            "count": 10,
            "period": "24h"
        },
        "velocity_count": 10,
        "velocity_period": "1d",
        "regulatory_reference": "BSA/AML Suspicious Activity"
    },
    {
        "rule_code": "VEL-002",
        "name": "Rapid Wire Transfers",
        "description": "Multiple wire transfers in short succession",
        "rule_type": "VELOCITY",
        "category": "AML",
        "default_severity": "HIGH",
        "conditions": {
            "type": "velocity",
            "count": 5,
            "period": "1h",
            "transaction_types": ["WIRE_TRANSFER"]
        },
        "velocity_count": 5,
        "velocity_period": "1h",
        "regulatory_reference": "FinCEN Wire Transfer Rule"
    },
    {
        "rule_code": "VEL-003",
        "name": "High Daily Volume",
        "description": "Total transaction volume exceeds expected daily limit",
        "rule_type": "VELOCITY",
        "category": "AML",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "cumulative_threshold",
            "period": "24h",
            "threshold": 100000
        },
        "velocity_amount": 100000,
        "velocity_period": "1d",
        "regulatory_reference": "BSA/AML Suspicious Activity"
    },

    # ==========================================================================
    # PATTERN-BASED RULES
    # ==========================================================================
    {
        "rule_code": "PAT-001",
        "name": "Round Amount Transaction",
        "description": "Large transaction with suspiciously round amount",
        "rule_type": "PATTERN",
        "category": "AML",
        "default_severity": "LOW",
        "conditions": {
            "type": "pattern",
            "pattern": "round_amount",
            "threshold": 5000,
            "round_to": 1000
        },
        "regulatory_reference": "AML Pattern Detection"
    },
    {
        "rule_code": "PAT-002",
        "name": "In-Out Pattern",
        "description": "Funds received and quickly transferred out (layering)",
        "rule_type": "PATTERN",
        "category": "AML",
        "default_severity": "HIGH",
        "conditions": {
            "type": "in_out",
            "in_window": "24h",
            "out_window": "48h",
            "amount_match_tolerance": 0.1
        },
        "regulatory_reference": "FATF Typologies - Layering"
    },
    {
        "rule_code": "PAT-003",
        "name": "Dormant Account Activity",
        "description": "Sudden activity on previously dormant account",
        "rule_type": "PATTERN",
        "category": "AML",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "dormancy",
            "dormant_period": "90d",
            "activity_threshold": 5000
        },
        "regulatory_reference": "BSA/AML Account Monitoring"
    },

    # ==========================================================================
    # BEHAVIORAL RULES
    # ==========================================================================
    {
        "rule_code": "BEH-001",
        "name": "Unusual Transaction Time",
        "description": "Transaction initiated during unusual hours",
        "rule_type": "BEHAVIORAL",
        "category": "FRAUD",
        "default_severity": "LOW",
        "conditions": {
            "type": "time_based",
            "unusual_hours": {"start": "00:00", "end": "05:00"},
            "threshold": 5000
        },
        "regulatory_reference": "Fraud Detection Best Practices"
    },
    {
        "rule_code": "BEH-002",
        "name": "New Beneficiary High Value",
        "description": "Large transfer to newly added beneficiary",
        "rule_type": "BEHAVIORAL",
        "category": "FRAUD",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "new_counterparty",
            "threshold": 10000,
            "new_period": "7d"
        },
        "regulatory_reference": "Fraud Prevention"
    },
    {
        "rule_code": "BEH-003",
        "name": "Customer Risk Profile Mismatch",
        "description": "Transaction inconsistent with customer's expected activity",
        "rule_type": "BEHAVIORAL",
        "category": "AML",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "profile_mismatch",
            "deviation_threshold": 3.0
        },
        "regulatory_reference": "KYC Expected Activity Monitoring"
    },

    # ==========================================================================
    # HIGH-RISK CUSTOMER RULES
    # ==========================================================================
    {
        "rule_code": "HRC-001",
        "name": "PEP Transaction",
        "description": "Any transaction by Politically Exposed Person",
        "rule_type": "BEHAVIORAL",
        "category": "AML",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "customer_flag",
            "flag": "is_pep",
            "threshold": 1000
        },
        "applies_to_customers": ["HIGH", "VERY_HIGH"],
        "regulatory_reference": "FATF PEP Requirements"
    },
    {
        "rule_code": "HRC-002",
        "name": "High-Risk Customer Large Transaction",
        "description": "Large transaction by high-risk rated customer",
        "rule_type": "THRESHOLD",
        "category": "AML",
        "default_severity": "HIGH",
        "conditions": {
            "type": "threshold",
            "field": "amount_usd",
            "operator": ">=",
            "value": 5000,
            "customer_risk": ["HIGH", "VERY_HIGH"]
        },
        "threshold_value": 5000,
        "applies_to_customers": ["HIGH", "VERY_HIGH"],
        "regulatory_reference": "Enhanced Due Diligence"
    },

    # ==========================================================================
    # CRYPTO/DIGITAL ASSET RULES
    # ==========================================================================
    {
        "rule_code": "CRY-001",
        "name": "Crypto to Fiat Conversion",
        "description": "Large cryptocurrency conversion to fiat currency",
        "rule_type": "THRESHOLD",
        "category": "AML",
        "default_severity": "MEDIUM",
        "conditions": {
            "type": "threshold",
            "field": "amount_usd",
            "operator": ">=",
            "value": 10000,
            "transaction_types": ["CRYPTO_TRANSFER"]
        },
        "threshold_value": 10000,
        "applies_to_types": ["CRYPTO_TRANSFER"],
        "regulatory_reference": "FinCEN Virtual Currency Guidance"
    },

    # ==========================================================================
    # TRADE-BASED LAUNDERING
    # ==========================================================================
    {
        "rule_code": "TBL-001",
        "name": "Trade Invoice Mismatch",
        "description": "Trade payment significantly different from invoice value",
        "rule_type": "PATTERN",
        "category": "AML",
        "default_severity": "HIGH",
        "conditions": {
            "type": "invoice_mismatch",
            "deviation_threshold": 0.2
        },
        "applies_to_types": ["WIRE_TRANSFER", "TRADE"],
        "regulatory_reference": "FATF Trade-Based Money Laundering"
    }
]


async def create_monitoring_rules(session: AsyncSession, tenant_id: str):
    """Create all monitoring rules."""
    print("\n[Monitoring Rules] Creating default transaction monitoring rules...")

    rule_count = 0
    for rule in MONITORING_RULES:
        await session.execute(text("""
            INSERT INTO monitoring_rules (
                id, tenant_id, rule_code, name, description, rule_type, category,
                default_severity, conditions, threshold_value, threshold_currency,
                velocity_count, velocity_period, velocity_amount,
                applies_to_types, applies_to_customers, regulatory_reference,
                is_active, is_production, created_at, updated_at
            ) VALUES (
                :id, :tenant_id, :rule_code, :name, :description, :rule_type, :category,
                :default_severity, :conditions, :threshold_value, :threshold_currency,
                :velocity_count, :velocity_period, :velocity_amount,
                :applies_to_types, :applies_to_customers, :regulatory_reference,
                true, true, NOW(), NOW()
            )
            ON CONFLICT (rule_code) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                conditions = EXCLUDED.conditions,
                updated_at = NOW()
        """), {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "rule_code": rule["rule_code"],
            "name": rule["name"],
            "description": rule["description"],
            "rule_type": rule["rule_type"],
            "category": rule["category"],
            "default_severity": rule["default_severity"],
            "conditions": json.dumps(rule["conditions"]),
            "threshold_value": rule.get("threshold_value"),
            "threshold_currency": rule.get("threshold_currency"),
            "velocity_count": rule.get("velocity_count"),
            "velocity_period": rule.get("velocity_period"),
            "velocity_amount": rule.get("velocity_amount"),
            "applies_to_types": rule.get("applies_to_types", []),
            "applies_to_customers": rule.get("applies_to_customers", []),
            "regulatory_reference": rule.get("regulatory_reference")
        })
        rule_count += 1

    await session.commit()
    print(f"[Monitoring Rules] Created {rule_count} monitoring rules")
    return rule_count


async def main():
    """Run rule creation."""
    print("=" * 60)
    print("CREATE TRANSACTION MONITORING RULES")
    print("=" * 60)

    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/cortex_ci")
    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(text("SELECT id FROM tenants LIMIT 1"))
        row = result.fetchone()
        tenant_id = str(row[0]) if row else str(uuid4())

        await create_monitoring_rules(session, tenant_id)

    print("\n" + "=" * 60)
    print("MONITORING RULES CREATED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
