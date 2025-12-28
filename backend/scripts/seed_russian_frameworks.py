"""
Seed Russian Regulatory Frameworks
Comprehensive Russian compliance frameworks with controls for CORTEX platform.

Frameworks included:
- 152-FZ: Personal Data Protection
- 187-FZ: Critical Information Infrastructure
- 115-FZ: Anti-Money Laundering
- CBR 683-P: Information Security for Financial Organizations
- GOST R 57580.1-2017: Financial Sector Security
"""

import asyncio
import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models.compliance.framework import (
    Framework,
    FrameworkType,
    Control,
    ControlCategory,
)


# =============================================================================
# 152-FZ: Federal Law on Personal Data
# =============================================================================
FZ_152_CONTROLS = [
    # Chapter 1: General Provisions
    {"control_id": "152-FZ-1.1", "family": "General Provisions", "title": "Scope of Application", "description": "Define scope of personal data processing activities subject to the law", "category": ControlCategory.GOVERNANCE, "guidance": "Document all personal data processing activities and their legal basis"},
    {"control_id": "152-FZ-1.2", "family": "General Provisions", "title": "Personal Data Definition", "description": "Identify and classify all personal data processed by the organization", "category": ControlCategory.DATA_PROTECTION, "guidance": "Maintain data inventory with categories: general, special, biometric"},
    # Chapter 2: Principles and Conditions
    {"control_id": "152-FZ-2.1", "family": "Processing Principles", "title": "Lawful Processing", "description": "Ensure personal data processing is lawful and fair", "category": ControlCategory.COMPLIANCE, "guidance": "Document legal basis for each processing activity"},
    {"control_id": "152-FZ-2.2", "family": "Processing Principles", "title": "Purpose Limitation", "description": "Process personal data only for specified, explicit, and legitimate purposes", "category": ControlCategory.DATA_PROTECTION, "guidance": "Define and document purposes before processing begins"},
    {"control_id": "152-FZ-2.3", "family": "Processing Principles", "title": "Data Minimization", "description": "Limit personal data to what is necessary for processing purposes", "category": ControlCategory.DATA_PROTECTION, "guidance": "Review data collection practices regularly"},
    {"control_id": "152-FZ-2.4", "family": "Processing Principles", "title": "Accuracy", "description": "Ensure personal data is accurate and kept up to date", "category": ControlCategory.DATA_PROTECTION, "guidance": "Implement data quality procedures and correction mechanisms"},
    {"control_id": "152-FZ-2.5", "family": "Processing Principles", "title": "Storage Limitation", "description": "Retain personal data only as long as necessary", "category": ControlCategory.DATA_PROTECTION, "guidance": "Define retention periods and implement deletion procedures"},
    # Chapter 3: Data Subject Rights
    {"control_id": "152-FZ-3.1", "family": "Data Subject Rights", "title": "Consent Management", "description": "Obtain and manage data subject consent for processing", "category": ControlCategory.PRIVACY, "guidance": "Implement consent collection, storage, and withdrawal mechanisms"},
    {"control_id": "152-FZ-3.2", "family": "Data Subject Rights", "title": "Right to Information", "description": "Provide data subjects with information about processing", "category": ControlCategory.PRIVACY, "guidance": "Publish privacy notices and respond to information requests"},
    {"control_id": "152-FZ-3.3", "family": "Data Subject Rights", "title": "Right of Access", "description": "Allow data subjects to access their personal data", "category": ControlCategory.PRIVACY, "guidance": "Implement subject access request procedures within 30 days"},
    {"control_id": "152-FZ-3.4", "family": "Data Subject Rights", "title": "Right to Rectification", "description": "Allow data subjects to correct inaccurate personal data", "category": ControlCategory.PRIVACY, "guidance": "Implement data correction procedures"},
    {"control_id": "152-FZ-3.5", "family": "Data Subject Rights", "title": "Right to Deletion", "description": "Delete personal data upon request when processing is no longer necessary", "category": ControlCategory.PRIVACY, "guidance": "Implement secure deletion procedures"},
    {"control_id": "152-FZ-3.6", "family": "Data Subject Rights", "title": "Right to Object", "description": "Allow data subjects to object to processing", "category": ControlCategory.PRIVACY, "guidance": "Implement opt-out mechanisms and processing cessation procedures"},
    # Chapter 4: Operator Obligations
    {"control_id": "152-FZ-4.1", "family": "Operator Obligations", "title": "Roskomnadzor Notification", "description": "Register as personal data operator with Roskomnadzor", "category": ControlCategory.COMPLIANCE, "guidance": "Submit notification before processing and update annually"},
    {"control_id": "152-FZ-4.2", "family": "Operator Obligations", "title": "Data Protection Officer", "description": "Appoint responsible person for personal data protection", "category": ControlCategory.GOVERNANCE, "guidance": "Designate DPO with appropriate authority and resources"},
    {"control_id": "152-FZ-4.3", "family": "Operator Obligations", "title": "Internal Policies", "description": "Develop and publish personal data processing policies", "category": ControlCategory.GOVERNANCE, "guidance": "Create comprehensive policy document accessible to data subjects"},
    {"control_id": "152-FZ-4.4", "family": "Operator Obligations", "title": "Employee Training", "description": "Train employees on personal data protection requirements", "category": ControlCategory.AWARENESS_TRAINING, "guidance": "Conduct regular training and maintain training records"},
    {"control_id": "152-FZ-4.5", "family": "Operator Obligations", "title": "Internal Control", "description": "Implement internal control over personal data processing", "category": ControlCategory.AUDIT_LOGGING, "guidance": "Conduct regular audits and document findings"},
    # Chapter 5: Security Measures
    {"control_id": "152-FZ-5.1", "family": "Security Measures", "title": "Security System", "description": "Implement personal data protection security system", "category": ControlCategory.DATA_PROTECTION, "guidance": "Deploy technical and organizational measures per FSTEC requirements"},
    {"control_id": "152-FZ-5.2", "family": "Security Measures", "title": "Threat Assessment", "description": "Conduct security threat assessment for personal data systems", "category": ControlCategory.RISK_ASSESSMENT, "guidance": "Identify and document threats per FSTEC methodology"},
    {"control_id": "152-FZ-5.3", "family": "Security Measures", "title": "Protection Level", "description": "Determine required protection level for personal data", "category": ControlCategory.DATA_PROTECTION, "guidance": "Classify data and systems by protection level (1-4)"},
    {"control_id": "152-FZ-5.4", "family": "Security Measures", "title": "Incident Response", "description": "Implement incident response procedures for data breaches", "category": ControlCategory.INCIDENT_RESPONSE, "guidance": "Establish 24-hour notification to Roskomnadzor for breaches"},
    # Chapter 6: Cross-Border Transfer
    {"control_id": "152-FZ-6.1", "family": "Cross-Border Transfer", "title": "Data Localization", "description": "Store personal data of Russian citizens on servers in Russia", "category": ControlCategory.DATA_PROTECTION, "guidance": "Primary storage and databases must be located in Russian Federation"},
    {"control_id": "152-FZ-6.2", "family": "Cross-Border Transfer", "title": "Transfer Conditions", "description": "Ensure adequate protection for cross-border transfers", "category": ControlCategory.DATA_PROTECTION, "guidance": "Verify destination country provides adequate protection or use safeguards"},
    {"control_id": "152-FZ-6.3", "family": "Cross-Border Transfer", "title": "Transfer Documentation", "description": "Document all cross-border data transfers", "category": ControlCategory.COMPLIANCE, "guidance": "Maintain records of transfers including legal basis and safeguards"},
    # Chapter 7: Special Categories
    {"control_id": "152-FZ-7.1", "family": "Special Categories", "title": "Special Category Data", "description": "Apply enhanced protection for sensitive personal data", "category": ControlCategory.DATA_PROTECTION, "guidance": "Special categories include: race, health, political views, criminal records"},
    {"control_id": "152-FZ-7.2", "family": "Special Categories", "title": "Biometric Data", "description": "Apply specific requirements for biometric personal data", "category": ControlCategory.DATA_PROTECTION, "guidance": "Obtain written consent and implement enhanced security measures"},
]


