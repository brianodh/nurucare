\# NuruCare - Ethics \& Privacy Statement



\## Document Information



| Property | Value |

|----------|-------|

| \*\*Document Version\*\* | 1.0 |

| \*\*Effective Date\*\* | May 27, 2026 |

| \*\*Last Reviewed\*\* | May 27, 2026 |

| \*\*Prepared By\*\* | Moffat Mose (Health Expert + QA) |

| \*\*Approved By\*\* | NuruCare Team |

| \*\*Project\*\* | AI for Reproductive Health in Africa Hackathon |

| \*\*Hackathon\*\* | Data Science Africa 2026 |



\---



\## Executive Summary



NuruCare is an AI-powered contraceptive decision-support platform designed for Sub-Saharan Africa. This ethics statement outlines our commitments to:



1\. \*\*Privacy First\*\* - No unnecessary data collection, cryptographic protections

2\. \*\*Informed Consent\*\* - Clear, plain-language consent before data collection

3\. \*\*Data Minimization\*\* - Only collect what's clinically necessary

4\. \*\*Limited Retention\*\* - Health data deleted after 30 days

5\. \*\*Open Science\*\* - Transparent methodology, reproducible results

6\. \*\*Safety Guardrails\*\* - WHO MEC rules prevent harmful recommendations

7\. \*\*Equitable Access\*\* - Offline-first design, multilingual support



\---



\## PART 1: Our Ethical Principles



\### 1.1 Core Principles



| Principle | Description |

|-----------|-------------|

| \*\*Beneficence\*\* | Our AI must benefit users by improving contraceptive decision-making |

| \*\*Non-maleficence\*\* | Our AI must not cause harm (WHO MEC safety rules prevent unsafe recommendations) |

| \*\*Autonomy\*\* | Users control their data and can delete at any time |

| \*\*Justice\*\* | Free access for underserved populations, offline capability for rural areas |

| \*\*Transparency\*\* | Explainable AI - users see WHY a method is recommended or restricted |

| \*\*Accountability\*\* | We are responsible for the AI's recommendations and safety |



\### 1.2 Target Population Considerations



NuruCare serves users in Sub-Saharan Africa, with special attention to:



| Consideration | Our Approach |

|---------------|--------------|

| \*\*Low internet connectivity\*\* | PWA offline capability, sync when connected |

| \*\*Multiple languages\*\* | English + Swahili support (extensible to others) |

| \*\*Low health literacy\*\* | Plain language explanations, myth-busting content |

| \*\*Sensitive topic\*\* | Private by design, no data sharing without consent |

| \*\*Cultural context\*\* | Educational content adapted from local datasets |



\---



\## PART 2: Data Collection \& Privacy



\### 2.1 What Data We Collect



| Category | Data Points | Purpose | Required? |

|----------|-------------|---------|-----------|

| \*\*Demographics\*\* | Age, gender, education level | Personalization | Yes |

| \*\*Clinical\*\* | Blood pressure, smoking status, migraine type | WHO MEC safety rules | Yes |

| \*\*Reproductive\*\* | Menstrual cycle, fertility intentions, parity | Method recommendations | Yes |

| \*\*Medical history\*\* | Breastfeeding status, postpartum weeks | Method safety | Yes |

| \*\*Preferences\*\* | Side effect concerns | Personalization | Optional |

| \*\*Usage data\*\* | Which methods viewed, time spent | Product improvement | Optional (anonymous) |



\### 2.2 What Data We DO NOT Collect



| Data Type | Reason |

|-----------|--------|

| \*\*Name\*\* | Not needed for clinical decisions |

| \*\*Physical address\*\* | Not needed (only county/region for demographics) |

| \*\*Government ID\*\* | Never collected |

| \*\*Payment information\*\* | Free service |

| \*\*GPS location\*\* | Not needed |

| \*\*Device contacts\*\* | Not needed |

| \*\*Photos/Media\*\* | Not needed |

| \*\*Call logs/SMS\*\* | Not needed |



\### 2.3 Data Flow Diagram

┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐

│ User │────▶│ Intake │────▶│ Encrypt │────▶│ Store │

│ Inputs │ │ Form │ │ (AES-256) │ │ (Supabase)│

