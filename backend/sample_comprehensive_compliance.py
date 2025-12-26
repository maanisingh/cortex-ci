#!/usr/bin/env python3
"""
Comprehensive Compliance Constraints for CORTEX-CI.
Full compliance framework for government and organizations - beyond just sanctions.

Categories covered:
- Data Privacy & Protection (GDPR, CCPA, HIPAA, etc.)
- Anti-Money Laundering (AML/KYC)
- Anti-Corruption & Bribery (FCPA, UK Bribery Act)
- Environmental Compliance (ESG, Carbon)
- Labor & Employment
- Cybersecurity & Information Security
- Financial Regulations
- Government Procurement
- AI/ML Governance
- Industry-Specific Compliance
- International Trade
- Corporate Governance

Run: python sample_comprehensive_compliance.py
"""

import json
import subprocess
import uuid
from datetime import datetime, date

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
# DATA PRIVACY & PROTECTION CONSTRAINTS
# ============================================================================
DATA_PRIVACY_CONSTRAINTS = [
    {
        "name": "GDPR - General Data Protection Regulation",
        "type": "gdpr",
        "severity": "critical",
        "description": "EU regulation on data protection and privacy for all individuals within the European Union and EEA",
        "source_document": "Regulation (EU) 2016/679",
        "external_url": "https://gdpr-info.eu/",
        "applies_to_countries": ["EU"],
        "risk_weight": 5.0,
        "tags": ["DATA_PRIVACY", "GDPR", "EU"],
    },
    {
        "name": "GDPR Article 17 - Right to Erasure",
        "type": "data_protection",
        "severity": "high",
        "description": "Right to be forgotten - data subjects can request deletion of personal data",
        "source_document": "GDPR Article 17",
        "external_url": "https://gdpr-info.eu/art-17-gdpr/",
        "applies_to_countries": ["EU"],
        "risk_weight": 4.5,
        "tags": ["DATA_PRIVACY", "GDPR", "DATA_DELETION"],
    },
    {
        "name": "GDPR Article 33 - Data Breach Notification",
        "type": "data_protection",
        "severity": "critical",
        "description": "72-hour notification requirement for personal data breaches to supervisory authority",
        "source_document": "GDPR Article 33",
        "external_url": "https://gdpr-info.eu/art-33-gdpr/",
        "applies_to_countries": ["EU"],
        "risk_weight": 5.0,
        "tags": ["DATA_PRIVACY", "GDPR", "BREACH_NOTIFICATION"],
    },
    {
        "name": "CCPA - California Consumer Privacy Act",
        "type": "ccpa",
        "severity": "high",
        "description": "California state data privacy law giving consumers control over personal information",
        "source_document": "California Civil Code 1798.100-1798.199",
        "external_url": "https://oag.ca.gov/privacy/ccpa",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["DATA_PRIVACY", "CCPA", "USA", "CALIFORNIA"],
    },
    {
        "name": "CPRA - California Privacy Rights Act",
        "type": "data_privacy",
        "severity": "high",
        "description": "Enhanced California privacy law expanding CCPA with additional consumer rights",
        "source_document": "Proposition 24",
        "external_url": "https://cppa.ca.gov/",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["DATA_PRIVACY", "CPRA", "USA", "CALIFORNIA"],
    },
    {
        "name": "HIPAA - Health Insurance Portability and Accountability Act",
        "type": "healthcare",
        "severity": "critical",
        "description": "US federal law protecting sensitive patient health information",
        "source_document": "Public Law 104-191",
        "external_url": "https://www.hhs.gov/hipaa/",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["HEALTHCARE", "HIPAA", "PHI"],
    },
    {
        "name": "HIPAA Security Rule",
        "type": "data_protection",
        "severity": "critical",
        "description": "Technical and administrative safeguards for electronic protected health information",
        "source_document": "45 CFR Part 160 and 164",
        "external_url": "https://www.hhs.gov/hipaa/for-professionals/security/",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["HEALTHCARE", "HIPAA", "SECURITY"],
    },
    {
        "name": "LGPD - Brazil General Data Protection Law",
        "type": "data_privacy",
        "severity": "high",
        "description": "Brazilian data protection law modeled after GDPR",
        "source_document": "Lei Geral de Protecao de Dados",
        "external_url": "https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd",
        "applies_to_countries": ["BR"],
        "risk_weight": 4.0,
        "tags": ["DATA_PRIVACY", "LGPD", "BRAZIL"],
    },
    {
        "name": "PIPL - China Personal Information Protection Law",
        "type": "data_privacy",
        "severity": "critical",
        "description": "Chinese comprehensive data privacy law with strict cross-border transfer requirements",
        "source_document": "PIPL",
        "external_url": "http://www.npc.gov.cn/npc/c30834/202108/a8c4e3672c74491a80b53a172bb753fe.shtml",
        "applies_to_countries": ["CN"],
        "risk_weight": 5.0,
        "tags": ["DATA_PRIVACY", "PIPL", "CHINA"],
    },
    {
        "name": "POPIA - South Africa Protection of Personal Information Act",
        "type": "data_privacy",
        "severity": "high",
        "description": "South African data protection legislation",
        "source_document": "Act No. 4 of 2013",
        "external_url": "https://popia.co.za/",
        "applies_to_countries": ["ZA"],
        "risk_weight": 3.5,
        "tags": ["DATA_PRIVACY", "POPIA", "SOUTH_AFRICA"],
    },
    {
        "name": "UK Data Protection Act 2018",
        "type": "data_protection",
        "severity": "high",
        "description": "UK implementation of GDPR principles post-Brexit",
        "source_document": "Data Protection Act 2018",
        "external_url": "https://www.gov.uk/data-protection",
        "applies_to_countries": ["GB"],
        "risk_weight": 4.5,
        "tags": ["DATA_PRIVACY", "UK_GDPR", "UK"],
    },
]