# =============================================================================
# 187-FZ: Critical Information Infrastructure
# =============================================================================
FZ_187_CONTROLS = [
    {"control_id": "187-FZ-1.1", "family": "CII Categorization", "title": "CII Object Identification", "description": "Identify and inventory all critical information infrastructure objects", "category": ControlCategory.ASSET_MANAGEMENT, "guidance": "Document all information systems, networks, and automated control systems"},
    {"control_id": "187-FZ-1.2", "family": "CII Categorization", "title": "Significance Category Assignment", "description": "Assign significance category (1, 2, or 3) to CII objects", "category": ControlCategory.RISK_ASSESSMENT, "guidance": "Category 1 is highest significance, Category 3 is lowest"},
    {"control_id": "187-FZ-1.3", "family": "CII Categorization", "title": "FSTEC Registration", "description": "Register CII objects with FSTEC Russia", "category": ControlCategory.COMPLIANCE, "guidance": "Submit categorization results to FSTEC within 10 days"},
    {"control_id": "187-FZ-2.1", "family": "Security Requirements", "title": "Security Measures Implementation", "description": "Implement security measures based on CII category", "category": ControlCategory.DATA_PROTECTION, "guidance": "Follow FSTEC Order 239 requirements for each category"},
    {"control_id": "187-FZ-2.2", "family": "Security Requirements", "title": "Access Control", "description": "Implement access control for CII objects", "category": ControlCategory.ACCESS_CONTROL, "guidance": "Role-based access with privileged access management"},
    {"control_id": "187-FZ-2.3", "family": "Security Requirements", "title": "Network Security", "description": "Implement network security measures for CII", "category": ControlCategory.COMMUNICATIONS, "guidance": "Network segmentation, firewalls, intrusion detection"},
    {"control_id": "187-FZ-2.4", "family": "Security Requirements", "title": "Vulnerability Management", "description": "Conduct regular vulnerability assessments", "category": ControlCategory.VULNERABILITY_MANAGEMENT, "guidance": "Quarterly vulnerability scans, annual penetration testing"},
    {"control_id": "187-FZ-2.5", "family": "Security Requirements", "title": "Security Monitoring", "description": "Implement continuous security monitoring", "category": ControlCategory.AUDIT_LOGGING, "guidance": "Deploy SIEM, log collection, and analysis capabilities"},
    {"control_id": "187-FZ-3.1", "family": "GosSOPKA", "title": "GosSOPKA Connection", "description": "Connect to State System for Detection and Prevention of Computer Attacks", "category": ControlCategory.INCIDENT_RESPONSE, "guidance": "Establish technical connection to GosSOPKA center"},
    {"control_id": "187-FZ-3.2", "family": "GosSOPKA", "title": "Incident Reporting", "description": "Report computer incidents to GosSOPKA", "category": ControlCategory.INCIDENT_RESPONSE, "guidance": "Report incidents within 24 hours for Category 1, 48 hours for others"},
    {"control_id": "187-FZ-3.3", "family": "GosSOPKA", "title": "Threat Intelligence Sharing", "description": "Share and receive threat intelligence through GosSOPKA", "category": ControlCategory.INCIDENT_RESPONSE, "guidance": "Participate in threat information exchange"},
    {"control_id": "187-FZ-4.1", "family": "Organizational", "title": "Security Unit", "description": "Establish dedicated security unit for CII protection", "category": ControlCategory.GOVERNANCE, "guidance": "Appoint qualified personnel with appropriate authority"},
    {"control_id": "187-FZ-4.2", "family": "Organizational", "title": "Security Documentation", "description": "Develop CII security documentation", "category": ControlCategory.GOVERNANCE, "guidance": "Security policies, procedures, and operational documents"},
    {"control_id": "187-FZ-4.3", "family": "Organizational", "title": "Personnel Security", "description": "Implement personnel security measures", "category": ControlCategory.PERSONNEL_SECURITY, "guidance": "Background checks, access agreements, termination procedures"},
    {"control_id": "187-FZ-4.4", "family": "Organizational", "title": "Security Training", "description": "Conduct CII security awareness training", "category": ControlCategory.AWARENESS_TRAINING, "guidance": "Annual training for all personnel with CII access"},
    {"control_id": "187-FZ-5.1", "family": "Response", "title": "Incident Response Plan", "description": "Develop and maintain incident response plan", "category": ControlCategory.INCIDENT_RESPONSE, "guidance": "Include detection, containment, eradication, recovery phases"},
    {"control_id": "187-FZ-5.2", "family": "Response", "title": "Business Continuity", "description": "Implement business continuity measures for CII", "category": ControlCategory.BUSINESS_CONTINUITY, "guidance": "Backup, redundancy, and recovery capabilities"},
    {"control_id": "187-FZ-5.3", "family": "Response", "title": "Incident Testing", "description": "Conduct regular incident response exercises", "category": ControlCategory.INCIDENT_RESPONSE, "guidance": "Annual exercises with GosSOPKA coordination"},
]


