"""
Dataset 4: MC Baseline - Variable Extraction
Extracts variables for: Menstrual cycle regularity, cycle length, symptoms, myths

This dataset powers the menstrual cycle personalization and side effect navigator!
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURATION - UPDATE THIS PATH
# ============================================

# TODO: Change this to where YOUR file is located
INPUT_FILE = r"C:\Users\brian\Downloads\MC_Baseline_final_ANON.csv"

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("DATASET 4: MC Baseline - MENSTRUAL CYCLE DATA EXTRACTION")
print("=" * 70)
print("🩸 This dataset contains menstrual cycle data for personalization!")

# ============================================
# LOAD DATASET
# ============================================

print("\n📂 Loading dataset...")

# Try different encodings
encodings = ['latin1', 'utf-8', 'cp1252', 'ISO-8859-1']

df = None
for encoding in encodings:
    try:
        df = pd.read_csv(INPUT_FILE, encoding=encoding, low_memory=False)
        print(f"✅ Loaded with {encoding} encoding: {len(df):,} rows, {len(df.columns)} columns")
        break
    except UnicodeDecodeError:
        print(f"   Failed with {encoding}, trying next...")
        continue
    except FileNotFoundError:
        print(f"❌ File not found at: {INPUT_FILE}")
        print("\n📌 Please update the INPUT_FILE path to where your file is located.")
        print("   Current path:", INPUT_FILE)
        exit(1)
    except Exception as e:
        print(f"   Error with {encoding}: {e}")
        continue

if df is None:
    print("\n❌ Could not read file with any encoding.")
    print("   The file might be Excel (.xlsx). Try changing the extension.")
    exit(1)

# ============================================
# SEE WHAT COLUMNS WE HAVE
# ============================================

print("\n📋 First 50 columns in this dataset:")
for i, col in enumerate(df.columns[:50]):
    print(f"   {i+1:2d}. {col}")

if len(df.columns) > 50:
    print(f"   ... and {len(df.columns) - 50} more columns")

# ============================================
# EXTRACT VARIABLES (Based on documentation)
# ============================================

print("\n📊 Extracting variables...")

extracted = {}

# ----------------------------------------------------------------------
# 1. IDENTIFIERS & DEMOGRAPHICS
# ----------------------------------------------------------------------
if 'vq01' in df.columns:
    extracted['individual_id'] = df['vq01']
if 'v102' in df.columns:
    extracted['age'] = df['v102']
elif 'age' in df.columns:
    extracted['age'] = df['age']
if 's701' in df.columns:
    extracted['gender'] = df['s701']
if 's702' in df.columns:
    extracted['age_alt'] = df['s702']

print("   ✅ Extracted demographics")

# ----------------------------------------------------------------------
# 2. MENSTRUAL CYCLE REGULARITY (CRITICAL!)
# ----------------------------------------------------------------------
if 'v403' in df.columns:
    extracted['cycle_pattern'] = df['v403']
    print("   ✅ Found cycle pattern (v403)")
elif 'q403' in df.columns:
    extracted['cycle_pattern'] = df['q403']
    print("   ✅ Found cycle pattern (q403)")

if 'v408' in df.columns:
    extracted['cycle_interval_same'] = df['v408']
    print("   ✅ Found cycle regularity (v408)")
elif 'q408' in df.columns:
    extracted['cycle_interval_same'] = df['q408']

# ----------------------------------------------------------------------
# 3. CYCLE LENGTH (For personalization)
# ----------------------------------------------------------------------
if 'v402' in df.columns:
    extracted['cycle_length_days'] = df['v402']
    print("   ✅ Found cycle length (v402)")
elif 'q402' in df.columns:
    extracted['cycle_length_days'] = df['q402']

if 'v407' in df.columns:
    extracted['days_between_periods'] = df['v407']
    print("   ✅ Found days between periods (v407)")

# ----------------------------------------------------------------------
# 4. LAST MENSTRUAL PERIOD (LMP)
# ----------------------------------------------------------------------
if 'v405' in df.columns:
    extracted['last_period_start'] = df['v405']
    print("   ✅ Found LMP (v405)")
if 'v406' in df.columns:
    extracted['next_period_expected'] = df['v406']

# ----------------------------------------------------------------------
# 5. MENSTRUAL FLOW & CURRENT STATUS
# ----------------------------------------------------------------------
if 'v401' in df.columns:
    extracted['menstrual_flow_quantity'] = df['v401']
if 'v404' in df.columns:
    extracted['currently_menstruating'] = df['v404']

# ----------------------------------------------------------------------
# 6. MENSTRUAL SYMPTOMS (For side effect navigator)
# ----------------------------------------------------------------------
symptoms = {
    'v409aa': 'abdominal_pain',
    'v409ab': 'abdominal_pain_severity',
    'v409ba': 'back_pain',
    'v409bb': 'back_pain_severity',
    'v409ca': 'irregular_periods',
    'v409cb': 'irregular_periods_severity',
    'v409da': 'lack_of_sleep',
    'v409db': 'lack_of_sleep_severity',
    'v409ea': 'lack_of_energy',
    'v409eb': 'lack_of_energy_severity',
    'v409fa': 'negative_moods',
    'v409fb': 'negative_moods_severity',
}

for col, name in symptoms.items():
    if col in df.columns:
        extracted[f'symptom_{name}'] = df[col]

print("   ✅ Extracted menstrual symptoms")

# ----------------------------------------------------------------------
# 7. MENSTRUAL MYTHS (GOLD for educational module!)
# ----------------------------------------------------------------------
menstrual_myths = {
    'v201a': 'myth_travel_changes_cycle',
    'v201g': 'myth_swimming_dangerous',
    'v201i': 'myth_periods_clean_dirty_blood',
    'v201m': 'myth_blood_comes_from_urethra',
    'v201n': 'myth_all_get_bad_tempered',
}

for col, name in menstrual_myths.items():
    if col in df.columns:
        extracted[f'menstrual_{name}'] = df[col]
        print(f"   ✅ Found menstrual myth: {name}")

# ----------------------------------------------------------------------
# 8. MENSTRUAL ATTITUDES (Cultural context)
# ----------------------------------------------------------------------
attitudes = {
    'v202d': 'attitude_periods_nuisance',
    'v202e': 'attitude_periods_embarrassing',
    'v202g': 'attitude_keep_quiet_about_periods',
}

for col, name in attitudes.items():
    if col in df.columns:
        extracted[f'attitude_{name}'] = df[col]

print("   ✅ Extracted menstrual attitudes")

# ----------------------------------------------------------------------
# 9. SEXUAL & PREGNANCY HISTORY
# ----------------------------------------------------------------------
if 'v301' in df.columns:
    extracted['ever_had_sex'] = df['v301']
if 'v303' in df.columns:
    extracted['age_first_sex'] = df['v303']
if 'v305' in df.columns:
    extracted['ever_pregnant'] = df['v305']
if 'v306' in df.columns:
    extracted['number_of_births'] = df['v306']

print("   ✅ Extracted sexual history")

# ----------------------------------------------------------------------
# 10. CONTRACEPTIVE USE (Vaginal insertion methods)
# ----------------------------------------------------------------------
if 'v602' in df.columns:
    extracted['inserted_to_prevent_pregnancy'] = df['v602']
    print("   ✅ Found contraceptive insertion data")

# ============================================
# CREATE DATAFRAME
# ============================================

print("\n💾 Creating dataset...")

df_extracted = pd.DataFrame(extracted)

# Save main extracted file
output_file = OUTPUT_DIR / "mc_baseline_extracted.csv"
df_extracted.to_csv(output_file, index=False)
print(f"✅ Saved {len(df_extracted):,} rows, {len(df_extracted.columns)} columns to:")
print(f"   {output_file}")

# ============================================
# CREATE SPECIALIZED DATASETS
# ============================================

# 1. Menstrual cycle dataset
cycle_cols = [c for c in df_extracted.columns if any(x in c.lower() for x in ['cycle', 'period', 'menstrual', 'lmp'])]
if cycle_cols:
    df_cycle = df_extracted[cycle_cols].copy()
    cycle_file = OUTPUT_DIR / "mc_baseline_cycle_data.csv"
    df_cycle.to_csv(cycle_file, index=False)
    print(f"✅ Saved menstrual cycle dataset: {cycle_file}")

# 2. Menstrual myths dataset (for educational module)
myth_cols = [c for c in df_extracted.columns if 'myth' in c.lower() or 'attitude' in c.lower()]
if myth_cols:
    df_myths = df_extracted[myth_cols].copy()
    myths_file = OUTPUT_DIR / "mc_baseline_menstrual_myths.csv"
    df_myths.to_csv(myths_file, index=False)
    print(f"✅ Saved menstrual myths dataset: {myths_file}")

# 3. Symptoms dataset (for side effect navigator)
symptom_cols = [c for c in df_extracted.columns if 'symptom' in c.lower()]
if symptom_cols:
    df_symptoms = df_extracted[symptom_cols].copy()
    symptoms_file = OUTPUT_DIR / "mc_baseline_symptoms.csv"
    df_symptoms.to_csv(symptoms_file, index=False)
    print(f"✅ Saved symptoms dataset: {symptoms_file}")

# ============================================
# CALCULATE KEY STATISTICS FOR PITCH
# ============================================

print("\n" + "=" * 70)
print("📊 KEY STATISTICS FOR YOUR PITCH")
print("=" * 70)

print(f"\n📌 Total records: {len(df_extracted):,}")

if 'age' in df_extracted.columns:
    print(f"\n📌 Age distribution:")
    print(f"   - Mean age: {df_extracted['age'].mean():.1f}")
    print(f"   - Min age: {df_extracted['age'].min():.0f}")
    print(f"   - Max age: {df_extracted['age'].max():.0f}")

if 'cycle_pattern' in df_extracted.columns:
    print(f"\n📌 Cycle pattern distribution:")
    pattern_counts = df_extracted['cycle_pattern'].value_counts()
    for pattern, count in pattern_counts.head(5).items():
        print(f"   - {pattern}: {count} ({count/len(df_extracted)*100:.1f}%)")

if 'cycle_length_days' in df_extracted.columns:
    print(f"\n📌 Cycle length:")
    print(f"   - Mean: {df_extracted['cycle_length_days'].mean():.1f} days")
    print(f"   - Min: {df_extracted['cycle_length_days'].min():.0f} days")
    print(f"   - Max: {df_extracted['cycle_length_days'].max():.0f} days")

# Calculate common symptoms prevalence
symptom_cols_list = [c for c in df_extracted.columns if 'symptom_' in c and '_severity' not in c]
if symptom_cols_list:
    print(f"\n📌 Common menstrual symptoms (% experiencing):")
    for col in symptom_cols_list[:5]:
        symptom_name = col.replace('symptom_', '')
        count = df_extracted[col].notna().sum()
        pct = (count / len(df_extracted)) * 100
        print(f"   - {symptom_name}: {pct:.1f}%")

# Menstrual myths prevalence
myth_cols_list = [c for c in df_extracted.columns if 'menstrual_myth' in c]
if myth_cols_list:
    print(f"\n📌 Menstrual myth prevalence (% who responded):")
    for col in myth_cols_list[:5]:
        myth_name = col.replace('menstrual_myth_', '').replace('_', ' ')
        count = df_extracted[col].notna().sum()
        pct = (count / len(df_extracted)) * 100
        print(f"   - {myth_name}: {pct:.1f}%")

# ============================================
# SAVE SUMMARY REPORT
# ============================================

summary_file = OUTPUT_DIR / "mc_baseline_summary.txt"
with open(summary_file, 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("DATASET 4: MC Baseline - MENSTRUAL CYCLE SUMMARY\n")
    f.write("=" * 70 + "\n\n")
    
    f.write(f"Total records: {len(df_extracted):,}\n")
    f.write(f"Total columns extracted: {len(df_extracted.columns)}\n\n")
    
    if 'age' in df_extracted.columns:
        f.write(f"Age range: {df_extracted['age'].min():.0f} - {df_extracted['age'].max():.0f}\n")
        f.write(f"Mean age: {df_extracted['age'].mean():.1f}\n\n")
    
    if 'cycle_pattern' in df_extracted.columns:
        f.write("Cycle pattern distribution:\n")
        for pattern, count in df_extracted['cycle_pattern'].value_counts().items():
            f.write(f"  {pattern}: {count} ({count/len(df_extracted)*100:.1f}%)\n")
        f.write("\n")
    
    if 'cycle_length_days' in df_extracted.columns:
        f.write(f"Cycle length (days):\n")
        f.write(f"  Mean: {df_extracted['cycle_length_days'].mean():.1f}\n")
        f.write(f"  Range: {df_extracted['cycle_length_days'].min():.0f} - {df_extracted['cycle_length_days'].max():.0f}\n")

print(f"\n✅ Saved summary report to: {summary_file}")

print("\n" + "=" * 70)
print("✅ EXTRACTION COMPLETE!")
print("=" * 70)

print("\n📁 Output files created in: data/processed/")
print("   1. mc_baseline_extracted.csv - All variables")
print("   2. mc_baseline_cycle_data.csv - Cycle regularity and length")
print("   3. mc_baseline_menstrual_myths.csv - Menstrual myths for education")
print("   4. mc_baseline_symptoms.csv - Menstrual symptoms data")
print("   5. mc_baseline_summary.txt - Statistics for pitch")