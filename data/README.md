# NuruCare - Data Documentation

## Overview

This directory contains all datasets used for training, validating and testing the NuruCare AI contraceptive decision-support platform. Data comes from real family planning service records, clinical surveys and student questionnaires across Kenya.

**Total records analyzed:** ~224,000+

---

## Data Sources Summary

| Dataset | Records | Key Value | Format |
|---------|---------|-----------|--------|
| Client Service Statistics | 216,539 | Method adoption, fertility intentions | CSV |
| Final Women Data ANON | 1,997 | Contraceptive myths, side effects | CSV |
| Prospective Morbidity Survey | 3,215 | Blood pressure, clinical data | CSV |
| MC Baseline | 96 | Menstrual cycle, symptoms | CSV |
| Student Dataset | 2,484 | Adolescent myths, knowledge gaps | CSV |

---

## Dataset 1: Client Service Statistics

**Source:** Real family planning service delivery data from Kenya

**Records:** 216,539

**Key Variables:**

| Variable | Description | Use in NuruCare |
|----------|-------------|-----------------|
| `fertilityintention` | Wants children? When? | Personalization (LARC vs short-term) |
| `methodadopted` | Which method client chose | Recommendation validation |
| `fpstatus` | New or returning user | User segmentation |
| `counseled` | Received counseling | Impact metric |
| `referred` | Required referral | Access gap identification |

**Key Findings for Pitch:**
- 43% are first-time FP users → need education
- 46.8% want children later → need reversible methods
- 34.9% are male → validates partner sync feature

---

## Dataset 2: Final Women Data ANON

**Source:** Women's health survey (Kenya)

**Records:** 1,997

**Key Variables:**

| Variable | Description | Use in NuruCare |
|----------|-------------|-----------------|
| `v378` - `v384` | 7 contraceptive myths | Educational module (Myth vs Fact) |
| `v334a` - `v336x` | Side effects experienced | Side Effect Navigator |
| `v341a` - `v341w` | Why not using contraception | Barrier analysis |
| `v602` - `v612` | Fertility intentions | Personalization |

**The 7 Myths Identified:**

| Variable | Myth Statement |
|----------|----------------|
| v378 | Contraceptive injection causes infertility |
| v379 | Contraceptives cause health problems |
| v380 | Contraceptives harm the womb |
| v381 | Contraceptives reduce sexual urge |
| v382 | Contraceptives cause cancer |
| v383 | Contraceptives cause deformed babies |
| v384 | Contraceptives are dangerous |

**Key Findings:**
- 94% of women responded to myth questions
- 44.7% want more children, 42.1% want no more

---

## Dataset 3: Prospective Morbidity Survey

**Source:** Clinical survey of women seeking care (Kenya)

**Records:** 3,215

**Key Variables:**

| Variable | Description | Use in NuruCare |
|----------|-------------|-----------------|
| `pds315s` / `pds315d` | Systolic/Diastolic BP | WHO MEC safety rules |
| `pds101` | Age | WHO MEC rules |
| `pds201` - `pds205` | Pregnancy history | Parity calculations |
| `pds208` | Fertility intentions | Personalization |

**Key Findings for Pitch:**
- Mean BP: 113/70 mmHg
- Hypertension (≥140/90): 6.0% (194 women)
- Would restrict combined pills: 14.5% (466 women)
- Unintended pregnancies: 35%

---

## Dataset 4: MC Baseline

**Source:** Menstrual health study (Kenya)

**Records:** 96

**Key Variables:**

| Variable | Description | Use in NuruCare |
|----------|-------------|-----------------|
| `q4_2` | Cycle length (days) | Cycle personalization |
| `q4_4` | Cycle pattern (regular/irregular) | Rhythm method suitability |
| `q4_9a` - `q4_9g` | Menstrual symptoms | Side Effect Navigator |
| `q2_1a` - `q2_1n` | Menstrual myths | Educational module |

**Key Findings:**
- Detailed cycle regularity data
- Menstrual symptom prevalence documented
- 14 menstrual-specific myths identified

---