# =============================================================================
# CBR 683-P: Information Security for Financial Organizations
# =============================================================================
CBR_683P_CONTROLS = [
    {"control_id": "683-P-1.1", "family": "Governance", "title": "Information Security Policy", "description": "Develop and maintain information security policy", "category": ControlCategory.GOVERNANCE, "guidance": "Board-approved policy covering all security domains"},
    {"control_id": "683-P-1.2", "family": "Governance", "title": "Security Organization", "description": "Establish information security organizational structure", "category": ControlCategory.GOVERNANCE, "guidance": "Define roles, responsibilities, and reporting lines"},
    {"control_id": "683-P-1.3", "family": "Governance", "title": "Risk Management", "description": "Implement information security risk management", "category": ControlCategory.RISK_ASSESSMENT, "guidance": "Identify, assess, and treat information security risks"},
    {"control_id": "683-P-2.1", "family": "Access Control", "title": "Identity Management", "description": "Implement identity and access management", "category": ControlCategory.IDENTIFICATION_AUTHENTICATION, "guidance": "Unique identification, authentication, authorization"},
    {"control_id": "683-P-2.2", "family": "Access Control", "title": "Privileged Access", "description": "Control privileged access to systems", "category": ControlCategory.ACCESS_CONTROL, "guidance": "PAM solutions, session recording, just-in-time access"},
    {"control_id": "683-P-2.3", "family": "Access Control", "title": "Access Review", "description": "Conduct periodic access rights review", "category": ControlCategory.ACCESS_CONTROL, "guidance": "Quarterly review of access rights and privileges"},
    {"control_id": "683-P-3.1", "family": "Data Protection", "title": "Data Classification", "description": "Classify information assets by sensitivity", "category": ControlCategory.ASSET_MANAGEMENT, "guidance": "Classification levels: public, internal, confidential, secret"},
    {"control_id": "683-P-3.2", "family": "Data Protection", "title": "Encryption", "description": "Implement cryptographic protection of data", "category": ControlCategory.CRYPTOGRAPHY, "guidance": "Use GOST cryptographic algorithms for sensitive data"},
    {"control_id": "683-P-3.3", "family": "Data Protection", "title": "Data Loss Prevention", "description": "Implement DLP controls", "category": ControlCategory.DATA_PROTECTION, "guidance": "Monitor and prevent unauthorized data exfiltration"},
    {"control_id": "683-P-4.1", "family": "Operations", "title": "Change Management", "description": "Implement change management process", "category": ControlCategory.CHANGE_MANAGEMENT, "guidance": "Formal change request, approval, and implementation process"},
    {"control_id": "683-P-4.2", "family": "Operations", "title": "Patch Management", "description": "Implement patch management process", "category": ControlCategory.VULNERABILITY_MANAGEMENT, "guidance": "Timely patching of systems and applications"},
    {"control_id": "683-P-4.3", "family": "Operations", "title": "Malware Protection", "description": "Implement malware protection", "category": ControlCategory.SYSTEM_SERVICES, "guidance": "Antivirus, endpoint detection and response"},
    {"control_id": "683-P-4.4", "family": "Operations", "title": "Backup and Recovery", "description": "Implement backup and recovery procedures", "category": ControlCategory.BUSINESS_CONTINUITY, "guidance": "Regular backups, tested recovery procedures"},
    {"control_id": "683-P-5.1", "family": "Network Security", "title": "Network Segmentation", "description": "Implement network segmentation", "category": ControlCategory.COMMUNICATIONS, "guidance": "Separate networks for different security zones"},
    {"control_id": "683-P-5.2", "family": "Network Security", "title": "Perimeter Security", "description": "Implement perimeter security controls", "category": ControlCategory.COMMUNICATIONS, "guidance": "Firewalls, IDS/IPS, WAF"},
    {"control_id": "683-P-5.3", "family": "Network Security", "title": "Secure Communications", "description": "Protect data in transit", "category": ControlCategory.COMMUNICATIONS, "guidance": "TLS/SSL, VPN for remote access"},
    {"control_id": "683-P-6.1", "family": "Monitoring", "title": "Security Monitoring", "description": "Implement security event monitoring", "category": ControlCategory.AUDIT_LOGGING, "guidance": "SIEM implementation, 24/7 monitoring"},
    {"control_id": "683-P-6.2", "family": "Monitoring", "title": "Incident Management", "description": "Implement incident management process", "category": ControlCategory.INCIDENT_RESPONSE, "guidance": "Detection, response, recovery, lessons learned"},
    {"control_id": "683-P-6.3", "family": "Monitoring", "title": "FinCERT Reporting", "description": "Report incidents to FinCERT", "category": ControlCategory.INCIDENT_RESPONSE, "guidance": "Report significant incidents within required timeframes"},
    {"control_id": "683-P-7.1", "family": "Third-Party", "title": "Vendor Assessment", "description": "Assess third-party security", "category": ControlCategory.SUPPLY_CHAIN, "guidance": "Due diligence before engagement, ongoing monitoring"},
    {"control_id": "683-P-7.2", "family": "Third-Party", "title": "Contractual Controls", "description": "Include security requirements in contracts", "category": ControlCategory.SUPPLY_CHAIN, "guidance": "SLAs, audit rights, incident notification"},
    {"control_id": "683-P-8.1", "family": "Assessment", "title": "Vulnerability Assessment", "description": "Conduct regular vulnerability assessments", "category": ControlCategory.SECURITY_ASSESSMENT, "guidance": "Quarterly vulnerability scanning"},
    {"control_id": "683-P-8.2", "family": "Assessment", "title": "Penetration Testing", "description": "Conduct penetration testing", "category": ControlCategory.SECURITY_ASSESSMENT, "guidance": "Annual penetration testing by qualified assessors"},
    {"control_id": "683-P-8.3", "family": "Assessment", "title": "Compliance Assessment", "description": "Conduct compliance assessments", "category": ControlCategory.COMPLIANCE, "guidance": "Annual assessment against CBR requirements"},
]


