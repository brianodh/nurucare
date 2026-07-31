\# 📊 NuruCare - Dataset Extraction Log



\## Project: AI-Powered Contraceptive Decision-Support Platform

\## Author: Brian Odhiambo Ouma (AI Lead + Coordinator)

\## Date: May 27, 2026



\---



\## EXECUTIVE SUMMARY



This document logs the complete process of extracting, cleaning and validating all datasets used in NuruCare. A total of \*\*5 primary datasets\*\* were processed, comprising \*\*224,331 unique records\*\* and \*\*300+ extracted variables\*\*.



| Metric | Value |

|--------|-------|

| Total datasets processed | 5 |

| Total records analyzed | 224,331 |

| Total variables extracted | 300+ |

| Output files created | 25+ |

| Extraction success rate | 100% |



\---



\## PART 1: EXTRACTION METHODOLOGY



\### 1.1 Tools Used



| Tool | Version | Purpose |

|------|---------|---------|

| Python | 3.11+ | Primary programming language |

| Pandas | 2.0+ | Data manipulation and extraction |

| VS Code / Notepad | - | Script development |

| Git / GitHub | - | Version control |

| Command Prompt | - | Running scripts |



\### 1.2 Extraction Process Flow

Step 1: Locate Dataset File

↓

Step 2: Preview Columns \& Structure

↓

Step 3: Identify Target Variables

↓

Step 4: Create Extraction Script

↓

Step 5: Run Extraction with Error Handling

↓

Step 6: Validate Output \& Generate Statistics

↓

Step 7: Create Specialized Subsets

↓

Step 8: Save to data/processed/ directory

↓

Step 9: Commit to GitHub



\### 1.3 Challenges Overcome



| Challenge | Solution |

|-----------|----------|

| UnicodeDecodeError (UTF-8) | Used `encoding='latin1'` for all CSV reads |

| Different column naming conventions | Mapped `pdsXXX` to required variables |

| Nested folder paths | Moved files to `data/processed/` |

| Non-numeric age columns | Used `pd.to\_numeric(errors='coerce')` |

| Missing expected columns | Implemented column detection and mapping |



\---



\## PART 2: DATASET 1 - FINAL WOMEN DATA ANON



\### 2.1 Basic Information



| Property | Value |

|----------|-------|

| \*\*File Name\*\* | Final\_women\_Data\_ANON.csv |

| \*\*Source\*\* | Kenya DHS / Survey Data |

| \*\*Rows\*\* | 1,997 |

| \*\*Original Columns\*\* | 791 |

| \*\*Extracted Columns\*\* | 133 |

| \*\*Key Value\*\* | Contraceptive myths, side effects, fertility intentions |



\### 2.2 Extraction Script



| Property | Value |

|----------|-------|

| \*\*Script Name\*\* | `03\_extract\_final\_women\_final.py` |

| \*\*Location\*\* | `data/processing/03\_extract\_final\_women\_final.py` |

| \*\*Encoding Used\*\* | latin1 |



\### 2.3 Variables Extracted



| Category | Variables | Count |

|----------|-----------|-------|

| Demographics | woman\_id, age, education\_level, marital\_status, religion, ethnicity | 10 |

| Pregnancy History | ever\_given\_birth, children\_living, total\_children\_ever\_born, currently\_pregnant | 12 |

| Contraceptive Knowledge | knows\_pill, knows\_implants, knows\_iud, knows\_injectables, knows\_condom | 12 |

| Ever Used Contraception | ever\_used\_pill, ever\_used\_implants, ever\_used\_iud, ever\_used\_injectables | 12 |

| Current Use | currently\_using\_fp, current\_method, current\_method\_decided\_by | 5 |

| Method at Last Sex | fp\_used\_at\_last\_sex, last\_sex\_pill, last\_sex\_condom, last\_sex\_injectables | 8 |

| \*\*Myths (Critical)\*\* | myth\_injection\_infertility, myth\_contraceptives\_cause\_cancer (7 total) | 7 |

| \*\*Side Effects\*\* | problem\_bleeding, problem\_headache, problem\_weight\_gain (24 total) | 24 |

| Why Not Using FP | not\_using\_breastfeeding, not\_using\_fear\_side\_effects (18 total) | 18 |

| Fertility Intentions | fertility\_preference, fertility\_timing, preferred\_children\_count | 6 |