# ============================================================================
# ANTI-MONEY LAUNDERING & FINANCIAL CRIMES
# ============================================================================
AML_KYC_CONSTRAINTS = [
    {
        "name": "Bank Secrecy Act (BSA)",
        "type": "aml",
        "severity": "critical",
        "description": "US law requiring financial institutions to assist government in detecting money laundering",
        "source_document": "31 U.S.C. 5311-5330",
        "external_url": "https://www.fincen.gov/resources/statutes-and-regulations/bank-secrecy-act",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["AML", "BSA", "FINANCIAL"],
    },
    {
        "name": "USA PATRIOT Act - AML Requirements",
        "type": "aml",
        "severity": "critical",
        "description": "Enhanced AML requirements including customer identification programs",
        "source_document": "Public Law 107-56",
        "external_url": "https://www.fincen.gov/resources/statutes-and-regulations/usa-patriot-act",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["AML", "PATRIOT_ACT", "CIP"],
    },
    {
        "name": "FinCEN Customer Due Diligence Rule",
        "type": "kyc",
        "severity": "critical",
        "description": "Requirements to identify and verify beneficial owners of legal entity customers",
        "source_document": "31 CFR 1010.230",
        "external_url": "https://www.fincen.gov/resources/statutes-and-regulations/cdd-final-rule",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["KYC", "CDD", "BENEFICIAL_OWNERSHIP"],
    },
    {
        "name": "EU 6th Anti-Money Laundering Directive (6AMLD)",
        "type": "aml",
        "severity": "critical",
        "description": "EU directive expanding money laundering predicate offenses and criminal liability",
        "source_document": "Directive (EU) 2018/1673",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32018L1673",
        "applies_to_countries": ["EU"],
        "risk_weight": 5.0,
        "tags": ["AML", "6AMLD", "EU"],
    },
    {
        "name": "UK Money Laundering Regulations 2017",
        "type": "aml",
        "severity": "high",
        "description": "UK regulations implementing EU AML directives with enhanced due diligence requirements",
        "source_document": "SI 2017/692",
        "external_url": "https://www.legislation.gov.uk/uksi/2017/692",
        "applies_to_countries": ["GB"],
        "risk_weight": 4.5,
        "tags": ["AML", "UK", "MLR"],
    },
    {
        "name": "FATF Recommendations",
        "type": "aml",
        "severity": "critical",
        "description": "International standards on combating money laundering and terrorist financing",
        "source_document": "FATF 40 Recommendations",
        "external_url": "https://www.fatf-gafi.org/recommendations.html",
        "applies_to_countries": [],
        "risk_weight": 5.0,
        "tags": ["AML", "FATF", "INTERNATIONAL"],
    },
    {
        "name": "Suspicious Activity Reporting (SAR)",
        "type": "aml",
        "severity": "critical",
        "description": "Requirement to file reports of suspicious transactions",
        "source_document": "31 CFR 1020.320",
        "external_url": "https://www.fincen.gov/resources/filing-information",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["AML", "SAR", "REPORTING"],
    },
    {
        "name": "Currency Transaction Reporting (CTR)",
        "type": "aml",
        "severity": "high",
        "description": "Reports required for cash transactions exceeding $10,000",
        "source_document": "31 CFR 1010.311",
        "external_url": "https://www.fincen.gov/resources/filing-information",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["AML", "CTR", "REPORTING"],
    },
]