└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘

│

▼

┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐

│ User │◀────│ Delete │◀────│ Expire │◀────│ 30 Days │

│ Control │ │ Data │ │ (Auto) │ │ Limit │

└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘



\### 2.4 Data Encryption



| Stage | Method |

|-------|--------|

| \*\*In transit\*\* | TLS 1.3 (HTTPS) |

| \*\*At rest (database)\*\* | AES-256 encryption |

| \*\*Session keys\*\* | Hashed (bcrypt), never stored raw |

| \*\*Partner sync tokens\*\* | Hashed, expire in 15 minutes |



\---



\## PART 3: Informed Consent



\### 3.1 Consent Process



Before collecting any data, users must:



1\. \*\*See\*\* a plain-language consent screen

2\. \*\*Read\*\* what data is collected and why

3\. \*\*Understand\*\* their rights (access, deletion, opt-out)

4\. \*\*Actively agree\*\* by clicking "I Consent"



\### 3.2 Consent Screen Text

📋 YOUR PRIVACY MATTERS



Before we begin, please understand:



✅ WHAT WE COLLECT:

• Age, gender, education (to personalize recommendations)

• Blood pressure, health history (for safety)

• Pregnancy intentions, menstrual cycle (for accurate advice)



❌ WHAT WE DON'T COLLECT:

• Your name, address, phone number, or ID



🔒 HOW WE PROTECT YOU:

• Your data is encrypted (AES-256)

• Automatically deleted after 30 days

• Never sold or shared with third parties

• You can delete your data anytime



⚠️ MEDICAL DISCLAIMER:

• NuruCare is NOT a substitute for medical advice

• Always consult a healthcare provider before starting contraception



Do you consent to share your health information for personalized

contraceptive recommendations?



\[ I CONSENT ] \[ I DO NOT CONSENT ]



\### 3.3 Age of Consent



| Age Group | Consent Requirement |

|-----------|---------------------|

| \*\*18+ years\*\* | Self-consent |

| \*\*15-17 years\*\* | Self-consent with parental notification (per Kenyan law for reproductive health) |

| \*\*Under 15 years\*\* | Redirect to healthcare provider |



\---



\## PART 4: Data Retention



\### 4.1 Retention Periods



| Data Type | Retention Period | Reason |

|-----------|-----------------|--------|

| \*\*Health profiles\*\* | 30 days | Enough time for decision-making, minimizes breach risk |

| \*\*Recommendations\*\* | 30 days | Audit trail for user questions |

| \*\*Sync tokens\*\* | 15 minutes | Security - short-lived tokens |

| \*\*Nurse session keys\*\* | 15 minutes | Security - short-lived access |

| \*\*Audit logs\*\* | 90 days | Security monitoring |

| \*\*Anonymous usage data\*\* | Indefinite | Product improvement (no PII) |



\### 4.2 Automatic Deletion