# =============================================================================
# GOST R 57580.1-2017: Financial Sector Security
# =============================================================================
GOST_57580_CONTROLS = [
    {"control_id": "GOST-ZOR-1", "family": "Organizational", "title": "Security Management System", "description": "Establish information security management system", "category": ControlCategory.GOVERNANCE, "guidance": "Aligned with ISO 27001 requirements"},
    {"control_id": "GOST-ZOR-2", "family": "Organizational", "title": "Security Roles and Responsibilities", "description": "Define security roles and responsibilities", "category": ControlCategory.GOVERNANCE, "guidance": "Clear accountability for security functions"},
    {"control_id": "GOST-ZOR-3", "family": "Organizational", "title": "Security Documentation", "description": "Maintain security documentation", "category": ControlCategory.GOVERNANCE, "guidance": "Policies, procedures, standards, guidelines"},
    {"control_id": "GOST-ZUP-1", "family": "Access Control", "title": "Identification and Authentication", "description": "Implement identification and authentication controls", "category": ControlCategory.IDENTIFICATION_AUTHENTICATION, "guidance": "Multi-factor authentication for critical systems"},
    {"control_id": "GOST-ZUP-2", "family": "Access Control", "title": "Access Rights Management", "description": "Manage access rights lifecycle", "category": ControlCategory.ACCESS_CONTROL, "guidance": "Provisioning, review, revocation processes"},
    {"control_id": "GOST-ZUP-3", "family": "Access Control", "title": "Privileged Access Control", "description": "Control privileged access", "category": ControlCategory.ACCESS_CONTROL, "guidance": "PAM implementation, session monitoring"},
    {"control_id": "GOST-ZKS-1", "family": "Cryptography", "title": "Cryptographic Key Management", "description": "Implement key management procedures", "category": ControlCategory.CRYPTOGRAPHY, "guidance": "Key generation, distribution, storage, destruction"},
    {"control_id": "GOST-ZKS-2", "family": "Cryptography", "title": "Encryption Implementation", "description": "Implement encryption for data protection", "category": ControlCategory.CRYPTOGRAPHY, "guidance": "GOST 34.10, GOST 34.11, GOST 34.12 algorithms"},
    {"control_id": "GOST-ZPS-1", "family": "Network", "title": "Network Architecture Security", "description": "Secure network architecture design", "category": ControlCategory.COMMUNICATIONS, "guidance": "DMZ, network segmentation, defense in depth"},
    {"control_id": "GOST-ZPS-2", "family": "Network", "title": "Network Traffic Protection", "description": "Protect network traffic", "category": ControlCategory.COMMUNICATIONS, "guidance": "Firewalls, IDS/IPS, traffic filtering"},
    {"control_id": "GOST-ZFZ-1", "family": "Physical", "title": "Physical Access Control", "description": "Control physical access to facilities", "category": ControlCategory.PHYSICAL_SECURITY, "guidance": "Access control systems, visitor management"},
    {"control_id": "GOST-ZFZ-2", "family": "Physical", "title": "Environmental Protection", "description": "Protect against environmental threats", "category": ControlCategory.PHYSICAL_SECURITY, "guidance": "Fire suppression, climate control, power protection"},
    {"control_id": "GOST-ZMZ-1", "family": "Monitoring", "title": "Security Event Logging", "description": "Implement security event logging", "category": ControlCategory.AUDIT_LOGGING, "guidance": "Comprehensive logging of security events"},
    {"control_id": "GOST-ZMZ-2", "family": "Monitoring", "title": "Security Event Analysis", "description": "Analyze security events", "category": ControlCategory.AUDIT_LOGGING, "guidance": "SIEM implementation, correlation rules"},
    {"control_id": "GOST-ZMZ-3", "family": "Monitoring", "title": "Security Metrics", "description": "Collect and report security metrics", "category": ControlCategory.AUDIT_LOGGING, "guidance": "KPIs, KRIs, management reporting"},
    {"control_id": "GOST-ZRI-1", "family": "Incident Response", "title": "Incident Response Process", "description": "Implement incident response process", "category": ControlCategory.INCIDENT_RESPONSE, "guidance": "Detection, analysis, containment, recovery"},
    {"control_id": "GOST-ZRI-2", "family": "Incident Response", "title": "Incident Communication", "description": "Communicate incidents to stakeholders", "category": ControlCategory.INCIDENT_RESPONSE, "guidance": "Internal and external communication procedures"},
    {"control_id": "GOST-ZNS-1", "family": "Continuity", "title": "Business Impact Analysis", "description": "Conduct business impact analysis", "category": ControlCategory.BUSINESS_CONTINUITY, "guidance": "Identify critical processes and recovery requirements"},
    {"control_id": "GOST-ZNS-2", "family": "Continuity", "title": "Continuity Planning", "description": "Develop business continuity plans", "category": ControlCategory.BUSINESS_CONTINUITY, "guidance": "Recovery strategies and procedures"},
    {"control_id": "GOST-ZNS-3", "family": "Continuity", "title": "Continuity Testing", "description": "Test business continuity plans", "category": ControlCategory.BUSINESS_CONTINUITY, "guidance": "Regular testing and plan updates"},
    {"control_id": "GOST-ZUZ-1", "family": "Vulnerability", "title": "Vulnerability Identification", "description": "Identify vulnerabilities in systems", "category": ControlCategory.VULNERABILITY_MANAGEMENT, "guidance": "Regular scanning, threat intelligence"},
    {"control_id": "GOST-ZUZ-2", "family": "Vulnerability", "title": "Vulnerability Remediation", "description": "Remediate identified vulnerabilities", "category": ControlCategory.VULNERABILITY_MANAGEMENT, "guidance": "Prioritized remediation based on risk"},
    {"control_id": "GOST-ZKP-1", "family": "Personnel", "title": "Personnel Screening", "description": "Screen personnel before employment", "category": ControlCategory.PERSONNEL_SECURITY, "guidance": "Background checks for sensitive positions"},
    {"control_id": "GOST-ZKP-2", "family": "Personnel", "title": "Security Awareness", "description": "Conduct security awareness training", "category": ControlCategory.AWARENESS_TRAINING, "guidance": "Regular training for all employees"},
]