# ============================================================================
# ANTI-CORRUPTION & BRIBERY
# ============================================================================
ANTI_CORRUPTION_CONSTRAINTS = [
    {
        "name": "Foreign Corrupt Practices Act (FCPA)",
        "type": "anti_corruption",
        "severity": "critical",
        "description": "US law prohibiting bribery of foreign officials and requiring accurate books and records",
        "source_document": "15 U.S.C. 78dd-1",
        "external_url": "https://www.justice.gov/criminal-fraud/foreign-corrupt-practices-act",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["ANTI_CORRUPTION", "FCPA", "BRIBERY"],
    },
    {
        "name": "UK Bribery Act 2010",
        "type": "anti_corruption",
        "severity": "critical",
        "description": "UK law covering bribery and corruption with extraterritorial reach",
        "source_document": "Bribery Act 2010",
        "external_url": "https://www.legislation.gov.uk/ukpga/2010/23",
        "applies_to_countries": ["GB"],
        "risk_weight": 5.0,
        "tags": ["ANTI_CORRUPTION", "UK_BRIBERY_ACT", "BRIBERY"],
    },
    {
        "name": "OECD Anti-Bribery Convention",
        "type": "anti_corruption",
        "severity": "high",
        "description": "International convention criminalizing bribery of foreign public officials",
        "source_document": "OECD Convention",
        "external_url": "https://www.oecd.org/corruption/oecdantibriberyconvention.htm",
        "applies_to_countries": [],
        "risk_weight": 4.5,
        "tags": ["ANTI_CORRUPTION", "OECD", "INTERNATIONAL"],
    },
    {
        "name": "Brazil Clean Company Act",
        "type": "anti_corruption",
        "severity": "high",
        "description": "Brazilian anti-corruption law with strict liability for companies",
        "source_document": "Law 12.846/2013",
        "external_url": "http://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12846.htm",
        "applies_to_countries": ["BR"],
        "risk_weight": 4.0,
        "tags": ["ANTI_CORRUPTION", "BRAZIL", "CLEAN_COMPANY"],
    },
    {
        "name": "France Sapin II Law",
        "type": "anti_corruption",
        "severity": "high",
        "description": "French anti-corruption law requiring compliance programs",
        "source_document": "Law No. 2016-1691",
        "external_url": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000033558528",
        "applies_to_countries": ["FR"],
        "risk_weight": 4.0,
        "tags": ["ANTI_CORRUPTION", "FRANCE", "SAPIN_II"],
    },
]

