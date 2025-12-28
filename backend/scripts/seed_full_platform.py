"""
Comprehensive Platform Seed Script
Seeds the entire platform with realistic compliance data
"""
import asyncio
import random
from uuid import uuid4
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models import User, Tenant
from app.models.compliance.framework import (
    Framework, Control, FrameworkType, ControlCategory, AssessmentResult
)
from app.models.compliance.customer import (
    Customer, CustomerType, CustomerStatus, CustomerRiskRating
)
from app.models.compliance.transaction import (
    Transaction, TransactionType, TransactionStatus,
    MonitoringRule, RuleType, AlertSeverity
)
from app.models.compliance.case import (
    Case, CaseType, CaseStatus, CasePriority
)
from app.models.compliance.training import (
    Course, CourseType, CourseStatus, TrainingAssignment, AssignmentStatus
)


# ============================================================
# COMPLIANCE FRAMEWORKS DATA
# ============================================================

FRAMEWORKS = [
    {
        "type": FrameworkType.ISO_27001,
        "name": "ISO/IEC 27001:2022",
        "version": "2022",
        "description": "Information Security Management System (ISMS) standard",
        "publisher": "International Organization for Standardization",
        "controls": [
            # Organizational Controls (A.5)
            ("A.5.1", "Policies for information security", ControlCategory.GOVERNANCE),
            ("A.5.2", "Information security roles and responsibilities", ControlCategory.GOVERNANCE),
            ("A.5.3", "Segregation of duties", ControlCategory.ACCESS_CONTROL),
            ("A.5.4", "Management responsibilities", ControlCategory.GOVERNANCE),
            ("A.5.5", "Contact with authorities", ControlCategory.COMPLIANCE),
            ("A.5.6", "Contact with special interest groups", ControlCategory.COMPLIANCE),
            ("A.5.7", "Threat intelligence", ControlCategory.RISK_ASSESSMENT),
            ("A.5.8", "Information security in project management", ControlCategory.GOVERNANCE),
            ("A.5.9", "Inventory of information and associated assets", ControlCategory.ASSET_MANAGEMENT),
            ("A.5.10", "Acceptable use of information and associated assets", ControlCategory.GOVERNANCE),
            ("A.5.11", "Return of assets", ControlCategory.ASSET_MANAGEMENT),
            ("A.5.12", "Classification of information", ControlCategory.DATA_PROTECTION),
            ("A.5.13", "Labelling of information", ControlCategory.DATA_PROTECTION),
            ("A.5.14", "Information transfer", ControlCategory.COMMUNICATIONS),
            ("A.5.15", "Access control", ControlCategory.ACCESS_CONTROL),
            ("A.5.16", "Identity management", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("A.5.17", "Authentication information", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("A.5.18", "Access rights", ControlCategory.ACCESS_CONTROL),
            ("A.5.19", "Information security in supplier relationships", ControlCategory.SUPPLY_CHAIN),
            ("A.5.20", "Addressing information security within supplier agreements", ControlCategory.SUPPLY_CHAIN),
            ("A.5.21", "Managing information security in the ICT supply chain", ControlCategory.SUPPLY_CHAIN),
            ("A.5.22", "Monitoring, review and change management of supplier services", ControlCategory.SUPPLY_CHAIN),
            ("A.5.23", "Information security for use of cloud services", ControlCategory.SUPPLY_CHAIN),
            ("A.5.24", "Information security incident management planning and preparation", ControlCategory.INCIDENT_RESPONSE),
            ("A.5.25", "Assessment and decision on information security events", ControlCategory.INCIDENT_RESPONSE),
            ("A.5.26", "Response to information security incidents", ControlCategory.INCIDENT_RESPONSE),
            ("A.5.27", "Learning from information security incidents", ControlCategory.INCIDENT_RESPONSE),
            ("A.5.28", "Collection of evidence", ControlCategory.INCIDENT_RESPONSE),
            ("A.5.29", "Information security during disruption", ControlCategory.BUSINESS_CONTINUITY),
            ("A.5.30", "ICT readiness for business continuity", ControlCategory.BUSINESS_CONTINUITY),
            ("A.5.31", "Legal, statutory, regulatory and contractual requirements", ControlCategory.COMPLIANCE),
            ("A.5.32", "Intellectual property rights", ControlCategory.COMPLIANCE),
            ("A.5.33", "Protection of records", ControlCategory.DATA_PROTECTION),
            ("A.5.34", "Privacy and protection of PII", ControlCategory.PRIVACY),
            ("A.5.35", "Independent review of information security", ControlCategory.SECURITY_ASSESSMENT),
            ("A.5.36", "Compliance with policies, rules and standards", ControlCategory.COMPLIANCE),
            ("A.5.37", "Documented operating procedures", ControlCategory.GOVERNANCE),
            # People Controls (A.6)
            ("A.6.1", "Screening", ControlCategory.PERSONNEL_SECURITY),
            ("A.6.2", "Terms and conditions of employment", ControlCategory.PERSONNEL_SECURITY),
            ("A.6.3", "Information security awareness, education and training", ControlCategory.AWARENESS_TRAINING),
            ("A.6.4", "Disciplinary process", ControlCategory.PERSONNEL_SECURITY),
            ("A.6.5", "Responsibilities after termination or change of employment", ControlCategory.PERSONNEL_SECURITY),
            ("A.6.6", "Confidentiality or non-disclosure agreements", ControlCategory.PERSONNEL_SECURITY),
            ("A.6.7", "Remote working", ControlCategory.ACCESS_CONTROL),
            ("A.6.8", "Information security event reporting", ControlCategory.INCIDENT_RESPONSE),
            # Physical Controls (A.7)
            ("A.7.1", "Physical security perimeters", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.2", "Physical entry", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.3", "Securing offices, rooms and facilities", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.4", "Physical security monitoring", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.5", "Protecting against physical and environmental threats", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.6", "Working in secure areas", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.7", "Clear desk and clear screen", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.8", "Equipment siting and protection", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.9", "Security of assets off-premises", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.10", "Storage media", ControlCategory.MEDIA_PROTECTION),
            ("A.7.11", "Supporting utilities", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.12", "Cabling security", ControlCategory.PHYSICAL_SECURITY),
            ("A.7.13", "Equipment maintenance", ControlCategory.MAINTENANCE),
            ("A.7.14", "Secure disposal or re-use of equipment", ControlCategory.MEDIA_PROTECTION),
            # Technological Controls (A.8)
            ("A.8.1", "User endpoint devices", ControlCategory.CONFIGURATION_MANAGEMENT),
            ("A.8.2", "Privileged access rights", ControlCategory.ACCESS_CONTROL),
            ("A.8.3", "Information access restriction", ControlCategory.ACCESS_CONTROL),
            ("A.8.4", "Access to source code", ControlCategory.ACCESS_CONTROL),
            ("A.8.5", "Secure authentication", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("A.8.6", "Capacity management", ControlCategory.SYSTEM_SERVICES),
            ("A.8.7", "Protection against malware", ControlCategory.SYSTEM_SERVICES),
            ("A.8.8", "Management of technical vulnerabilities", ControlCategory.VULNERABILITY_MANAGEMENT),
            ("A.8.9", "Configuration management", ControlCategory.CONFIGURATION_MANAGEMENT),
            ("A.8.10", "Information deletion", ControlCategory.DATA_PROTECTION),
            ("A.8.11", "Data masking", ControlCategory.DATA_PROTECTION),
            ("A.8.12", "Data leakage prevention", ControlCategory.DATA_PROTECTION),
            ("A.8.13", "Information backup", ControlCategory.BUSINESS_CONTINUITY),
            ("A.8.14", "Redundancy of information processing facilities", ControlCategory.BUSINESS_CONTINUITY),
            ("A.8.15", "Logging", ControlCategory.AUDIT_LOGGING),
            ("A.8.16", "Monitoring activities", ControlCategory.AUDIT_LOGGING),
            ("A.8.17", "Clock synchronization", ControlCategory.AUDIT_LOGGING),
            ("A.8.18", "Use of privileged utility programs", ControlCategory.ACCESS_CONTROL),
            ("A.8.19", "Installation of software on operational systems", ControlCategory.CONFIGURATION_MANAGEMENT),
            ("A.8.20", "Networks security", ControlCategory.COMMUNICATIONS),
            ("A.8.21", "Security of network services", ControlCategory.COMMUNICATIONS),
            ("A.8.22", "Segregation of networks", ControlCategory.COMMUNICATIONS),
            ("A.8.23", "Web filtering", ControlCategory.COMMUNICATIONS),
            ("A.8.24", "Use of cryptography", ControlCategory.CRYPTOGRAPHY),
            ("A.8.25", "Secure development life cycle", ControlCategory.SYSTEM_SERVICES),
            ("A.8.26", "Application security requirements", ControlCategory.SYSTEM_SERVICES),
            ("A.8.27", "Secure system architecture and engineering principles", ControlCategory.SYSTEM_SERVICES),
            ("A.8.28", "Secure coding", ControlCategory.SYSTEM_SERVICES),
            ("A.8.29", "Security testing in development and acceptance", ControlCategory.SECURITY_ASSESSMENT),
            ("A.8.30", "Outsourced development", ControlCategory.SUPPLY_CHAIN),
            ("A.8.31", "Separation of development, test and production environments", ControlCategory.CONFIGURATION_MANAGEMENT),
            ("A.8.32", "Change management", ControlCategory.CHANGE_MANAGEMENT),
            ("A.8.33", "Test information", ControlCategory.DATA_PROTECTION),
            ("A.8.34", "Protection of information systems during audit testing", ControlCategory.SECURITY_ASSESSMENT),
        ]
    },
    {
        "type": FrameworkType.SOC_2,
        "name": "SOC 2 Type II",
        "version": "2017",
        "description": "Service Organization Control 2 - Trust Services Criteria",
        "publisher": "AICPA",
        "controls": [
            # Security (CC)
            ("CC1.1", "COSO Principle 1: Demonstrates Commitment to Integrity and Ethical Values", ControlCategory.GOVERNANCE),
            ("CC1.2", "COSO Principle 2: Exercises Oversight Responsibility", ControlCategory.GOVERNANCE),
            ("CC1.3", "COSO Principle 3: Establishes Structure, Authority, and Responsibility", ControlCategory.GOVERNANCE),
            ("CC1.4", "COSO Principle 4: Demonstrates Commitment to Competence", ControlCategory.PERSONNEL_SECURITY),
            ("CC1.5", "COSO Principle 5: Enforces Accountability", ControlCategory.GOVERNANCE),
            ("CC2.1", "COSO Principle 13: Obtains or Generates Relevant, Quality Information", ControlCategory.COMMUNICATIONS),
            ("CC2.2", "COSO Principle 14: Internally Communicates Information", ControlCategory.COMMUNICATIONS),
            ("CC2.3", "COSO Principle 15: Communicates Externally", ControlCategory.COMMUNICATIONS),
            ("CC3.1", "COSO Principle 6: Specifies Suitable Objectives", ControlCategory.RISK_ASSESSMENT),
            ("CC3.2", "COSO Principle 7: Identifies and Analyzes Risk", ControlCategory.RISK_ASSESSMENT),
            ("CC3.3", "COSO Principle 8: Assesses Fraud Risk", ControlCategory.RISK_ASSESSMENT),
            ("CC3.4", "COSO Principle 9: Identifies and Analyzes Significant Change", ControlCategory.CHANGE_MANAGEMENT),
            ("CC4.1", "COSO Principle 16: Selects, Develops, and Performs Ongoing Evaluations", ControlCategory.SECURITY_ASSESSMENT),
            ("CC4.2", "COSO Principle 17: Evaluates and Communicates Deficiencies", ControlCategory.SECURITY_ASSESSMENT),
            ("CC5.1", "COSO Principle 10: Selects and Develops Control Activities", ControlCategory.GOVERNANCE),
            ("CC5.2", "COSO Principle 11: Selects and Develops General Controls over Technology", ControlCategory.CONFIGURATION_MANAGEMENT),
            ("CC5.3", "COSO Principle 12: Deploys Through Policies and Procedures", ControlCategory.GOVERNANCE),
            ("CC6.1", "Logical and Physical Access Controls", ControlCategory.ACCESS_CONTROL),
            ("CC6.2", "Prior to Issuing System Credentials", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("CC6.3", "Internal and External System Users", ControlCategory.ACCESS_CONTROL),
            ("CC6.4", "Access to System Components", ControlCategory.ACCESS_CONTROL),
            ("CC6.5", "Access to Information Assets", ControlCategory.ACCESS_CONTROL),
            ("CC6.6", "Restrictions on Access", ControlCategory.ACCESS_CONTROL),
            ("CC6.7", "Transmission of Information", ControlCategory.COMMUNICATIONS),
            ("CC6.8", "Malicious Software Prevention", ControlCategory.SYSTEM_SERVICES),
            ("CC7.1", "Detection and Monitoring", ControlCategory.AUDIT_LOGGING),
            ("CC7.2", "Evaluating Security Events", ControlCategory.INCIDENT_RESPONSE),
            ("CC7.3", "Response to Security Incidents", ControlCategory.INCIDENT_RESPONSE),
            ("CC7.4", "Recovery from Security Incidents", ControlCategory.INCIDENT_RESPONSE),
            ("CC7.5", "Information Recovery", ControlCategory.BUSINESS_CONTINUITY),
            ("CC8.1", "Changes to Infrastructure and Software", ControlCategory.CHANGE_MANAGEMENT),
            ("CC9.1", "Mitigation of Ongoing Risks", ControlCategory.RISK_ASSESSMENT),
            ("CC9.2", "Vendor Risk Management", ControlCategory.SUPPLY_CHAIN),
            # Availability (A)
            ("A1.1", "System Availability Commitments", ControlCategory.BUSINESS_CONTINUITY),
            ("A1.2", "Environmental Protections", ControlCategory.PHYSICAL_SECURITY),
            ("A1.3", "Recovery Operations", ControlCategory.BUSINESS_CONTINUITY),
            # Processing Integrity (PI)
            ("PI1.1", "Processing Integrity Commitments", ControlCategory.DATA_PROTECTION),
            ("PI1.2", "Complete, Accurate, and Timely Processing", ControlCategory.DATA_PROTECTION),
            ("PI1.3", "Inputs and Outputs", ControlCategory.DATA_PROTECTION),
            ("PI1.4", "Processing Errors", ControlCategory.DATA_PROTECTION),
            ("PI1.5", "Outputs Complete and Accurate", ControlCategory.DATA_PROTECTION),
            # Confidentiality (C)
            ("C1.1", "Confidential Information Identification", ControlCategory.DATA_PROTECTION),
            ("C1.2", "Confidential Information Disposal", ControlCategory.DATA_PROTECTION),
            # Privacy (P)
            ("P1.1", "Privacy Notice", ControlCategory.PRIVACY),
            ("P2.1", "Choice and Consent", ControlCategory.PRIVACY),
            ("P3.1", "Personal Information Collection", ControlCategory.PRIVACY),
            ("P3.2", "Collection Limitation", ControlCategory.PRIVACY),
            ("P4.1", "Use, Retention, and Disposal", ControlCategory.PRIVACY),
            ("P4.2", "Use Limitation", ControlCategory.PRIVACY),
            ("P4.3", "Retention", ControlCategory.PRIVACY),
            ("P5.1", "Access Requests", ControlCategory.PRIVACY),
            ("P5.2", "Correction Requests", ControlCategory.PRIVACY),
            ("P6.1", "Disclosure to Third Parties", ControlCategory.PRIVACY),
            ("P6.2", "Authorization for Disclosure", ControlCategory.PRIVACY),
            ("P6.3", "Compliance with Disclosure Requirements", ControlCategory.PRIVACY),
            ("P6.4", "Disclosure of Privacy Practices", ControlCategory.PRIVACY),
            ("P6.5", "Privacy Agreements", ControlCategory.PRIVACY),
            ("P6.6", "Third-Party Obligations", ControlCategory.PRIVACY),
            ("P6.7", "Notice of Changes", ControlCategory.PRIVACY),
            ("P7.1", "Data Quality", ControlCategory.DATA_PROTECTION),
            ("P8.1", "Privacy Complaints", ControlCategory.PRIVACY),
        ]
    },
    {
        "type": FrameworkType.PCI_DSS,
        "name": "PCI DSS v4.0",
        "version": "4.0",
        "description": "Payment Card Industry Data Security Standard",
        "publisher": "PCI Security Standards Council",
        "controls": [
            # Requirement 1: Network Security Controls
            ("1.1.1", "Define and document network security policies", ControlCategory.GOVERNANCE),
            ("1.2.1", "Restrict inbound and outbound traffic", ControlCategory.COMMUNICATIONS),
            ("1.2.5", "Services, protocols, and ports are documented", ControlCategory.COMMUNICATIONS),
            ("1.3.1", "Restrict inbound traffic to CDE", ControlCategory.ACCESS_CONTROL),
            ("1.3.2", "Restrict outbound traffic from CDE", ControlCategory.ACCESS_CONTROL),
            ("1.4.1", "NSCs between wireless and CDE", ControlCategory.COMMUNICATIONS),
            ("1.5.1", "Risk to CDE from computing devices is mitigated", ControlCategory.CONFIGURATION_MANAGEMENT),
            # Requirement 2: Secure Configurations
            ("2.1.1", "Define and document secure configuration standards", ControlCategory.CONFIGURATION_MANAGEMENT),
            ("2.2.1", "Configuration standards developed for all system components", ControlCategory.CONFIGURATION_MANAGEMENT),
            ("2.2.2", "Vendor default accounts are managed", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("2.2.5", "Primary functions require different security levels", ControlCategory.CONFIGURATION_MANAGEMENT),
            ("2.2.7", "Non-console administrative access encrypted", ControlCategory.CRYPTOGRAPHY),
            # Requirement 3: Protect Stored Account Data
            ("3.1.1", "Data retention and disposal policies", ControlCategory.DATA_PROTECTION),
            ("3.2.1", "Account data storage kept minimum", ControlCategory.DATA_PROTECTION),
            ("3.3.1", "SAD not stored after authorization", ControlCategory.DATA_PROTECTION),
            ("3.4.1", "PAN is masked when displayed", ControlCategory.DATA_PROTECTION),
            ("3.5.1", "PAN rendered unreadable", ControlCategory.CRYPTOGRAPHY),
            ("3.6.1", "Cryptographic key lifecycle management", ControlCategory.CRYPTOGRAPHY),
            ("3.7.1", "Key management procedures documented", ControlCategory.CRYPTOGRAPHY),
            # Requirement 4: Protect Cardholder Data in Transit
            ("4.1.1", "Strong cryptography for transmission", ControlCategory.CRYPTOGRAPHY),
            ("4.2.1", "PAN protected when sent via messaging", ControlCategory.DATA_PROTECTION),
            # Requirement 5: Protect from Malicious Software
            ("5.1.1", "Anti-malware solution deployed", ControlCategory.SYSTEM_SERVICES),
            ("5.2.1", "Periodic scans and active monitoring", ControlCategory.VULNERABILITY_MANAGEMENT),
            ("5.3.1", "Anti-malware mechanisms are active", ControlCategory.SYSTEM_SERVICES),
            ("5.4.1", "Anti-phishing mechanisms protect users", ControlCategory.AWARENESS_TRAINING),
            # Requirement 6: Develop Secure Systems
            ("6.1.1", "Security vulnerabilities identified and ranked", ControlCategory.VULNERABILITY_MANAGEMENT),
            ("6.2.1", "Bespoke and custom software developed securely", ControlCategory.SYSTEM_SERVICES),
            ("6.3.1", "Security vulnerabilities addressed", ControlCategory.VULNERABILITY_MANAGEMENT),
            ("6.4.1", "Public-facing web apps protected", ControlCategory.SYSTEM_SERVICES),
            ("6.5.1", "Changes to production managed", ControlCategory.CHANGE_MANAGEMENT),
            # Requirement 7: Restrict Access
            ("7.1.1", "Access control policy defined", ControlCategory.ACCESS_CONTROL),
            ("7.2.1", "Access control model established", ControlCategory.ACCESS_CONTROL),
            ("7.2.4", "Access reviews performed", ControlCategory.ACCESS_CONTROL),
            ("7.3.1", "Access control system in place", ControlCategory.ACCESS_CONTROL),
            # Requirement 8: Identify Users and Authenticate
            ("8.1.1", "User identification policy defined", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("8.2.1", "User accounts properly managed", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("8.3.1", "Strong authentication for users", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("8.3.6", "Password/passphrase requirements", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("8.4.1", "MFA for non-console access to CDE", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("8.5.1", "MFA systems properly configured", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("8.6.1", "Interactive login accounts managed", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            # Requirement 9: Restrict Physical Access
            ("9.1.1", "Physical access policy defined", ControlCategory.PHYSICAL_SECURITY),
            ("9.2.1", "Physical access controls in place", ControlCategory.PHYSICAL_SECURITY),
            ("9.3.1", "Physical access for personnel controlled", ControlCategory.PHYSICAL_SECURITY),
            ("9.4.1", "Media physically secured", ControlCategory.MEDIA_PROTECTION),
            ("9.5.1", "POI devices protected from tampering", ControlCategory.PHYSICAL_SECURITY),
            # Requirement 10: Log and Monitor
            ("10.1.1", "Logging and monitoring policy defined", ControlCategory.AUDIT_LOGGING),
            ("10.2.1", "Audit logs enabled and active", ControlCategory.AUDIT_LOGGING),
            ("10.3.1", "Audit logs protected from modification", ControlCategory.AUDIT_LOGGING),
            ("10.4.1", "Audit logs reviewed daily", ControlCategory.AUDIT_LOGGING),
            ("10.5.1", "Audit log history retained", ControlCategory.AUDIT_LOGGING),
            ("10.6.1", "Time synchronization mechanisms", ControlCategory.AUDIT_LOGGING),
            ("10.7.1", "Failures of critical security systems detected", ControlCategory.AUDIT_LOGGING),
            # Requirement 11: Test Security Regularly
            ("11.1.1", "Security testing policy defined", ControlCategory.SECURITY_ASSESSMENT),
            ("11.2.1", "Wireless access points identified", ControlCategory.SECURITY_ASSESSMENT),
            ("11.3.1", "Vulnerabilities addressed in internal scans", ControlCategory.VULNERABILITY_MANAGEMENT),
            ("11.3.2", "External vulnerability scans performed", ControlCategory.VULNERABILITY_MANAGEMENT),
            ("11.4.1", "Penetration testing performed", ControlCategory.SECURITY_ASSESSMENT),
            ("11.5.1", "Intrusion detection/prevention in place", ControlCategory.SYSTEM_SERVICES),
            ("11.6.1", "Change detection mechanisms deployed", ControlCategory.CHANGE_MANAGEMENT),
            # Requirement 12: Support Information Security
            ("12.1.1", "Information security policy established", ControlCategory.GOVERNANCE),
            ("12.2.1", "Acceptable use policies defined", ControlCategory.GOVERNANCE),
            ("12.3.1", "Risks to CDE formally identified", ControlCategory.RISK_ASSESSMENT),
            ("12.4.1", "PCI DSS compliance managed", ControlCategory.COMPLIANCE),
            ("12.5.1", "PCI DSS scope documented", ControlCategory.COMPLIANCE),
            ("12.6.1", "Security awareness program implemented", ControlCategory.AWARENESS_TRAINING),
            ("12.7.1", "Personnel screened before hire", ControlCategory.PERSONNEL_SECURITY),
            ("12.8.1", "Service providers managed", ControlCategory.SUPPLY_CHAIN),
            ("12.9.1", "Service provider compliance confirmed", ControlCategory.SUPPLY_CHAIN),
            ("12.10.1", "Incident response plan implemented", ControlCategory.INCIDENT_RESPONSE),
        ]
    },
    {
        "type": FrameworkType.GDPR,
        "name": "GDPR",
        "version": "2018",
        "description": "General Data Protection Regulation",
        "publisher": "European Union",
        "controls": [
            ("Art.5", "Principles of data processing", ControlCategory.PRIVACY),
            ("Art.6", "Lawfulness of processing", ControlCategory.PRIVACY),
            ("Art.7", "Conditions for consent", ControlCategory.PRIVACY),
            ("Art.8", "Child's consent for information society services", ControlCategory.PRIVACY),
            ("Art.9", "Processing of special categories of data", ControlCategory.PRIVACY),
            ("Art.10", "Processing of criminal conviction data", ControlCategory.PRIVACY),
            ("Art.12", "Transparent information and communication", ControlCategory.PRIVACY),
            ("Art.13", "Information when data collected from subject", ControlCategory.PRIVACY),
            ("Art.14", "Information when data not obtained from subject", ControlCategory.PRIVACY),
            ("Art.15", "Right of access by data subject", ControlCategory.PRIVACY),
            ("Art.16", "Right to rectification", ControlCategory.PRIVACY),
            ("Art.17", "Right to erasure (right to be forgotten)", ControlCategory.PRIVACY),
            ("Art.18", "Right to restriction of processing", ControlCategory.PRIVACY),
            ("Art.19", "Notification obligation", ControlCategory.PRIVACY),
            ("Art.20", "Right to data portability", ControlCategory.PRIVACY),
            ("Art.21", "Right to object", ControlCategory.PRIVACY),
            ("Art.22", "Automated individual decision-making", ControlCategory.PRIVACY),
            ("Art.24", "Responsibility of the controller", ControlCategory.GOVERNANCE),
            ("Art.25", "Data protection by design and by default", ControlCategory.PRIVACY),
            ("Art.26", "Joint controllers", ControlCategory.GOVERNANCE),
            ("Art.27", "Representatives of controllers not in Union", ControlCategory.GOVERNANCE),
            ("Art.28", "Processor requirements", ControlCategory.SUPPLY_CHAIN),
            ("Art.29", "Processing under controller/processor authority", ControlCategory.GOVERNANCE),
            ("Art.30", "Records of processing activities", ControlCategory.AUDIT_LOGGING),
            ("Art.32", "Security of processing", ControlCategory.DATA_PROTECTION),
            ("Art.33", "Notification of breach to supervisory authority", ControlCategory.INCIDENT_RESPONSE),
            ("Art.34", "Communication of breach to data subject", ControlCategory.INCIDENT_RESPONSE),
            ("Art.35", "Data protection impact assessment", ControlCategory.RISK_ASSESSMENT),
            ("Art.36", "Prior consultation", ControlCategory.RISK_ASSESSMENT),
            ("Art.37", "Designation of DPO", ControlCategory.GOVERNANCE),
            ("Art.38", "Position of DPO", ControlCategory.GOVERNANCE),
            ("Art.39", "Tasks of DPO", ControlCategory.GOVERNANCE),
            ("Art.40", "Codes of conduct", ControlCategory.COMPLIANCE),
            ("Art.42", "Certification", ControlCategory.COMPLIANCE),
            ("Art.44", "General transfer principles", ControlCategory.DATA_PROTECTION),
            ("Art.45", "Transfers on adequacy decision", ControlCategory.DATA_PROTECTION),
            ("Art.46", "Transfers with appropriate safeguards", ControlCategory.DATA_PROTECTION),
            ("Art.47", "Binding corporate rules", ControlCategory.GOVERNANCE),
            ("Art.49", "Derogations for specific situations", ControlCategory.DATA_PROTECTION),
        ]
    },
    {
        "type": FrameworkType.HIPAA,
        "name": "HIPAA Security Rule",
        "version": "2013",
        "description": "Health Insurance Portability and Accountability Act",
        "publisher": "U.S. Department of Health and Human Services",
        "controls": [
            # Administrative Safeguards
            ("164.308(a)(1)", "Security Management Process", ControlCategory.GOVERNANCE),
            ("164.308(a)(2)", "Assigned Security Responsibility", ControlCategory.GOVERNANCE),
            ("164.308(a)(3)", "Workforce Security", ControlCategory.PERSONNEL_SECURITY),
            ("164.308(a)(4)", "Information Access Management", ControlCategory.ACCESS_CONTROL),
            ("164.308(a)(5)", "Security Awareness and Training", ControlCategory.AWARENESS_TRAINING),
            ("164.308(a)(6)", "Security Incident Procedures", ControlCategory.INCIDENT_RESPONSE),
            ("164.308(a)(7)", "Contingency Plan", ControlCategory.BUSINESS_CONTINUITY),
            ("164.308(a)(8)", "Evaluation", ControlCategory.SECURITY_ASSESSMENT),
            ("164.308(b)(1)", "Business Associate Contracts", ControlCategory.SUPPLY_CHAIN),
            # Physical Safeguards
            ("164.310(a)(1)", "Facility Access Controls", ControlCategory.PHYSICAL_SECURITY),
            ("164.310(b)", "Workstation Use", ControlCategory.PHYSICAL_SECURITY),
            ("164.310(c)", "Workstation Security", ControlCategory.PHYSICAL_SECURITY),
            ("164.310(d)(1)", "Device and Media Controls", ControlCategory.MEDIA_PROTECTION),
            # Technical Safeguards
            ("164.312(a)(1)", "Access Control", ControlCategory.ACCESS_CONTROL),
            ("164.312(b)", "Audit Controls", ControlCategory.AUDIT_LOGGING),
            ("164.312(c)(1)", "Integrity", ControlCategory.DATA_PROTECTION),
            ("164.312(d)", "Person or Entity Authentication", ControlCategory.IDENTIFICATION_AUTHENTICATION),
            ("164.312(e)(1)", "Transmission Security", ControlCategory.CRYPTOGRAPHY),
            # Organizational Requirements
            ("164.314(a)(1)", "Business Associate Contracts", ControlCategory.SUPPLY_CHAIN),
            ("164.314(b)(1)", "Requirements for Group Health Plans", ControlCategory.COMPLIANCE),
            # Policies and Documentation
            ("164.316(a)", "Policies and Procedures", ControlCategory.GOVERNANCE),
            ("164.316(b)(1)", "Documentation", ControlCategory.GOVERNANCE),
        ]
    },
    {
        "type": FrameworkType.CIS_CONTROLS,
        "name": "CIS Controls v8",
        "version": "8.0",
        "description": "Center for Internet Security Critical Security Controls",
        "publisher": "Center for Internet Security",
        "controls": [
            ("CIS.1", "Inventory and Control of Enterprise Assets", ControlCategory.ASSET_MANAGEMENT),
            ("CIS.2", "Inventory and Control of Software Assets", ControlCategory.ASSET_MANAGEMENT),
            ("CIS.3", "Data Protection", ControlCategory.DATA_PROTECTION),
            ("CIS.4", "Secure Configuration of Enterprise Assets and Software", ControlCategory.CONFIGURATION_MANAGEMENT),
            ("CIS.5", "Account Management", ControlCategory.ACCESS_CONTROL),
            ("CIS.6", "Access Control Management", ControlCategory.ACCESS_CONTROL),
            ("CIS.7", "Continuous Vulnerability Management", ControlCategory.VULNERABILITY_MANAGEMENT),
            ("CIS.8", "Audit Log Management", ControlCategory.AUDIT_LOGGING),
            ("CIS.9", "Email and Web Browser Protections", ControlCategory.SYSTEM_SERVICES),
            ("CIS.10", "Malware Defenses", ControlCategory.SYSTEM_SERVICES),
            ("CIS.11", "Data Recovery", ControlCategory.BUSINESS_CONTINUITY),
            ("CIS.12", "Network Infrastructure Management", ControlCategory.COMMUNICATIONS),
            ("CIS.13", "Network Monitoring and Defense", ControlCategory.AUDIT_LOGGING),
            ("CIS.14", "Security Awareness and Skills Training", ControlCategory.AWARENESS_TRAINING),
            ("CIS.15", "Service Provider Management", ControlCategory.SUPPLY_CHAIN),
            ("CIS.16", "Application Software Security", ControlCategory.SYSTEM_SERVICES),
            ("CIS.17", "Incident Response Management", ControlCategory.INCIDENT_RESPONSE),
            ("CIS.18", "Penetration Testing", ControlCategory.SECURITY_ASSESSMENT),
        ]
    },
]


# ============================================================
# SAMPLE CUSTOMERS/ENTITIES
# ============================================================

SAMPLE_CUSTOMERS = [
    {"legal_name": "Acme Corporation", "type": CustomerType.CORPORATION, "industry": "Technology", "country": "US", "risk": CustomerRiskRating.LOW},
    {"legal_name": "Global Finance Ltd", "type": CustomerType.FINANCIAL_INSTITUTION, "industry": "Banking", "country": "GB", "risk": CustomerRiskRating.MEDIUM},
    {"legal_name": "Pacific Trading Co", "type": CustomerType.CORPORATION, "industry": "Import/Export", "country": "SG", "risk": CustomerRiskRating.HIGH},
    {"first_name": "John", "last_name": "Smith", "type": CustomerType.INDIVIDUAL, "industry": None, "country": "US", "risk": CustomerRiskRating.LOW},
    {"legal_name": "Healthcare Partners Inc", "type": CustomerType.CORPORATION, "industry": "Healthcare", "country": "US", "risk": CustomerRiskRating.MEDIUM},
    {"legal_name": "EuroBank AG", "type": CustomerType.FINANCIAL_INSTITUTION, "industry": "Banking", "country": "DE", "risk": CustomerRiskRating.MEDIUM},
    {"legal_name": "Tech Innovations LLC", "type": CustomerType.LLC, "industry": "Technology", "country": "US", "risk": CustomerRiskRating.LOW},
    {"first_name": "Maria", "last_name": "Garcia", "type": CustomerType.INDIVIDUAL, "industry": None, "country": "ES", "risk": CustomerRiskRating.LOW},
    {"legal_name": "Asian Imports Ltd", "type": CustomerType.CORPORATION, "industry": "Retail", "country": "HK", "risk": CustomerRiskRating.HIGH},
    {"legal_name": "Nordic Energy AS", "type": CustomerType.CORPORATION, "industry": "Energy", "country": "NO", "risk": CustomerRiskRating.LOW},
    {"legal_name": "Middle East Holdings", "type": CustomerType.CORPORATION, "industry": "Investment", "country": "AE", "risk": CustomerRiskRating.HIGH},
    {"legal_name": "Canadian Resources Corp", "type": CustomerType.CORPORATION, "industry": "Mining", "country": "CA", "risk": CustomerRiskRating.MEDIUM},
    {"legal_name": "Latin America Trading", "type": CustomerType.CORPORATION, "industry": "Import/Export", "country": "BR", "risk": CustomerRiskRating.MEDIUM},
    {"legal_name": "Swiss Private Bank", "type": CustomerType.FINANCIAL_INSTITUTION, "industry": "Private Banking", "country": "CH", "risk": CustomerRiskRating.MEDIUM},
    {"legal_name": "Tokyo Electronics", "type": CustomerType.CORPORATION, "industry": "Electronics", "country": "JP", "risk": CustomerRiskRating.LOW},
    {"first_name": "Ahmed", "last_name": "Al-Hassan", "type": CustomerType.INDIVIDUAL, "industry": None, "country": "SA", "risk": CustomerRiskRating.MEDIUM},
    {"legal_name": "Australian Mining Corp", "type": CustomerType.CORPORATION, "industry": "Mining", "country": "AU", "risk": CustomerRiskRating.LOW},
    {"legal_name": "French Luxury Group", "type": CustomerType.CORPORATION, "industry": "Retail", "country": "FR", "risk": CustomerRiskRating.LOW},
    {"legal_name": "Indian Tech Services", "type": CustomerType.CORPORATION, "industry": "Technology", "country": "IN", "risk": CustomerRiskRating.MEDIUM},
    {"legal_name": "Shell Company XYZ", "type": CustomerType.CORPORATION, "industry": "Consulting", "country": "VG", "risk": CustomerRiskRating.HIGH},
]


# ============================================================
# SAMPLE TRAINING COURSES
# ============================================================

TRAINING_COURSES = [
    {"code": "SEC-101", "title": "Security Awareness Fundamentals", "type": CourseType.SECURITY_AWARENESS, "duration": 45, "required": True},
    {"code": "AML-201", "title": "Anti-Money Laundering Essentials", "type": CourseType.AML_COMPLIANCE, "duration": 60, "required": True},
    {"code": "SANC-301", "title": "Sanctions Compliance Training", "type": CourseType.SANCTIONS_COMPLIANCE, "duration": 90, "required": True},
    {"code": "GDPR-101", "title": "GDPR Data Privacy Fundamentals", "type": CourseType.GDPR, "duration": 60, "required": True},
    {"code": "PHISH-101", "title": "Phishing Awareness", "type": CourseType.PHISHING_AWARENESS, "duration": 30, "required": True},
    {"code": "COC-101", "title": "Code of Conduct", "type": CourseType.CODE_OF_CONDUCT, "duration": 45, "required": True},
    {"code": "HIPAA-201", "title": "HIPAA Privacy and Security", "type": CourseType.HIPAA, "duration": 60, "required": False},
    {"code": "PCI-201", "title": "PCI DSS Awareness", "type": CourseType.PCI_DSS, "duration": 45, "required": False},
    {"code": "ACORR-301", "title": "Anti-Corruption and Bribery", "type": CourseType.ANTI_CORRUPTION, "duration": 45, "required": True},
    {"code": "INSID-301", "title": "Insider Trading Prevention", "type": CourseType.INSIDER_TRADING, "duration": 30, "required": False},
    {"code": "IR-401", "title": "Incident Response Procedures", "type": CourseType.INCIDENT_RESPONSE, "duration": 60, "required": False},
    {"code": "ONB-001", "title": "New Hire Security Onboarding", "type": CourseType.ONBOARDING, "duration": 30, "required": True},
]


# ============================================================
# MONITORING RULES
# ============================================================

MONITORING_RULES = [
    {"code": "AML-001", "name": "Large Cash Transaction", "type": RuleType.THRESHOLD, "category": "AML", "threshold": 10000, "severity": AlertSeverity.HIGH},
    {"code": "AML-002", "name": "Structured Deposits", "type": RuleType.PATTERN, "category": "AML", "threshold": 9500, "severity": AlertSeverity.CRITICAL},
    {"code": "AML-003", "name": "High-Risk Country Transfer", "type": RuleType.GEOGRAPHIC, "category": "AML", "threshold": 5000, "severity": AlertSeverity.HIGH},
    {"code": "AML-004", "name": "Rapid Movement of Funds", "type": RuleType.VELOCITY, "category": "AML", "threshold": 50000, "severity": AlertSeverity.MEDIUM},
    {"code": "AML-005", "name": "Round Dollar Amounts", "type": RuleType.PATTERN, "category": "AML", "threshold": 10000, "severity": AlertSeverity.LOW},
    {"code": "FRAUD-001", "name": "Unusual Transaction Time", "type": RuleType.BEHAVIORAL, "category": "FRAUD", "threshold": 0, "severity": AlertSeverity.LOW},
    {"code": "FRAUD-002", "name": "Shell Company Transaction", "type": RuleType.NETWORK, "category": "FRAUD", "threshold": 1000, "severity": AlertSeverity.HIGH},
    {"code": "SANC-001", "name": "PEP Related Transaction", "type": RuleType.CUSTOM, "category": "SANCTIONS", "threshold": 5000, "severity": AlertSeverity.HIGH},
    {"code": "SANC-002", "name": "Sanctions List Match", "type": RuleType.CUSTOM, "category": "SANCTIONS", "threshold": 0, "severity": AlertSeverity.CRITICAL},
    {"code": "CRYPTO-001", "name": "Crypto Conversion", "type": RuleType.BEHAVIORAL, "category": "AML", "threshold": 1000, "severity": AlertSeverity.MEDIUM},
]


async def seed_full_platform():
    """Seed the entire platform with comprehensive data."""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("CORTEX COMPLIANCE PLATFORM - FULL DATA SEED")
        print("=" * 60)

        # Get or create tenant
        result = await db.execute(select(Tenant).where(Tenant.slug == "default"))
        tenant = result.scalar_one_or_none()

        if not tenant:
            tenant = Tenant(
                id=uuid4(),
                name="Demo Organization",
                slug="default",
                is_active=True,
                settings={
                    "features": ["compliance", "sanctions", "aml", "kyc", "training"],
                    "modules": ["frameworks", "customers", "transactions", "cases", "training"]
                },
            )
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)
            print(f"[+] Created tenant: {tenant.name}")

        tenant_id = tenant.id

        # Get or create demo users
        result = await db.execute(select(User).where(User.email == "demo@cortex.ai"))
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            admin_user = User(
                id=uuid4(),
                tenant_id=tenant_id,
                email="demo@cortex.ai",
                hashed_password=hash_password("demo1234"),
                full_name="Demo Admin",
                role="ADMIN",
                is_active=True,
                is_verified=True,
                created_at=datetime.now(timezone.utc),
            )
            db.add(admin_user)
            await db.commit()
            print(f"[+] Created admin user: {admin_user.email}")

        # Create additional users
        users = [admin_user]
        for i, (name, role) in enumerate([
            ("Alice Johnson", "ANALYST"),
            ("Bob Williams", "ANALYST"),
            ("Carol Davis", "APPROVER"),
            ("David Chen", "VIEWER"),
        ]):
            email = f"{name.lower().replace(' ', '.')}@cortex.ai"
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    email=email,
                    hashed_password=hash_password("password123"),
                    full_name=name,
                    role=role,
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 365)),
                )
                db.add(user)
                users.append(user)
        await db.commit()
        print(f"[+] Created {len(users)} users")

        # ============================================================
        # SEED COMPLIANCE FRAMEWORKS
        # ============================================================
        print("\n[Frameworks] Importing compliance frameworks...")
        framework_count = 0
        control_count = 0

        for fw_data in FRAMEWORKS:
            # Check if framework exists
            result = await db.execute(
                select(Framework).where(
                    Framework.tenant_id == tenant_id,
                    Framework.type == fw_data["type"]
                )
            )
            framework = result.scalar_one_or_none()

            if not framework:
                framework = Framework(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    type=fw_data["type"],
                    name=fw_data["name"],
                    version=fw_data["version"],
                    description=fw_data["description"],
                    publisher=fw_data["publisher"],
                    total_controls=len(fw_data["controls"]),
                    categories=list(set(c[2].value for c in fw_data["controls"])),
                    is_active=True,
                )
                db.add(framework)
                await db.flush()
                framework_count += 1

                # Add controls
                for ctrl_id, title, category in fw_data["controls"]:
                    # Randomly assign implementation status
                    status = random.choices(
                        [AssessmentResult.FULLY_IMPLEMENTED, AssessmentResult.PARTIALLY_IMPLEMENTED,
                         AssessmentResult.NOT_IMPLEMENTED, AssessmentResult.NOT_ASSESSED],
                        weights=[40, 30, 15, 15]
                    )[0]

                    control = Control(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        framework_id=framework.id,
                        control_id=ctrl_id,
                        title=title,
                        description=f"{title} - Implementation and verification of this control.",
                        category=category,
                        implementation_status=status,
                        priority=random.randint(1, 3),
                    )
                    db.add(control)
                    control_count += 1

        await db.commit()
        print(f"    Created {framework_count} frameworks with {control_count} controls")

        # ============================================================
        # SEED CUSTOMERS
        # ============================================================
        print("\n[Customers] Creating sample customers...")
        customer_ids = []

        for cust_data in SAMPLE_CUSTOMERS:
            # Build query based on customer type
            if cust_data["type"] == CustomerType.INDIVIDUAL:
                result = await db.execute(
                    select(Customer).where(
                        Customer.tenant_id == tenant_id,
                        Customer.first_name == cust_data.get("first_name"),
                        Customer.last_name == cust_data.get("last_name")
                    )
                )
            else:
                result = await db.execute(
                    select(Customer).where(
                        Customer.tenant_id == tenant_id,
                        Customer.legal_name == cust_data.get("legal_name")
                    )
                )
            customer = result.scalar_one_or_none()

            if not customer:
                customer = Customer(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    external_id=f"CUST-{random.randint(10000, 99999)}",
                    customer_type=cust_data["type"],
                    status=CustomerStatus.ACTIVE,
                    risk_rating=cust_data["risk"],
                    risk_score=random.uniform(20, 90),
                    # Individual fields
                    first_name=cust_data.get("first_name"),
                    last_name=cust_data.get("last_name"),
                    country_of_residence=cust_data["country"] if cust_data["type"] == CustomerType.INDIVIDUAL else None,
                    # Organization fields
                    legal_name=cust_data.get("legal_name"),
                    incorporation_country=cust_data["country"] if cust_data["type"] != CustomerType.INDIVIDUAL else None,
                    industry_description=cust_data["industry"],
                    # Review dates
                    last_review_date=date.today() - timedelta(days=random.randint(1, 180)),
                    next_review_date=date.today() + timedelta(days=random.randint(30, 365)),
                    onboarded_at=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 730)),
                    # Risk factors
                    is_pep=random.random() < 0.1,
                    is_sanctioned=False,
                    high_risk_country=cust_data["country"] in ["VG", "AE", "HK"],
                    high_risk_industry=cust_data["industry"] in ["Investment", "Consulting"] if cust_data["industry"] else False,
                )
                db.add(customer)
                customer_ids.append(customer.id)

        await db.commit()
        print(f"    Created {len(SAMPLE_CUSTOMERS)} customers")

        # Get all customer IDs for transactions
        result = await db.execute(select(Customer.id).where(Customer.tenant_id == tenant_id))
        customer_ids = [row[0] for row in result.fetchall()]

        # ============================================================
        # SEED TRANSACTIONS
        # ============================================================
        print("\n[Transactions] Generating sample transactions...")
        transaction_count = 0

        transaction_types = [TransactionType.WIRE_TRANSFER, TransactionType.ACH, TransactionType.CHECK,
                           TransactionType.CASH_DEPOSIT, TransactionType.CARD_PAYMENT, TransactionType.CRYPTO_TRANSFER]
        currencies = ["USD", "EUR", "GBP", "CHF", "JPY", "CAD", "AUD", "SGD"]
        countries = ["US", "GB", "DE", "FR", "SG", "HK", "AE", "CH", "JP", "AU"]
        banks = ["Chase Bank", "HSBC", "Deutsche Bank", "UBS", "Barclays", "Standard Chartered", "Citibank", "BNP Paribas"]

        for i in range(500):  # Create 500 transactions
            tx_date = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 90))
            amount = Decimal(str(round(random.uniform(100, 500000), 2)))

            # Determine if this should be flagged
            is_suspicious = random.random() < 0.1
            status = TransactionStatus.HELD if is_suspicious else random.choice([
                TransactionStatus.COMPLETED, TransactionStatus.COMPLETED,
                TransactionStatus.PENDING, TransactionStatus.PROCESSING
            ])

            direction = "OUTBOUND" if random.random() < 0.5 else "INBOUND"

            transaction = Transaction(
                id=uuid4(),
                tenant_id=tenant_id,
                transaction_ref=f"TXN-{datetime.now().strftime('%Y%m%d')}-{random.randint(100000, 999999)}-{i}",
                customer_id=random.choice(customer_ids),
                transaction_type=random.choice(transaction_types),
                direction=direction,
                amount=amount,
                currency=random.choice(currencies),
                status=status,
                initiated_at=tx_date,
                completed_at=tx_date + timedelta(hours=random.randint(1, 48)) if status == TransactionStatus.COMPLETED else None,
                value_date=tx_date + timedelta(days=random.randint(0, 3)),
                originator_name=f"Originator Corp {random.randint(1, 50)}" if direction == "INBOUND" else None,
                originator_bank=random.choice(banks) if direction == "INBOUND" else None,
                originator_bank_country=random.choice(countries) if direction == "INBOUND" else None,
                beneficiary_name=f"Beneficiary Ltd {random.randint(1, 50)}" if direction == "OUTBOUND" else None,
                beneficiary_bank=random.choice(banks) if direction == "OUTBOUND" else None,
                beneficiary_bank_country=random.choice(countries) if direction == "OUTBOUND" else None,
                purpose=random.choice(["Trade Payment", "Service Fee", "Investment", "Loan Repayment", "Dividend", "Salary"]),
                risk_score=random.uniform(0.5, 0.95) if is_suspicious else random.uniform(0.0, 0.4),
                has_alert=is_suspicious,
            )
            db.add(transaction)
            transaction_count += 1

        await db.commit()
        print(f"    Created {transaction_count} transactions")

        # ============================================================
        # SEED CASES
        # ============================================================
        print("\n[Cases] Creating sample cases...")
        case_count = 0

        case_titles = [
            "Suspicious Wire Transfer Activity",
            "KYC Documentation Review",
            "PEP Relationship Investigation",
            "Unusual Transaction Pattern",
            "Sanctions Hit Review",
            "Customer Due Diligence Refresh",
            "High-Risk Customer Onboarding",
            "Transaction Monitoring Alert",
            "Adverse Media Finding",
            "Regulatory Inquiry Response",
            "AML Program Assessment",
            "Third-Party Risk Review",
            "Data Breach Investigation",
            "Policy Violation Review",
            "Compliance Audit Finding",
        ]

        for i in range(50):  # Create 50 cases
            case_date = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 180))
            status = random.choice([CaseStatus.NEW, CaseStatus.NEW, CaseStatus.IN_PROGRESS,
                                   CaseStatus.IN_PROGRESS, CaseStatus.CLOSED_RESOLVED, CaseStatus.CLOSED_NO_ACTION])

            case = Case(
                id=uuid4(),
                tenant_id=tenant_id,
                case_ref=f"CASE-{datetime.now().strftime('%Y')}-{str(i+1).zfill(5)}",
                title=random.choice(case_titles),
                description=f"Investigation case opened for compliance review. Case involves multiple entities and requires thorough documentation.",
                case_type=random.choice([CaseType.AML_INVESTIGATION, CaseType.UNUSUAL_ACTIVITY, CaseType.SANCTIONS_MATCH, CaseType.FRAUD_INVESTIGATION, CaseType.REGULATORY_INQUIRY, CaseType.PEP_REVIEW]),
                status=status,
                priority=random.choice([CasePriority.LOW, CasePriority.MEDIUM, CasePriority.HIGH, CasePriority.CRITICAL]),
                source_type=random.choice(["ALERT", "SCREENING", "MANUAL"]),
                customer_id=random.choice(customer_ids),
                assigned_to=random.choice(users).id,
                opened_by=admin_user.id,
                opened_at=case_date,
                due_date=case_date.date() + timedelta(days=random.randint(7, 60)),
                sar_required=status == CaseStatus.CLOSED_SAR_FILED,
            )
            db.add(case)
            case_count += 1

        await db.commit()
        print(f"    Created {case_count} cases")

        # ============================================================
        # SEED TRAINING COURSES
        # ============================================================
        print("\n[Training] Creating training courses...")
        course_count = 0

        for course_data in TRAINING_COURSES:
            result = await db.execute(
                select(Course).where(
                    Course.tenant_id == tenant_id,
                    Course.course_code == course_data["code"]
                )
            )
            course = result.scalar_one_or_none()

            if not course:
                course = Course(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    course_code=course_data["code"],
                    title=course_data["title"],
                    description=f"Comprehensive training on {course_data['title'].lower()}. This course covers essential concepts and practical applications.",
                    course_type=course_data["type"],
                    status=CourseStatus.PUBLISHED,
                    duration_minutes=course_data["duration"],
                    required_for_all=course_data["required"],
                    has_quiz=True,
                    passing_score=80,
                    owner_id=admin_user.id,
                    average_score=random.uniform(75, 95),
                    completion_rate=random.uniform(0.6, 0.95),
                    total_completions=random.randint(50, 500),
                )
                db.add(course)
                course_count += 1

        await db.commit()
        print(f"    Created {course_count} training courses")

        # Create training assignments for users
        result = await db.execute(select(Course).where(Course.tenant_id == tenant_id))
        courses = result.scalars().all()

        assignment_count = 0
        for user in users:
            for course in random.sample(courses, min(5, len(courses))):
                status = random.choice([
                    AssignmentStatus.COMPLETED, AssignmentStatus.COMPLETED,
                    AssignmentStatus.IN_PROGRESS, AssignmentStatus.ASSIGNED
                ])

                assigned_date = datetime.now(timezone.utc) - timedelta(days=random.randint(30, 180))

                assignment = TrainingAssignment(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    course_id=course.id,
                    user_id=user.id,
                    status=status,
                    assigned_at=assigned_date,
                    due_date=(assigned_date + timedelta(days=30)).date(),
                    progress_percentage=100 if status == AssignmentStatus.COMPLETED else random.randint(0, 80),
                    completed_at=assigned_date + timedelta(days=random.randint(1, 25)) if status == AssignmentStatus.COMPLETED else None,
                    passed=status == AssignmentStatus.COMPLETED,
                    best_score=random.randint(75, 100) if status == AssignmentStatus.COMPLETED else None,
                )
                db.add(assignment)
                assignment_count += 1

        await db.commit()
        print(f"    Created {assignment_count} training assignments")

        # ============================================================
        # SEED MONITORING RULES
        # ============================================================
        print("\n[Monitoring] Creating monitoring rules...")
        rule_count = 0

        for rule_data in MONITORING_RULES:
            result = await db.execute(
                select(MonitoringRule).where(
                    MonitoringRule.tenant_id == tenant_id,
                    MonitoringRule.name == rule_data["name"]
                )
            )
            rule = result.scalar_one_or_none()

            if not rule:
                rule = MonitoringRule(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    rule_code=rule_data["code"],
                    name=rule_data["name"],
                    description=f"Automated monitoring rule for {rule_data['name'].lower()}",
                    rule_type=rule_data["type"],
                    category=rule_data["category"],
                    default_severity=rule_data["severity"],
                    is_active=True,
                    is_production=True,
                    threshold_value=float(rule_data["threshold"]) if rule_data["threshold"] > 0 else None,
                    threshold_currency="USD",
                    conditions={"type": rule_data["type"].value, "threshold": rule_data["threshold"]},
                )
                db.add(rule)
                rule_count += 1

        await db.commit()
        print(f"    Created {rule_count} monitoring rules")

        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 60)
        print("SEEDING COMPLETE!")
        print("=" * 60)
        print(f"""
Platform Data Summary:
- Frameworks: {len(FRAMEWORKS)} (with {control_count}+ controls)
- Customers: {len(SAMPLE_CUSTOMERS)}
- Transactions: 500
- Cases: 50
- Training Courses: {len(TRAINING_COURSES)}
- Monitoring Rules: {len(MONITORING_RULES)}
- Users: {len(users)}

Login Credentials:
- Email: demo@cortex.ai
- Password: demo1234

Additional test users (password: password123):
- alice.johnson@cortex.ai (Analyst)
- bob.williams@cortex.ai (Analyst)
- carol.davis@cortex.ai (Approver)
- david.chen@cortex.ai (Viewer)
""")


if __name__ == "__main__":
    asyncio.run(seed_full_platform())
