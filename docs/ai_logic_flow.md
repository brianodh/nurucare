\# NuruCare AI Logic Flow Documentation



\## Version: 1.0

\## Last Updated: May 24, 2026



\---



\## 1. Overview



NuruCare uses a \*\*two-tier hybrid AI approach\*\*:



| Tier | Name | Purpose | Technology |

|------|------|---------|------------|

| 1 | Safety Guardrail | Eliminate clinically unsafe methods | WHO MEC deterministic rules |

| 2 | Personalization | Rank safe methods by user preference | RAG + Gemini Flash API |



\---



\## 2. Input Variables



The AI requires 8 inputs from the user:



| Input | Type | Allowed Values | Source |

|-------|------|----------------|--------|

| age | integer | 15-49 years | User input |

| systolic\_bp | integer | 60-200 mmHg | User input |

| diastolic\_bp | integer | 40-120 mmHg | User input |

| smoking | boolean | true/false | User input |

| migraine\_type | string | "none", "without\_aura", "with\_aura" | User input |

| cycle\_regularity | string | "regular", "irregular" | User input |

| fertility\_intent | string | "want\_soon", "want\_later", "no\_more", "unsure" | User input |

| breastfeeding | boolean | true/false | User input |

| parity | integer | 0-10+ | User input |



\---



\## 3. Tier 1: WHO MEC Safety Guardrail



\### 3.1 Rule Evaluation Order



The guardrail evaluates rules in this order (priority from highest to lowest):

Rule 1: Critical Risk (Category 4)

↓

Rule 2: Major Restriction (Category 3)

↓

Rule 3: Minor Restriction (Category 2)





\### 3.2 Complete Rule Set



| Rule ID | Condition | Restricted Methods | WHO Category |

|---------|-----------|-------------------|--------------|

| MEC-001 | age > 35 AND smoking = true | Combined pills, patch, ring | 4 |

| MEC-002 | migraine = "with\_aura" | Combined pills, patch, ring | 4 |

| MEC-003 | systolic\_bp ≥ 140 OR diastolic\_bp ≥ 90 | Combined hormonal methods | 3 |

| MEC-004 | breastfeeding = true AND postpartum\_weeks < 6 | Combined hormonal methods | 3 |

| MEC-005 | age ≥ 40 | Combined hormonal methods | 2 |

| MEC-006 | breastfeeding = true AND postpartum\_weeks < 6 | Combined pills, patch, ring | 3 |



\### 3.3 Method Mapping



| Method ID | Display Name | Safe For |

|-----------|--------------|----------|

| combined\_pill | Daily Pill (Combined) | Only if no MEC-001,002,003,004,005 |

| progestin\_pill | Daily Pill (Mini-Pill) | Safe for all (no estrogen) |

| injectables | Depo-Provera (Injection) | Safe for all |

| implants | Implant (Jadelle) | Safe for all |

| iud\_copper | IUD (Copper) | Safe for all |

| iud\_hormonal | IUD (Hormonal - Mirena) | Safe for all |

| male\_condom | Male Condom | Safe for all |

| female\_condom | Female Condom | Safe for all |

| emergency | Emergency Pill (P2) | Safe for all |

| withdrawal | Withdrawal | Safe for all |

| rhythm | Rhythm/Safe Days | Safe for all |

| lam | LAM (Breastfeeding) | Only if breastfeeding |

| sterilization\_female | Tubal Ligation | Only if no\_more children |

| sterilization\_male | Vasectomy | Only if no\_more children |



\---



\## 4. Tier 2: Personalization (RAG + Gemini Flash)



\### 4.1 Scoring Formula



Each allowed method receives a confidence score based on:

Confidence Score = (Preference Match × 0.4) + (Medical Fit × 0.3) + (Effectiveness × 0.2) + (Accessibility × 0.1)





| Component | Weight | Description |

|-----------|--------|-------------|

| Preference Match | 40% | How well method aligns with fertility intent and side effect concerns |

| Medical Fit | 30% | Absence of contraindications (from Tier 1) |

| Effectiveness | 20% | Typical use effectiveness rate (from WHO) |

| Accessibility | 10% | Likelihood of method being available locally |



\### 4.2 Preference Matching Logic



| Fertility Intent | Best Method Categories |

|-----------------|----------------------|

| "want\_soon" (within 1 year) | Condoms, withdrawal, rhythm, progestin pill |

| "want\_later" (1-5 years) | Injectables, implants, IUD |

| "no\_more" | Sterilization, implants, IUD |



\### 4.3 Side Effect Concern Mapping



| Concern | Methods to Avoid | Better Alternatives |

|---------|-----------------|---------------------|

| Weight gain | Injectables | Implants, IUD, condoms |

| Acne | Progestin-only pills | Combined pills (if eligible), IUD |

| Mood changes | Combined pills | IUD, implants, condoms |

| Menstrual changes | Hormonal methods | Copper IUD, condoms |



\### 4.4 RAG Context



The Gemini Flash prompt includes:



1\. User's clinical profile (age, parity, fertility intent)

2\. WHO guideline excerpts (vector embeddings)

3\. Local myth-busting context (from dataset analysis)

4\. Regional effectiveness data (from Client Service Statistics)



\---



\## 5. Output Format



The AI returns:



```json

{

\&#x20; "recommended\\\_methods": \\\[

\&#x20;   {

\&#x20;     "method\\\_id": "implants",

\&#x20;     "name": "Implant (Jadelle)",

\&#x20;     "confidence\\\_score": 92,

\&#x20;     "explanation": "The implant is 99% effective and lasts 5 years. Since you don't want children for at least 2 years, this is an excellent option.",

\&#x20;     "benefits": \\\["Long-lasting", "Very effective", "Reversible"],

\&#x20;     "side\\\_effects": \\\["Irregular bleeding first 3-6 months", "Possible weight changes"],

\&#x20;     "myth\\\_buster": "Implants do NOT cause infertility. Fertility returns immediately after removal."

\&#x20;   }

\&#x20; ],

\&#x20; "restricted\\\_methods": \\\[

\&#x20;   {

\&#x20;     "method\\\_id": "combined\\\_pill",

\&#x20;     "reason": "Not safe for you because you have migraine with aura. Estrogen-containing pills increase stroke risk."

\&#x20;   }

\&#x20; ],

\&#x20; "requires\\\_provider": false,

\&#x20; "disclaimer": "This is not medical advice. Consult a healthcare provider before starting any contraceptive method."

}



## 6. Edge Cases



| Scenario | AI Response |

|---------|-----------------|

| HBP + migraine with aura | Critical alert: "Consult provider immediately" |

| All methods restricted | "Please speak with a healthcare provider for personalized guidance" |

| Wants children soon + wants sterilization | Educational note about reversibility |

| Irregular cycles + rhythm method warning | "Rhythm method may be less reliable with irregular cycles" |



## 7. Data Sources for Rules



| Rule Source | File Location |

|---------|-----------------|

| WHO MEC Categories | backend/engine/who\\\_mec\\\_rules.json |

| Method effectiveness | WHO Family Planning Handbook |

| Side effect profiles | Final Women Dataset analysis |

| Myth data | Student + Final Women datasets |



## 8. Version History



| Version | Date | Changes |

|---------|-----------------|---------------------|

| 1.0 | 2026-05-24 | Initial documentation |