# ============================================================================
# ENVIRONMENTAL, SOCIAL, GOVERNANCE (ESG)
# ============================================================================
ESG_CONSTRAINTS = [
    {
        "name": "EU Corporate Sustainability Reporting Directive (CSRD)",
        "type": "environmental",
        "severity": "high",
        "description": "EU directive requiring companies to report on sustainability matters",
        "source_document": "Directive (EU) 2022/2464",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022L2464",
        "applies_to_countries": ["EU"],
        "risk_weight": 4.0,
        "tags": ["ESG", "CSRD", "SUSTAINABILITY"],
    },
    {
        "name": "EU Taxonomy Regulation",
        "type": "environmental",
        "severity": "high",
        "description": "Classification system for sustainable economic activities",
        "source_document": "Regulation (EU) 2020/852",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32020R0852",
        "applies_to_countries": ["EU"],
        "risk_weight": 4.0,
        "tags": ["ESG", "TAXONOMY", "GREEN_FINANCE"],
    },
    {
        "name": "SEC Climate Disclosure Rules",
        "type": "environmental",
        "severity": "high",
        "description": "SEC requirements for climate-related disclosures in registration statements and annual reports",
        "source_document": "SEC Final Rule",
        "external_url": "https://www.sec.gov/rules/final/2024/33-11275.pdf",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["ESG", "CLIMATE", "SEC"],
    },
    {
        "name": "UK Modern Slavery Act 2015",
        "type": "labor",
        "severity": "high",
        "description": "Requirement for commercial organizations to publish slavery and human trafficking statements",
        "source_document": "Modern Slavery Act 2015",
        "external_url": "https://www.legislation.gov.uk/ukpga/2015/30",
        "applies_to_countries": ["GB"],
        "risk_weight": 4.0,
        "tags": ["ESG", "MODERN_SLAVERY", "SUPPLY_CHAIN"],
    },
    {
        "name": "German Supply Chain Due Diligence Act",
        "type": "supply_chain",
        "severity": "high",
        "description": "Requirements for human rights and environmental due diligence in supply chains",
        "source_document": "LkSG",
        "external_url": "https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/lieferkettensorgfaltspflichtengesetz.html",
        "applies_to_countries": ["DE"],
        "risk_weight": 4.0,
        "tags": ["ESG", "SUPPLY_CHAIN", "DUE_DILIGENCE"],
    },
    {
        "name": "Carbon Border Adjustment Mechanism (CBAM)",
        "type": "environmental",
        "severity": "high",
        "description": "EU carbon pricing mechanism for imports of carbon-intensive products",
        "source_document": "Regulation (EU) 2023/956",
        "external_url": "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
        "applies_to_countries": ["EU"],
        "risk_weight": 4.5,
        "tags": ["ESG", "CARBON", "CBAM"],
    },
    {
        "name": "Task Force on Climate-related Financial Disclosures (TCFD)",
        "type": "environmental",
        "severity": "medium",
        "description": "Framework for climate-related financial risk disclosures",
        "source_document": "TCFD Recommendations",
        "external_url": "https://www.fsb-tcfd.org/",
        "applies_to_countries": [],
        "risk_weight": 3.5,
        "tags": ["ESG", "TCFD", "CLIMATE"],
    },
]