| Partner Dynamics | discussed\_fp\_with\_spouse, need\_permission\_for\_fp | 5 |



\### 2.4 Key Findings



| Finding | Value | Implication |

|---------|-------|-------------|

| Myth recognition rate | 94.0-94.5% | Widespread myths need busting |

| Want more children | 44.7% | Need reversible methods |

| Want no more children | 42.1% | Need LARC/sterilization |

| Women with FP use data | 1,670 (84%) | Strong behavioral data |



\### 2.5 Output Files Created



| File Name | Purpose |

|-----------|---------|

| `final\_women\_extracted\_complete.csv` | All 133 variables |

| `final\_women\_myths.csv` | 7 myths for educational module |

| `final\_women\_side\_effects.csv` | 24 side effect variables |

| `final\_women\_fertility.csv` | Fertility intentions |

| `final\_women\_contraceptive\_use.csv` | Method knowledge \& use |

| `final\_women\_not\_using.csv` | Reasons for not using FP |



\### 2.6 Challenges \& Resolutions



| Challenge | Resolution |

|-----------|------------|

| Column names used `qXXX` format instead of `vXXX` | Mapped using actual column names from preview |

| Age column had text data | Used `pd.to\_numeric(errors='coerce')` |

| Large file (791 columns) | Used `low\_memory=False` in pd.read\_csv |



\---



\## PART 3: DATASET 2 - CLIENT SERVICE STATISTICS



\### 3.1 Basic Information



| Property | Value |

|----------|-------|

| \*\*File Name\*\* | Client\_Service\_Statistics\_Data.csv |

| \*\*Source\*\* | Family planning service records |

| \*\*Rows\*\* | 216,539 |

| \*\*Original Columns\*\* | 33 |

| \*\*Extracted Columns\*\* | 29 |

| \*\*Key Value\*\* | REAL service data - method adoption patterns |



\### 3.2 Extraction Script



| Property | Value |

|----------|-------|

| \*\*Script Name\*\* | `04\_extract\_client\_service.py` |

| \*\*Location\*\* | `data/processing/04\_extract\_client\_service.py` |

| \*\*Encoding Used\*\* | latin1 |



\### 3.3 Variables Extracted



| Category | Variables | Count |

|----------|-----------|-------|

| Identifiers | visit\_id, unique\_id, county, division, facility\_name, organization | 6 |

| Demographics | gender, age, education\_level, number\_of\_children | 4 |

| \*\*Fertility Intentions\*\* | fertility\_intention | 1 |

| FP Status | fp\_status, project\_status | 2 |

| \*\*Previous Method\*\* | previous\_method, previous\_method\_recoded | 2 |

| \*\*Counseling\*\* | counseled, counseled\_recoded | 2 |

| \*\*Method Adopted\*\* | method\_adopted, method\_adopted\_recoded | 2 |

| Referrals | referred, referred\_method | 2 |

| Long-Acting | adopted\_long\_acting | 1 |

| Delivery Channel | delivery\_channel, delivery\_channel\_recoded | 2 |

| Time | year, month | 2 |



\### 3.4 Key Findings



| Finding | Value | Implication |

|---------|-------|-------------|

| \*\*Total clients\*\* | 216,539 | Massive scale validation |

| \*\*New users\*\* | 93,095 (43.0%) | Need educational module |

| \*\*Want children later\*\* | 101,306 (46.8%) | Need reversible methods |

| \*\*Male clients\*\* | 75,562 (34.9%) | Validates partner sync feature |

| \*\*Need referrals\*\* | 61,523 (28.4%) | Access gap to address |

| \*\*Condom adopters\*\* | 87,245 (40.3%) | Most common method |

| \*\*Implants + Injectables\*\* | 66,819 (30.9%) | Strong LARC adoption |



\### 3.5 Method Adoption Breakdown



| Method | Count | Percentage |

|--------|-------|------------|

| Condoms | 87,245 | 40.3% |

| Pills | 48,127 | 22.2% |

| Implants | 33,967 | 15.7% |

| Injectables | 32,852 | 15.2% |

| IUCD | 4,624 | 2.1% |



\### 3.6 Output Files Created



| File Name | Purpose |

|-----------|---------|

| `client\_service\_extracted.csv` | All 29 variables |

| `client\_service\_method\_adoption.csv` | Method adoption patterns |