```sql

\-- Automated cleanup runs daily at midnight

DELETE FROM health\_profiles WHERE expires\_at < NOW();

DELETE FROM sync\_tokens WHERE expires\_at < NOW();

DELETE FROM nurse\_keys WHERE expires\_at < NOW();

4.3 User-Initiated Deletion

Users can delete their data at any time:



Click "Delete My Data" in settings



Confirm deletion



All associated data is permanently removed within 24 hours



4.4 Data Backup Policy

Aspect	Policy

Backup frequency	Daily (automated by Supabase)

Backup retention	7 days (point-in-time recovery)

Backup encryption	Yes

Backup location	Same region as primary data

PART 5: Data Sharing \& Third Parties

5.1 Third Party Services

Service	Data Shared	Purpose	Privacy Link

Supabase	Encrypted health data	Database hosting	https://supabase.com/privacy

Google Gemini API	Anonymous query text	AI recommendations	https://policies.google.com/privacy

Render	None (hosting only)	API hosting	https://render.com/privacy

Vercel	None (hosting only)	Frontend hosting	https://vercel.com/legal/privacy-policy

5.2 What We NEVER Share

❌ Never sell user data



❌ Never share with advertisers



❌ Never share with insurance companies



❌ Never share with employers



❌ Never share without explicit consent (except legal requirement)



5.3 Legal Compliance

NuruCare complies with:



Regulation	Applicability

Kenya Data Protection Act (2019)	Primary jurisdiction

GDPR	For EU users (if any)

HIPAA	Not directly applicable (not a medical provider)

PART 6: Safety \& Clinical Guardrails

6.1 WHO MEC Safety Rules

NuruCare implements WHO Medical Eligibility Criteria to prevent harm:



Rule	Condition	Action	Category

MEC-001	Age >35 AND smoking	Restrict combined pills	4 (Do not use)

MEC-002	Migraine with aura	Restrict combined pills	4 (Do not use)

MEC-003	BP ≥140/90	Restrict combined hormonal	3 (Caution)

MEC-004	Breastfeeding <6 weeks	Restrict combined hormonal	3 (Caution)

MEC-005	Age ≥40	Caution for combined methods	2 (Generally safe)

6.2 Medical Disclaimer

NuruCare is a decision-support tool, not a medical provider. Every recommendation includes:

⚠️ This is not medical advice. 

Consult a healthcare provider before starting any contraceptive method.

6.3 When We Refer to a Provider

NuruCare will not provide recommendations for:



Users with Category 4 contraindications (direct to provider)



Users with multiple Category 3 conditions



Users under 15 years old



Users requesting sterilization without meeting WHO criteria



6.4 Emergency Alerts

If a user enters life-threatening combinations, the app displays:

🚨 CRITICAL: Your health information indicates potential risks.

Please consult a healthcare provider IMMEDIATELY.

Do not use combined hormonal contraceptives without medical supervision.

PART 7: Open Science \& Reproducibility

7.1 Open Source Commitment

Component	Open Source?	Location

Code	✅ Yes (MIT License)	GitHub.com/brianodh/nurucare

WHO MEC rules	✅ Yes	backend/engine/who\_mec\_rules.json

Synthetic data	✅ Yes	data/synthetic/

Processing scripts	✅ Yes	data/processing/

API documentation	✅ Yes	docs/api\_documentation.md

Deployment guide	✅ Yes	docs/deployment\_guide.md

7.2 What We've Published

Asset	Format	Purpose

who\_mec\_rules.json	JSON	Transparent safety rules

synthetic\_profiles.json	JSON	55 test profiles for reproducibility

generate\_synthetic\_profiles.py	Python	Code to regenerate synthetic data

guardrail.py	Python	Complete guardrail engine

Extraction scripts	Python	How raw data was processed

7.3 Limitations Acknowledged

We openly acknowledge:



Smoking and migraine data are synthetic (not in source datasets)



Menstrual cycle data is from a small sample (96 women)



Generalizability - Primarily Kenya data, may not represent all of Sub-Saharan Africa



AI limitations - Recommendations are not substitutes for clinical judgment



PART 8: User Rights

8.1 Your Rights

Right	Description	How to Exercise

Right to access	See what data we have about you	Settings → Download My Data

Right to rectification	Correct inaccurate data	Edit intake form

Right to deletion	Delete your data	Settings → Delete My Data

Right to portability	Get your data in machine-readable format	Settings → Export (JSON/CSV)

Right to object	Stop processing your data	Stop using the app

Right to withdraw consent	Withdraw at any time	Settings → Withdraw Consent

8.2 How to Exercise Your Rights

Action	Steps

Download data	Settings → Download My Data → JSON or CSV

Delete data	Settings → Delete My Data → Confirm

Contact privacy officer	Email: privacy@nurucare.org (simulated for hackathon)

8.3 Response Timeline

Request Type	Response Time

Data access	Within 24 hours

Data deletion	Within 24 hours

Data correction	Immediate

Complex requests	Within 7 days

PART 9: AI-Specific Ethics

9.1 Explainability

NuruCare's AI is explainable by design:



Every recommendation includes a plain-language explanation



Every restriction includes the specific WHO MEC rule



Users can see why a method was recommended or restricted



Example:

❌ Combined Pill is not recommended for you.

Reason: You are over 35 and smoke.

WHO Category 4: Unacceptable health risk.

Alternative: Progestin-only pill or implant (no estrogen, safe for you).

9.2 Bias Mitigation

Bias Type	Mitigation Strategy

Data bias	Multiple datasets (service + survey + clinical)

Algorithmic bias	Rules-based guardrail before ML personalization

Cultural bias	Local dataset validation, Swahili support

Gender bias	Explicitly designed for female users (primary) with male partner sync

9.3 Human Oversight

Feature	Oversight

Guardrail rules	Defined by WHO MEC (medical experts)

Educational content	Reviewed by health expert (Moffat)

API decisions	Auditable via logs

Model updates	Manual review before deployment

9.4 Failure Mode Analysis

Failure Mode	Mitigation

API down	Service worker serves cached educational content

AI hallucination	Guardrail rules restrict unsafe recommendations

Data breach	Encryption, short retention, limited data collection

Model bias	Regular audits using synthetic test profiles

PART 10: Vulnerable Populations

10.1 Adolescents (15-17 years)

Consideration	Our Approach

Consent	Self-consent for reproductive health (per Kenyan law)

Parental notification	Recommended but not required

Content appropriateness	Age-appropriate language

Safety	Same WHO MEC rules apply

10.2 Rural/Low-Literacy Users

Consideration	Our Approach

Internet access	PWA offline capability

Literacy	Plain language, icons, Swahili option

Phone type	Mobile-first design, works on basic smartphones

10.3 Survivors of Gender-Based Violence

Consideration	Our Approach

Privacy	No data shared; session keys for nurse access only

Safety	Educational content includes GBV resources

Partner sync	Optional - never required

PART 11: Compliance Checklist

Requirement	Status	Evidence

Informed consent screen	✅	Implemented in intake flow

Data retention policy	✅	30 days, documented

User deletion capability	✅	Settings → Delete My Data

Data encryption in transit	✅	HTTPS only

Data encryption at rest	✅	Supabase AES-256

Third-party data sharing disclosure	✅	Section 5.1

Open science documentation	✅	GitHub public, MIT License

Medical disclaimer	✅	On every recommendation

Safety guardrails	✅	WHO MEC rules implemented

Age verification	✅	Age 15-60 validation

Bias mitigation plan	✅	Section 9.2

Human oversight	✅	Health expert on team

PART 12: Contact Information

Privacy Officer (Simulated for Hackathon)

Role	Name	Contact

Health Expert + QA	Moffat Mose	moffat@nurucare.org

AI Lead + Coordinator	Brian Odhiambo Ouma	brian@nurucare.org

Backend Lead	Alois Karanja Gitau	alois@nurucare.org

Frontend Lead	Lisa Adongo Akinyi	lisa@nurucare.org

Deployment Lead	Uvyne Chepchirchir Rop	uvyne@nurucare.org

Reporting Concerns

If you have concerns about:



Privacy violation → Contact privacy@nurucare.org



Safety issue → Contact safety@nurucare.org



Ethical concern → Contact ethics@nurucare.org



PART 13: Changes to This Statement

Version	Date	Changes	Author

1.0	2026-05-27	Initial ethics statement	Moffat Mose

We will notify users of material changes via:



Email (if provided)



In-app notification on next login



Updated date at top of this document



PART 14: Acknowledgment

By using NuruCare, you acknowledge that:



You have read and understood this ethics statement



You consent to data collection as described



You understand NuruCare is not a substitute for medical advice



You are at least 15 years old (or have parental consent)



You may withdraw consent at any time



Document Sign-off

Role	Name	Signature	Date

Health Expert + QA	Moffat Mose	✅ Approved	2026-05-27

AI Lead + Coordinator	Brian Odhiambo Ouma	✅ Approved	2026-05-27

Backend Lead	Alois Karanja Gitau	✅ Approved	2026-05-27

Frontend Lead	Lisa Adongo Akinyi	✅ Approved	2026-05-27

Deployment Lead	Uvyne Chepchirchir Rop	✅ Approved	2026-05-27

This ethics statement is a living document and will be updated as NuruCare evolves.



Prepared by: Moffat Mose (Health Expert + QA)

Project: NuruCare - AI for Reproductive Health in Africa

Hackathon: Data Science Africa 2026