# ============================================================================
# CYBERSECURITY & INFORMATION SECURITY
# ============================================================================
CYBERSECURITY_CONSTRAINTS = [
    {
        "name": "NIST Cybersecurity Framework",
        "type": "cybersecurity",
        "severity": "high",
        "description": "Voluntary framework for managing cybersecurity risk",
        "source_document": "NIST CSF 2.0",
        "external_url": "https://www.nist.gov/cyberframework",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["CYBERSECURITY", "NIST", "FRAMEWORK"],
    },
    {
        "name": "ISO 27001 Information Security Management",
        "type": "cybersecurity",
        "severity": "high",
        "description": "International standard for information security management systems",
        "source_document": "ISO/IEC 27001:2022",
        "external_url": "https://www.iso.org/standard/27001",
        "applies_to_countries": [],
        "risk_weight": 4.0,
        "tags": ["CYBERSECURITY", "ISO27001", "ISMS"],
    },
    {
        "name": "EU NIS2 Directive",
        "type": "cybersecurity",
        "severity": "critical",
        "description": "EU directive on security of network and information systems",
        "source_document": "Directive (EU) 2022/2555",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022L2555",
        "applies_to_countries": ["EU"],
        "risk_weight": 5.0,
        "tags": ["CYBERSECURITY", "NIS2", "EU"],
    },
    {
        "name": "SOC 2 Type II Compliance",
        "type": "audit",
        "severity": "high",
        "description": "Service organization control report on security, availability, processing integrity, confidentiality, and privacy",
        "source_document": "AICPA SOC 2",
        "external_url": "https://www.aicpa.org/topic/audit-assurance/audit-and-assurance-greater-than-soc-2",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["CYBERSECURITY", "SOC2", "AUDIT"],
    },
    {
        "name": "PCI DSS v4.0",
        "type": "cybersecurity",
        "severity": "critical",
        "description": "Payment Card Industry Data Security Standard for cardholder data protection",
        "source_document": "PCI DSS v4.0",
        "external_url": "https://www.pcisecuritystandards.org/",
        "applies_to_countries": [],
        "risk_weight": 5.0,
        "tags": ["CYBERSECURITY", "PCI_DSS", "PAYMENT"],
    },
    {
        "name": "CMMC 2.0 - Cybersecurity Maturity Model Certification",
        "type": "government",
        "severity": "critical",
        "description": "DoD cybersecurity requirements for defense industrial base",
        "source_document": "32 CFR Part 170",
        "external_url": "https://www.acq.osd.mil/cmmc/",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["CYBERSECURITY", "CMMC", "DOD"],
    },
    {
        "name": "FedRAMP Authorization",
        "type": "government",
        "severity": "critical",
        "description": "Federal Risk and Authorization Management Program for cloud services",
        "source_document": "FedRAMP",
        "external_url": "https://www.fedramp.gov/",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["CYBERSECURITY", "FEDRAMP", "CLOUD"],
    },
]

# ============================================================================
# FINANCIAL REGULATIONS
# ============================================================================
FINANCIAL_CONSTRAINTS = [
    {
        "name": "Dodd-Frank Wall Street Reform Act",
        "type": "financial",
        "severity": "critical",
        "description": "Comprehensive US financial regulatory reform",
        "source_document": "Public Law 111-203",
        "external_url": "https://www.cftc.gov/LawRegulation/DoddFrankAct/index.htm",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["FINANCIAL", "DODD_FRANK", "BANKING"],
    },
    {
        "name": "Basel III Capital Requirements",
        "type": "financial",
        "severity": "critical",
        "description": "International regulatory framework for bank capital adequacy",
        "source_document": "Basel III Framework",
        "external_url": "https://www.bis.org/bcbs/basel3.htm",
        "applies_to_countries": [],
        "risk_weight": 5.0,
        "tags": ["FINANCIAL", "BASEL_III", "BANKING"],
    },
    {
        "name": "MiFID II - Markets in Financial Instruments Directive",
        "type": "financial",
        "severity": "high",
        "description": "EU regulatory framework for investment services",
        "source_document": "Directive 2014/65/EU",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014L0065",
        "applies_to_countries": ["EU"],
        "risk_weight": 4.5,
        "tags": ["FINANCIAL", "MIFID", "INVESTMENT"],
    },
    {
        "name": "Sarbanes-Oxley Act (SOX)",
        "type": "audit",
        "severity": "critical",
        "description": "US law on corporate governance and financial disclosure",
        "source_document": "Public Law 107-204",
        "external_url": "https://www.soxlaw.com/",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["FINANCIAL", "SOX", "CORPORATE_GOVERNANCE"],
    },
    {
        "name": "EMIR - European Market Infrastructure Regulation",
        "type": "financial",
        "severity": "high",
        "description": "EU regulation on OTC derivatives, central counterparties and trade repositories",
        "source_document": "Regulation (EU) No 648/2012",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012R0648",
        "applies_to_countries": ["EU"],
        "risk_weight": 4.5,
        "tags": ["FINANCIAL", "EMIR", "DERIVATIVES"],
    },
]