| `client\_service\_fertility.csv` | Fertility intentions |

| `client\_service\_counseling.csv` | Counseling impact data |

| `client\_service\_geography.csv` | Geographic distribution |

| `client\_service\_summary.txt` | Statistics for pitch |



\---



\## PART 4: DATASET 3 - PROSPECTIVE MORBIDITY SURVEY



\### 4.1 Basic Information



| Property | Value |

|----------|-------|

| \*\*File Name\*\* | Prospective\_Morbidity\_Survey.csv |

| \*\*Source\*\* | Clinical survey of women seeking care |

| \*\*Rows\*\* | 3,215 |

| \*\*Original Columns\*\* | 188 |

| \*\*Extracted Columns\*\* | 36 |

| \*\*Key Value\*\* | ACTUAL blood pressure readings for WHO MEC rules |



\### 4.2 Extraction Script



| Property | Value |

|----------|-------|

| \*\*Script Name\*\* | `05\_extract\_prospective\_morbidity\_fixed.py` |

| \*\*Location\*\* | `data/processing/05\_extract\_prospective\_morbidity\_fixed.py` |

| \*\*Encoding Used\*\* | latin1 |



\### 4.3 Variables Extracted



| Category | Variables | Count |

|----------|-----------|-------|

| Identifiers | record\_id, province, county, district, facility\_type | 5 |

| Demographics | age, residence, marital\_status, education, religion, occupation | 6 |

| \*\*Blood Pressure (CRITICAL)\*\* | systolic\_bp, diastolic\_bp, bp\_reading, has\_hypertension | 4 |

| Pregnancy History | total\_pregnancies, live\_births, living\_children, miscarriages, induced\_abortions | 5 |

| Contraceptive History | used\_contraception\_before, contraceptive\_pills, contraceptive\_implants | 10 |

| \*\*Fertility Intentions\*\* | fertility\_intention | 1 |

| Clinical | gestational\_age\_weeks, reason\_for\_care, diagnosis | 3 |

| FP Counseling | counseled\_on\_fp, given\_fp\_method | 2 |



\### 4.4 Key Findings



| Finding | Value | Implication |

|---------|-------|-------------|

| \*\*Mean systolic BP\*\* | 113.1 mmHg | Baseline for synthetic data |

| \*\*Mean diastolic BP\*\* | 70.4 mmHg | Baseline for synthetic data |

| \*\*Hypertension (≥140/90)\*\* | 194 (6.0%) | Need combined pill restriction |

| \*\*Women over 35\*\* | 304 (9.5%) | Age-related restrictions |

| \*\*Need combined pill restriction\*\* | 466 (14.5%) | WHO MEC Category 3-4 |

| \*\*Unintended pregnancies\*\* | 1,121 (35%) | Validates need for app |

| \*\*Women with miscarriages\*\* | 530 (16.5%) | Educational content need |



\### 4.5 Column Mapping (pdsXXX format)



| Documentation Name | Actual Column Name |

|--------------------|---------------------|

| v101 (age) | pds101 |

| v315s (systolic BP) | pds315s |

| v315d (diastolic BP) | pds315d |

| v201 (pregnancies) | pds201 |

| v208 (fertility intentions) | pds208 |



\### 4.6 Output Files Created



| File Name | Purpose |

|-----------|---------|

| `prospective\_morbidity\_extracted.csv` | All 36 variables |

| `prospective\_morbidity\_blood\_pressure.csv` | BP data for WHO MEC |

| `prospective\_morbidity\_fertility.csv` | Fertility intentions |

| `prospective\_morbidity\_clinical.csv` | Clinical summary |

| `prospective\_morbidity\_summary.txt` | Statistics for pitch |



\---



\## PART 5: DATASET 4 - MC BASELINE



\### 5.1 Basic Information



| Property | Value |

|----------|-------|

| \*\*File Name\*\* | MC\_Baseline\_final.csv |

| \*\*Source\*\* | Menstrual health baseline survey |

| \*\*Rows\*\* | 96 |

| \*\*Original Columns\*\* | 361 |

| \*\*Extracted Columns\*\* | 53 |

| \*\*Key Value\*\* | Menstrual cycle regularity, symptoms, menstrual myths |



\### 5.2 Extraction Script



| Property | Value |

|----------|-------|

| \*\*Script Name\*\* | `06\_extract\_mc\_baseline\_fixed.py` |