# =============================================================================
# 115-FZ: Anti-Money Laundering
# =============================================================================
FZ_115_CONTROLS = [
    {"control_id": "115-FZ-1.1", "family": "Customer Due Diligence", "title": "Customer Identification", "description": "Identify and verify customer identity", "category": ControlCategory.COMPLIANCE, "guidance": "Collect and verify identification documents"},
    {"control_id": "115-FZ-1.2", "family": "Customer Due Diligence", "title": "Beneficial Ownership", "description": "Identify beneficial owners", "category": ControlCategory.COMPLIANCE, "guidance": "Determine ultimate beneficial owners with 25%+ control"},
    {"control_id": "115-FZ-1.3", "family": "Customer Due Diligence", "title": "Enhanced Due Diligence", "description": "Apply EDD for high-risk customers", "category": ControlCategory.COMPLIANCE, "guidance": "PEPs, high-risk jurisdictions, complex structures"},
    {"control_id": "115-FZ-2.1", "family": "Transaction Monitoring", "title": "Mandatory Control Transactions", "description": "Report transactions subject to mandatory control", "category": ControlCategory.COMPLIANCE, "guidance": "Cash transactions over 600,000 RUB and specified types"},
    {"control_id": "115-FZ-2.2", "family": "Transaction Monitoring", "title": "Suspicious Transaction Reporting", "description": "Report suspicious transactions to Rosfinmonitoring", "category": ControlCategory.COMPLIANCE, "guidance": "Submit STRs within 3 working days"},
    {"control_id": "115-FZ-3.1", "family": "Internal Controls", "title": "AML Program", "description": "Implement AML/CFT internal control program", "category": ControlCategory.GOVERNANCE, "guidance": "Board-approved program with designated responsible officer"},
    {"control_id": "115-FZ-3.2", "family": "Internal Controls", "title": "Risk-Based Approach", "description": "Apply risk-based approach to AML/CFT", "category": ControlCategory.RISK_ASSESSMENT, "guidance": "Assess and manage ML/TF risks"},
    {"control_id": "115-FZ-3.3", "family": "Internal Controls", "title": "Employee Training", "description": "Train employees on AML/CFT requirements", "category": ControlCategory.AWARENESS_TRAINING, "guidance": "Annual training for relevant personnel"},
    {"control_id": "115-FZ-3.4", "family": "Internal Controls", "title": "Record Keeping", "description": "Maintain AML/CFT records", "category": ControlCategory.AUDIT_LOGGING, "guidance": "Retain records for 5 years after relationship ends"},
]