# ============================================================================
# AI/ML GOVERNANCE
# ============================================================================
AI_GOVERNANCE_CONSTRAINTS = [
    {
        "name": "EU AI Act",
        "type": "ai_governance",
        "severity": "critical",
        "description": "EU regulation on artificial intelligence with risk-based approach",
        "source_document": "Regulation (EU) 2024/1689",
        "external_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
        "applies_to_countries": ["EU"],
        "risk_weight": 5.0,
        "tags": ["AI", "EU_AI_ACT", "HIGH_RISK"],
    },
    {
        "name": "NIST AI Risk Management Framework",
        "type": "ai_governance",
        "severity": "high",
        "description": "Framework for managing risks associated with AI systems",
        "source_document": "NIST AI RMF 1.0",
        "external_url": "https://www.nist.gov/itl/ai-risk-management-framework",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["AI", "NIST", "RISK_MANAGEMENT"],
    },
    {
        "name": "Colorado AI Act",
        "type": "ai_governance",
        "severity": "high",
        "description": "State law on algorithmic discrimination in high-risk AI systems",
        "source_document": "SB21-169",
        "external_url": "https://leg.colorado.gov/bills/sb21-169",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["AI", "ALGORITHMIC_DISCRIMINATION", "COLORADO"],
    },
    {
        "name": "NYC Local Law 144 - AI in Employment",
        "type": "algorithmic_accountability",
        "severity": "high",
        "description": "NYC law requiring bias audits for automated employment decision tools",
        "source_document": "Local Law 144",
        "external_url": "https://rules.cityofnewyork.us/rule/automated-employment-decision-tools/",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["AI", "EMPLOYMENT", "BIAS_AUDIT"],
    },
    {
        "name": "Model Risk Management (SR 11-7)",
        "type": "model_risk",
        "severity": "critical",
        "description": "Federal Reserve guidance on model risk management",
        "source_document": "SR Letter 11-7",
        "external_url": "https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["AI", "MODEL_RISK", "BANKING"],
    },
]

# ============================================================================
# GOVERNMENT & PUBLIC SECTOR
# ============================================================================
GOVERNMENT_CONSTRAINTS = [
    {
        "name": "FAR - Federal Acquisition Regulation",
        "type": "government",
        "severity": "critical",
        "description": "Primary regulation for federal government procurement",
        "source_document": "48 CFR Chapter 1",
        "external_url": "https://www.acquisition.gov/browse/index/far",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["GOVERNMENT", "FAR", "PROCUREMENT"],
    },
    {
        "name": "DFARS - Defense Federal Acquisition Regulation Supplement",
        "type": "government",
        "severity": "critical",
        "description": "DoD-specific supplement to FAR",
        "source_document": "48 CFR Chapter 2",
        "external_url": "https://www.acquisition.gov/dfars",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["GOVERNMENT", "DFARS", "DEFENSE"],
    },
    {
        "name": "ITAR - International Traffic in Arms Regulations",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on export of defense articles and services",
        "source_document": "22 CFR 120-130",
        "external_url": "https://www.pmddtc.state.gov/ddtc_public/ddtc_public?id=ddtc_kb_article_page&sys_id=24d528fddbfc930044f9ff621f961987",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["GOVERNMENT", "ITAR", "EXPORT_CONTROL"],
    },
    {
        "name": "EAR - Export Administration Regulations",
        "type": "export_control",
        "severity": "critical",
        "description": "Controls on export of dual-use items",
        "source_document": "15 CFR 730-774",
        "external_url": "https://www.bis.doc.gov/index.php/regulations/export-administration-regulations-ear",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["GOVERNMENT", "EAR", "EXPORT_CONTROL"],
    },
    {
        "name": "FISMA - Federal Information Security Management Act",
        "type": "government",
        "severity": "critical",
        "description": "Framework for protecting government information systems",
        "source_document": "Public Law 113-283",
        "external_url": "https://www.cisa.gov/topics/cyber-threats-and-advisories/federal-information-security-modernization-act",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["GOVERNMENT", "FISMA", "CYBERSECURITY"],
    },
    {
        "name": "Section 508 Accessibility",
        "type": "accessibility",
        "severity": "high",
        "description": "Federal accessibility requirements for electronic and information technology",
        "source_document": "29 U.S.C. 794d",
        "external_url": "https://www.section508.gov/",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["GOVERNMENT", "ACCESSIBILITY", "SECTION_508"],
    },
]