## Dataset 5: Student Dataset

**Source:** Adolescent health survey (Kenya)

**Records:** 2,484

**Key Variables:**

| Variable | Description | Use in NuruCare |
|----------|-------------|-----------------|
| `s701` / `s702` | Gender, Age | Demographics |
| `s801a` - `s801i` | Contraceptive myths | Educational module |
| `s504a` - `s504j` | Method awareness | Knowledge gap analysis |
| `s601aa` - `s601as` | Information sources | Channel strategy |

**Key Findings for Pitch:**
- 99% responded to myth questions
- 100% aware of all contraceptive methods
- 100% trust teachers and health centers for information
- 55.3% female, 44.3% male

---

## Synthetic Data

### Purpose
Real clinical data for smoking and migraines was not available in the source datasets. Synthetic data fills this gap for WHO MEC rule demonstration.

### Files

| File | Description |
|------|-------------|
| `synthetic_profiles.json` | 55 synthetic patient profiles (JSON format) |
| `synthetic_profiles.csv` | Same profiles (CSV format for Excel) |
| `generate_synthetic_profiles.py` | Python script to regenerate synthetic data |

### Generation Method

The synthetic profiles are generated using:
- **Age distribution:** Based on Kenya DHS data
- **Blood pressure:** Age-appropriate normal ranges + hypertension prevalence
- **Smoking:** 2-3% rate (WHO Africa estimates)
- **Migraine:** 70% none, 20% without aura, 10% with aura
- **Fertility intentions:** Based on parity and age

### Edge Cases Included

| Profile ID | Scenario | Purpose |
|------------|----------|---------|
| EDGE_001 | Age >35 + smoking | Test MEC-001 (Category 4) |
| EDGE_002 | Hypertension (145/95) | Test MEC-003 (Category 3) |
| EDGE_003 | Migraine with aura | Test MEC-002 (Category 4) |
| EDGE_004 | Irregular cycles | Test rhythm method warning |
| EDGE_005 | Breastfeeding + no more children | Test MEC-004 and LARC recommendation |

---

## Data Processing Pipeline

### Step 1: Raw Data Extraction
Each dataset was processed using Python scripts in `/data/processing/`:

| Script | Dataset |
|--------|---------|
| `01_extract_final_women.py` | Final Women Data ANON |
| `02_extract_client_service.py` | Client Service Statistics |
| `03_extract_prospective_morbidity.py` | Prospective Morbidity |
| `04_extract_mc_baseline.py` | MC Baseline |
| `05_extract_student.py` | Student Dataset |

### Step 2: Variable Selection
Only clinically relevant variables were extracted (300+ total)

### Step 3: Specialized Outputs
Each dataset was split into focused CSV files:
- `*_myths.csv` - Myth statements for educational module
- `*_side_effects.csv` - Side effect data for navigator
- `*_fertility.csv` - Fertility intentions for personalization
- `*_blood_pressure.csv` - BP data for WHO MEC rules

### Step 4: Validation
- Range checks for all numerical values
- Cross-dataset consistency validation
- Edge case testing

---

## Ethical Considerations

### Privacy
- No personally identifiable information (PII) in extracted datasets
- Cryptographic tokens used for any cross-referencing
- Data retention: 30 days maximum for user data

### Open Science
All datasets are:
- Documented with variable descriptions
- Reproducible via provided scripts
- Synthetic data generated for missing clinical variables

### Data Sources Attribution
All real data comes from authorized sources for the Data Science Africa 2026 Hackathon. Synthetic data is original to NuruCare.

---

## Reproducibility

To reproduce this data processing:

```bash
# Clone the repository
git clone https://github.com/brianodh/nurucare.git
cd nurucare

# Install dependencies
pip install pandas numpy

# Run extraction scripts
python data/processing/01_extract_final_women.py
python data/processing/02_extract_client_service.py
python data/processing/03_extract_prospective_morbidity.py
python data/processing/04_extract_mc_baseline.py
python data/processing/05_extract_student.py

# Generate synthetic profiles
python data/synthetic/generate_synthetic_profiles.py