# =============================================================================
# Main Seeding Function
# =============================================================================
async def seed_russian_frameworks(session: AsyncSession, tenant_id: str) -> dict:
    """Seed all Russian regulatory frameworks and controls."""
    results = {"frameworks_created": 0, "controls_created": 0, "errors": []}

    frameworks_data = [
        {"type": FrameworkType.FZ_152, "name": "152-FZ: Federal Law on Personal Data", "version": "2024", "description": "Russian Federal Law on Personal Data Protection", "publisher": "Government of the Russian Federation", "publication_date": date(2006, 7, 27), "source_url": "http://www.consultant.ru/document/cons_doc_LAW_61801/", "controls": FZ_152_CONTROLS},
        {"type": FrameworkType.FZ_187, "name": "187-FZ: Critical Information Infrastructure", "version": "2024", "description": "Russian Federal Law on Security of Critical Information Infrastructure", "publisher": "Government of the Russian Federation", "publication_date": date(2017, 7, 26), "source_url": "http://www.consultant.ru/document/cons_doc_LAW_220885/", "controls": FZ_187_CONTROLS},
        {"type": FrameworkType.FZ_115, "name": "115-FZ: Anti-Money Laundering", "version": "2024", "description": "Russian Federal Law on Countering Legalization of Criminal Proceeds", "publisher": "Government of the Russian Federation", "publication_date": date(2001, 8, 7), "source_url": "http://www.consultant.ru/document/cons_doc_LAW_32834/", "controls": FZ_115_CONTROLS},
        {"type": FrameworkType.CBR_683P, "name": "CBR 683-P: Information Security for Financial Organizations", "version": "2024", "description": "Central Bank of Russia information security requirements", "publisher": "Central Bank of Russia", "publication_date": date(2019, 4, 17), "source_url": "https://www.cbr.ru/", "controls": CBR_683P_CONTROLS},
        {"type": FrameworkType.GOST_57580, "name": "GOST R 57580.1-2017: Financial Sector Security", "version": "2017", "description": "Russian national standard for information security in financial sector", "publisher": "Rosstandart", "publication_date": date(2017, 8, 8), "source_url": "https://docs.cntd.ru/document/1200146534", "controls": GOST_57580_CONTROLS},
    ]

    for fw_data in frameworks_data:
        try:
            result = await session.execute(select(Framework).where(Framework.type == fw_data["type"], Framework.tenant_id == tenant_id))
            existing = result.scalar_one_or_none()
            if existing:
                print(f"Framework {fw_data['name']} already exists, skipping...")
                continue

            framework = Framework(id=uuid4(), tenant_id=tenant_id, type=fw_data["type"], name=fw_data["name"], version=fw_data["version"], description=fw_data["description"], publisher=fw_data["publisher"], publication_date=fw_data["publication_date"], source_url=fw_data["source_url"], total_controls=len(fw_data["controls"]), categories=list(set(c.get("family", "") for c in fw_data["controls"])), is_active=True, is_custom=False)
            session.add(framework)
            await session.flush()
            results["frameworks_created"] += 1

            for ctrl_data in fw_data["controls"]:
                control = Control(id=uuid4(), tenant_id=tenant_id, framework_id=framework.id, control_id=ctrl_data["control_id"], title=ctrl_data["title"], description=ctrl_data["description"], family=ctrl_data.get("family"), category=ctrl_data.get("category"), guidance=ctrl_data.get("guidance"))
                session.add(control)
                results["controls_created"] += 1

            print(f"Created framework: {fw_data['name']} with {len(fw_data['controls'])} controls")
        except Exception as e:
            results["errors"].append(f"Error creating {fw_data['name']}: {str(e)}")
            print(f"Error: {e}")

    await session.commit()
    return results


async def main():
    """Main entry point for seeding Russian frameworks."""
    tenant_id = "default"
    async with async_session_maker() as session:
        print("=" * 60)
        print("Seeding Russian Regulatory Frameworks")
        print("=" * 60)
        results = await seed_russian_frameworks(session, tenant_id)
        print("\n" + "=" * 60)
        print("Seeding Complete!")
        print(f"Frameworks created: {results['frameworks_created']}")
        print(f"Controls created: {results['controls_created']}")
        if results["errors"]:
            print(f"Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  - {error}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