# ============================================================================
# INDUSTRY-SPECIFIC CONSTRAINTS
# ============================================================================
INDUSTRY_CONSTRAINTS = [
    {
        "name": "FDA 21 CFR Part 11",
        "type": "healthcare",
        "severity": "critical",
        "description": "FDA regulations on electronic records and signatures",
        "source_document": "21 CFR Part 11",
        "external_url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/part-11-electronic-records-electronic-signatures-scope-and-application",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["HEALTHCARE", "FDA", "ELECTRONIC_RECORDS"],
    },
    {
        "name": "GLBA - Gramm-Leach-Bliley Act",
        "type": "financial",
        "severity": "critical",
        "description": "Requirements for protection of consumer financial information",
        "source_document": "15 U.S.C. 6801-6809",
        "external_url": "https://www.ftc.gov/business-guidance/privacy-security/gramm-leach-bliley-act",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["FINANCIAL", "GLBA", "PRIVACY"],
    },
    {
        "name": "NERC CIP Standards",
        "type": "critical_infrastructure",
        "severity": "critical",
        "description": "Cybersecurity standards for the bulk electric system",
        "source_document": "NERC CIP Standards",
        "external_url": "https://www.nerc.com/pa/Stand/Pages/CIPStandards.aspx",
        "applies_to_countries": ["US"],
        "risk_weight": 5.0,
        "tags": ["ENERGY", "NERC_CIP", "CRITICAL_INFRASTRUCTURE"],
    },
    {
        "name": "FERPA - Family Educational Rights and Privacy Act",
        "type": "education",
        "severity": "high",
        "description": "Protection of student education records",
        "source_document": "20 U.S.C. 1232g",
        "external_url": "https://www.ed.gov/policy/gen/guid/fpco/ferpa/index.html",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["EDUCATION", "FERPA", "PRIVACY"],
    },
    {
        "name": "COPPA - Children's Online Privacy Protection Act",
        "type": "data_privacy",
        "severity": "high",
        "description": "Protections for children's personal information online",
        "source_document": "15 U.S.C. 6501-6506",
        "external_url": "https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa",
        "applies_to_countries": ["US"],
        "risk_weight": 4.5,
        "tags": ["DATA_PRIVACY", "COPPA", "CHILDREN"],
    },
]