| \*\*Location\*\* | `data/processing/06\_extract\_mc\_baseline\_fixed.py` |

| \*\*Encoding Used\*\* | latin1 |



\### 5.3 Variables Extracted



| Category | Variables | Count |

|----------|-----------|-------|

| Identifiers | record\_id, site | 2 |

| Demographics | age | 1 |

| \*\*Menstrual Cycle\*\* | cycle\_pattern, cycle\_length\_days, days\_between\_periods, last\_period\_start, next\_period\_expected, menstrual\_flow\_quantity, currently\_menstruating | 7 |

| \*\*Menstrual Symptoms\*\* | abdominal\_pain, back\_pain, irregular\_periods, lack\_of\_sleep, lack\_of\_energy, negative\_moods (with severity) | 12 |

| \*\*Menstrual Myths\*\* | myth\_swimming\_dangerous, myth\_periods\_clean\_dirty\_blood, myth\_blood\_comes\_from\_urethra, myth\_all\_get\_bad\_tempered (14 total) | 14 |

| \*\*Menstrual Attitudes\*\* | attitude\_periods\_nuisance, attitude\_periods\_embarrassing, attitude\_keep\_quiet (11 total) | 11 |

| Sexual History | ever\_had\_sex, age\_first\_sex, ever\_pregnant, number\_of\_births | 4 |



\### 5.4 Column Mapping



| Documentation Name | Actual Column Name |

|--------------------|---------------------|

| v403 (cycle pattern) | q4\_4 |

| v402 (cycle length) | q4\_2 |

| v405 (last period) | q4\_5 |

| v409aa (abdominal pain) | q4\_9a |

| v201a (myth) | q2\_1a |



\### 5.5 Output Files Created



| File Name | Purpose |

|-----------|---------|

| `mc\_baseline\_extracted.csv` | All 53 variables |

| `mc\_baseline\_cycle\_data.csv` | Cycle regularity and length |

| `mc\_baseline\_menstrual\_myths.csv` | Menstrual-specific myths |

| `mc\_baseline\_symptoms.csv` | Menstrual symptoms data |

| `mc\_baseline\_attitudes.csv` | Cultural attitudes |

| `mc\_baseline\_summary.txt` | Statistics for pitch |



\---



\## PART 6: DATASET 5 - STUDENT DATASET



\### 6.1 Basic Information



| Property | Value |

|----------|-------|

| \*\*File Name\*\* | Student Dataset.csv |

| \*\*Source\*\* | Adolescent health survey |

| \*\*Rows\*\* | 2,484 |

| \*\*Original Columns\*\* | 279 |

| \*\*Extracted Columns\*\* | 51 |

| \*\*Key Value\*\* | Adolescent perspectives on contraception |



\### 6.2 Extraction Script



| Property | Value |

|----------|-------|

| \*\*Script Name\*\* | `07\_extract\_student\_dataset.py` |

| \*\*Location\*\* | `data/processing/07\_extract\_student\_dataset.py` |

| \*\*Encoding Used\*\* | latin1 |



\### 6.3 Variables Extracted



| Category | Variables | Count |

|----------|-----------|-------|

| Demographics | gender, age, class, religion | 4 |

| \*\*Contraceptive Knowledge\*\* | heard\_of\_pill, heard\_of\_condoms, heard\_of\_implants (10 total) | 10 |

| \*\*Last Sex Method\*\* | last\_sex\_condom, last\_sex\_pill, last\_sex\_implant, last\_sex\_no\_method (9 total) | 9 |

| Why Not Using | reason\_not\_using | 1 |

| Access | knows\_fp\_source, knows\_condom\_source | 2 |

| \*\*Myths (GOLD)\*\* | myth\_condoms\_mean\_promiscuous, myth\_condoms\_mean\_no\_trust, myth\_contraceptives\_encourage\_sex, myth\_acceptable\_to\_beat\_wife, myth\_sex\_only\_man\_woman | 5 |

| HIV Knowledge | hiv\_unprotected\_sex, hiv\_shared\_needles, hiv\_mother\_to\_child, prevent\_hiv\_abstinence, prevent\_hiv\_condoms (9 total) | 9 |

| \*\*Information Sources\*\* | info\_teacher, info\_health\_center, info\_internet, info\_mother, info\_father, info\_friend (8 total) | 8 |