# ============================================================================
# INTERNATIONAL TRADE
# ============================================================================
TRADE_CONSTRAINTS = [
    {
        "name": "USMCA Trade Agreement Compliance",
        "type": "trade_restriction",
        "severity": "high",
        "description": "United States-Mexico-Canada Agreement requirements",
        "source_document": "USMCA",
        "external_url": "https://ustr.gov/trade-agreements/free-trade-agreements/united-states-mexico-canada-agreement",
        "applies_to_countries": ["US", "MX", "CA"],
        "risk_weight": 3.5,
        "tags": ["TRADE", "USMCA", "NORTH_AMERICA"],
    },
    {
        "name": "Customs-Trade Partnership Against Terrorism (C-TPAT)",
        "type": "trade_restriction",
        "severity": "high",
        "description": "Voluntary supply chain security program",
        "source_document": "C-TPAT",
        "external_url": "https://www.cbp.gov/border-security/ports-entry/cargo-security/c-tpat-customs-trade-partnership-against-terrorism",
        "applies_to_countries": ["US"],
        "risk_weight": 3.5,
        "tags": ["TRADE", "C_TPAT", "SECURITY"],
    },
    {
        "name": "EU Customs Union Requirements",
        "type": "import_regulation",
        "severity": "high",
        "description": "EU customs procedures and requirements",
        "source_document": "Regulation (EU) No 952/2013",
        "external_url": "https://taxation-customs.ec.europa.eu/customs-4/union-customs-code_en",
        "applies_to_countries": ["EU"],
        "risk_weight": 4.0,
        "tags": ["TRADE", "EU_CUSTOMS", "IMPORT"],
    },
    {
        "name": "Anti-Dumping and Countervailing Duties",
        "type": "trade_restriction",
        "severity": "high",
        "description": "Trade remedy measures against unfair trade practices",
        "source_document": "19 U.S.C. 1671-1677",
        "external_url": "https://www.trade.gov/antidumping-and-countervailing-duties-ad-cvd",
        "applies_to_countries": ["US"],
        "risk_weight": 4.0,
        "tags": ["TRADE", "ANTIDUMPING", "CVD"],
    },
]


def load_all_constraints(tenant_id: str):
    """Load all comprehensive compliance constraints."""
    all_constraints = {
        "Data Privacy & Protection": DATA_PRIVACY_CONSTRAINTS,
        "AML & KYC": AML_KYC_CONSTRAINTS,
        "Anti-Corruption": ANTI_CORRUPTION_CONSTRAINTS,
        "ESG & Environmental": ESG_CONSTRAINTS,
        "Cybersecurity": CYBERSECURITY_CONSTRAINTS,
        "Financial Regulations": FINANCIAL_CONSTRAINTS,
        "AI Governance": AI_GOVERNANCE_CONSTRAINTS,
        "Government & Public Sector": GOVERNMENT_CONSTRAINTS,
        "Industry-Specific": INDUSTRY_CONSTRAINTS,
        "International Trade": TRADE_CONSTRAINTS,
    }

    total_loaded = 0

    for category, constraints in all_constraints.items():
        print(f"\n{'='*60}")
        print(f"Loading {len(constraints)} {category} constraints...")
        print(f"{'='*60}")

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
                '{{}}'::jsonb,
                NOW(),
                NOW()
            )
            ON CONFLICT DO NOTHING;
            """

            run_sql(sql)
            print(f"  [OK] {constraint['name']}")
            total_loaded += 1

    return total_loaded


def main():
    print("=" * 70)
    print("CORTEX-CI Comprehensive Compliance Constraints Loader")
    print("Full Compliance for Government and Organizations")
    print("=" * 70)

    tenant_id = get_tenant_id()
    if not tenant_id:
        print("ERROR: Could not find default tenant!")
        return

    print(f"Tenant: {tenant_id}")

    total = load_all_constraints(tenant_id)

    # Get final count
    result = run_sql(f"SELECT COUNT(*) FROM constraints WHERE tenant_id = '{tenant_id}';")
    for line in result.split("\n"):
        if line.strip().isdigit():
            print(f"\n{'='*70}")
            print(f"Total constraints loaded: {total}")
            print(f"Total constraints in database: {line.strip()}")
            print(f"{'='*70}")
            break


if __name__ == "__main__":
    main()