| Opinion | should\_rh\_be\_taught | 1 |

| Sexual Activity | ever\_had\_sex | 1 |



\### 6.4 Key Findings



| Finding | Value | Implication |

|---------|-------|-------------|

| \*\*Female students\*\* | 1,374 (55.3%) | Primary user segment |

| \*\*Male students\*\* | 1,101 (44.3%) | Partner sync relevance |

| \*\*Mean age\*\* | 16.6 years | Adolescent focus validated |

| \*\*Myth: contraceptives encourage sex\*\* | 99.1% responded | Widespread myth to bust |

| \*\*Myth: acceptable to beat wife\*\* | 99.4% responded | GBV education needed |

| \*\*Method awareness\*\* | 100% for all methods | Knowledge not the barrier |

| \*\*Trust teachers\*\* | 100% | School distribution channel |

| \*\*Trust health centers\*\* | 100% | Referral partner |

| \*\*Trust internet\*\* | 100% | Digital delivery validated |



\### 6.5 Output Files Created



| File Name | Purpose |

|-----------|---------|

| `student\_dataset\_extracted.csv` | All 51 variables |

| `student\_myths.csv` | Adolescent myths for educational module |

| `student\_knowledge\_gaps.csv` | Awareness gaps for content prioritization |

| `student\_info\_sources.csv` | Trusted channels for product design |

| `student\_contraceptive\_use.csv` | Adolescent use patterns for validation |

| `student\_dataset\_summary.txt` | Statistics for pitch |



\---



\## PART 7: SYNTHETIC DATA GENERATION



\### 7.1 Purpose



Synthetic data was created to fill gaps where real clinical data is sensitive or unavailable, specifically:

\- Smoking status (not in any dataset)

\- Migraine history (not in any dataset)



\### 7.2 Generation Script



| Property | Value |

|----------|-------|

| \*\*Script Name\*\* | `generate\_synthetic\_profiles.py` |

| \*\*Location\*\* | `data/synthetic/generate\_synthetic\_profiles.py` |



\### 7.3 Synthetic Variables



| Variable | Distribution | Justification |

|----------|--------------|---------------|

| Smoking status | 2-3% of women, 5% of men | WHO Africa estimates |

| Migraine type | 70% none, 20% without aura, 10% with aura | Global prevalence |



\### 7.4 Output Files



| File Name | Description |

|-----------|-------------|

| `synthetic\_profiles.json` | 55 synthetic patient profiles (JSON format) |

| `synthetic\_profiles.csv` | 55 synthetic patient profiles (CSV format for Excel) |



\### 7.5 Profile Types



| Type | Count | Description |

|------|-------|-------------|

| Regular profiles | 50 | Based on demographic distributions |

| Edge cases | 5 | Specific clinical scenarios for testing |



\---



\## PART 8: FILE INVENTORY



\### 8.1 Location: `data/processed/`



\#### From Final Women ANON (Dataset 1)

final\_women\_extracted\_complete.csv # 1,997 rows, 133 columns

final\_women\_myths.csv # 7 myths for educational module

final\_women\_side\_effects.csv # 24 side effect variables

final\_women\_fertility.csv # Fertility intentions

final\_women\_contraceptive\_use.csv # Method knowledge \& use

final\_women\_not\_using.csv # Reasons for not using FP





\#### From Client Service Statistics (Dataset 2)

client\_service\_extracted.csv # 216,539 rows, 29 columns

client\_service\_method\_adoption.csv # Method adoption patterns

client\_service\_fertility.csv # Fertility intentions

client\_service\_counseling.csv # Counseling impact data

client\_service\_geography.csv # Geographic distribution

client\_service\_summary.txt # Statistics for pitch





\#### From Prospective Morbidity (Dataset 3)

prospective\_morbidity\_extracted.csv # 3,215 rows, 36 columns

prospective\_morbidity\_blood\_pressure.csv # BP data for WHO MEC

prospective\_morbidity\_fertility.csv # Fertility intentions

prospective\_morbidity\_clinical.csv # Clinical summary

prospective\_morbidity\_summary.txt # Statistics for pitch





\#### From MC Baseline (Dataset 4)

mc\_baseline\_extracted.csv # 96 rows, 53 columns

mc\_baseline\_cycle\_data.csv # Cycle regularity \& length

mc\_baseline\_menstrual\_myths.csv # Menstrual myths

mc\_baseline\_symptoms.csv # Menstrual symptoms

mc\_baseline\_attitudes.csv # Cultural attitudes

mc\_baseline\_summary.txt # Statistics for pitch





\#### From Student Dataset (Dataset 5)

student\_dataset\_extracted.csv # 2,484 rows, 51 columns

student\_myths.csv # Adolescent myths

student\_knowledge\_gaps.csv # Awareness gaps

student\_info\_sources.csv # Trusted channels

student\_contraceptive\_use.csv # Contraceptive use data

student\_dataset\_summary.txt # Statistics for pitch





\### 8.2 Location: `data/synthetic/`

synthetic\_profiles.json # 55 synthetic patient profiles

synthetic\_profiles.csv # Same data in CSV format

generate\_synthetic\_profiles.py # Generation script





\---



\## PART 9: EXTRACTION SCRIPTS INVENTORY



| Script Name | Location | Purpose |

|-------------|----------|---------|

| `01\_extract\_final\_women.py` | `data/processing/` | Initial extraction (deprecated) |

| `02\_extract\_final\_women\_corrected.py` | `data/processing/` | Corrected extraction (deprecated) |

| `03\_extract\_final\_women\_final.py` | `data/processing/` | FINAL Final Women extraction |

| `04\_extract\_client\_service.py` | `data/processing/` | Client Service extraction |

| `05\_extract\_prospective\_morbidity\_fixed.py` | `data/processing/` | FINAL Prospective Morbidity extraction |

| `06\_extract\_mc\_baseline\_fixed.py` | `data/processing/` | FINAL MC Baseline extraction |

| `07\_extract\_student\_dataset.py` | `data/processing/` | Student Dataset extraction |

| `generate\_synthetic\_profiles.py` | `data/synthetic/` | Synthetic data generator |

| `view\_all\_columns.py` | `data/processing/` | Column inspection utility |

| `view\_mc\_columns.py` | `data/processing/` | MC column inspection |

| `auto\_detect\_mc.py` | `data/processing/` | Auto-detection for MC |



\---



\## PART 10: REPRODUCIBILITY INSTRUCTIONS



\### 10.1 To Reproduce This Extraction



1\. \*\*Clone the repository:\*\*

&#x20;  ```bash

&#x20;  git clone https://github.com/brianodh/nurucare.git

&#x20;  cd nurucare



2\. Install dependencies:



pip install pandas openpyxl



3\. Place datasets in Downloads folder:



Final\_women\_Data\_ANON.csv



Client\_Service\_Statistics\_Data.csv



Prospective\_Morbidity\_Survey.csv



MC\_Baseline\_final.csv



Student Dataset.csv



4\. Run extraction scripts in order:

python data/processing/03\_extract\_final\_women\_final.py

python data/processing/04\_extract\_client\_service.py

python data/processing/05\_extract\_prospective\_morbidity\_fixed.py

python data/processing/06\_extract\_mc\_baseline\_fixed.py

python data/processing/07\_extract\_student\_dataset.py

5\. Generate synthetic profiles:

python data/synthetic/generate\_synthetic\_profiles.py

10.2 Expected Output

After running all scripts, you should have:



25+ CSV files in data/processed/



2 files in data/synthetic/



Summary statistics printed to console



PART 11: ETHICS \& DATA PRIVACY

11.1 Data Handling

Principle	Implementation

Anonymization	All datasets are fully anonymized (no names, phone numbers, addresses)

No re-identification	Cryptographic tokens used, not raw identifiers

Data retention	Health data stored for 30 days maximum

Open Science	WHO MEC rule mappings published for reproducibility

11.2 Missing Data Justification

Missing Variable	Reason	Solution

Smoking status	Not collected in any dataset	Synthetic based on WHO Africa estimates

Migraine history	Not collected in any dataset	Synthetic based on global prevalence

PART 12: CONCLUSION

12.1 Summary of Achievements

✅ 5 primary datasets fully extracted and validated

✅ 224,331 total records processed

✅ 300+ variables extracted

✅ 25+ specialized output files created

✅ All WHO MEC clinical variables (except smoking/migraines) available as real data

✅ Myth data from both adult women and adolescents

✅ Side effect data for educational navigator

✅ Menstrual cycle data for personalization

✅ Fertility intentions from multiple sources

✅ Partner dynamics for sync feature validation

