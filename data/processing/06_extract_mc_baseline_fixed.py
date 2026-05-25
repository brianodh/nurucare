"""
Dataset 4: MC Baseline - CORRECTED EXTRACTION
Based on actual column names from the file

This dataset powers the menstrual cycle personalization and side effect navigator!
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================

INPUT_FILE = r"C:\Users\brian\Downloads\MC_Baseline_final_ANON.csv"

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("DATASET 4: MC Baseline - MENSTRUAL CYCLE DATA EXTRACTION (CORRECTED)")
print("=" * 70)
print("🩸 This dataset contains menstrual cycle data for personalization!")

# ============================================
# LOAD DATASET
# ============================================

print("\n📂 Loading dataset...")
df = pd.read_csv(INPUT_FILE, encoding='latin1', low_memory=False)
print(f"✅ Loaded: {len(df):,} rows, {len(df.columns)} columns")

# ============================================
# EXTRACT ALL VARIABLES
# ============================================

print("\n📊 Extracting variables...")

extracted = {}

# ----------------------------------------------------------------------
# 1. IDENTIFIERS & DEMOGRAPHICS
# ----------------------------------------------------------------------
extracted['record_id'] = df['id']
extracted['site'] = df['site']
extracted['age'] = df['Age']  # Age is at column 361!
print("   ✅ Extracted age")

# ----------------------------------------------------------------------
# 2. MENSTRUAL CYCLE REGULARITY (CRITICAL!)
# ----------------------------------------------------------------------
if 'q4_4' in df.columns:
    extracted['cycle_pattern'] = df['q4_4']
    print("   ✅ Found cycle pattern (q4_4)")

# ----------------------------------------------------------------------
# 3. CYCLE LENGTH (For personalization)
# ----------------------------------------------------------------------
if 'q4_2' in df.columns:
    extracted['cycle_length_days'] = df['q4_2']
    print("   ✅ Found cycle length (q4_2)")

if 'q4_3' in df.columns:
    extracted['days_between_periods'] = df['q4_3']
    print("   ✅ Found days between periods (q4_3)")

# ----------------------------------------------------------------------
# 4. LAST MENSTRUAL PERIOD (LMP)
# ----------------------------------------------------------------------
if 'q4_5' in df.columns:
    extracted['last_period_start'] = df['q4_5']
    print("   ✅ Found LMP (q4_5)")

if 'q4_6' in df.columns:
    extracted['next_period_expected'] = df['q4_6']
    print("   ✅ Found next period expected (q4_6)")

# ----------------------------------------------------------------------
# 5. MENSTRUAL FLOW & CURRENT STATUS
# ----------------------------------------------------------------------
if 'q4_8' in df.columns:
    extracted['menstrual_flow_quantity'] = df['q4_8']
    print("   ✅ Found menstrual flow (q4_8)")

if 'q4_7' in df.columns:
    extracted['currently_menstruating'] = df['q4_7']
    print("   ✅ Found current menstruation status (q4_7)")

# ----------------------------------------------------------------------
# 6. MENSTRUAL SYMPTOMS (For side effect navigator)
# ----------------------------------------------------------------------
symptoms = {
    'q4_9a': 'abdominal_pain',
    'q4_9aseverity': 'abdominal_pain_severity',
    'q4_9b': 'back_pain',
    'q4_9bseverity': 'back_pain_severity',
    'q4_9c': 'irregular_periods',
    'q4_9cseverity': 'irregular_periods_severity',
    'q4_9d': 'lack_of_sleep',
    'q4_9dseverity': 'lack_of_sleep_severity',
    'q4_9e': 'lack_of_energy',
    'q4_9eseverity': 'lack_of_energy_severity',
    'q4_9f': 'negative_moods',
    'q4_9fseverity': 'negative_moods_severity',
    'q4_9g': 'other_symptoms',
    'q4_9gseverity': 'other_symptoms_severity',
}

for col, name in symptoms.items():
    if col in df.columns:
        extracted[f'symptom_{name}'] = df[col]

print("   ✅ Extracted menstrual symptoms")

# ----------------------------------------------------------------------
# 7. MENSTRUAL MYTHS (GOLD for educational module!)
# ----------------------------------------------------------------------
menstrual_myths = {
    'q2_1a': 'myth_travel_changes_cycle',
    'q2_1b': 'myth_weight_gain_at_puberty',
    'q2_1c': 'myth_girls_puberty_before_boys',
    'q2_1d': 'myth_periods_every_28_days',
    'q2_1e': 'myth_tampons_age_restriction',
    'q2_1f': 'myth_others_can_tell',
    'q2_1g': 'myth_swimming_dangerous',
    'q2_1h': 'myth_athletes_stop_menstruating',
    'q2_1i': 'myth_periods_clean_dirty_blood',
    'q2_1j': 'myth_cup_of_blood_loss',
    'q2_1k': 'myth_blood_flushes_out_egg',
    'q2_1l': 'myth_blood_comes_from_uterus',
    'q2_1m': 'myth_blood_comes_from_urethra',
    'q2_1n': 'myth_all_get_bad_tempered',
}

for col, name in menstrual_myths.items():
    if col in df.columns:
        extracted[f'menstrual_{name}'] = df[col]

print("   ✅ Extracted menstrual myths")

# ----------------------------------------------------------------------
# 8. MENSTRUAL ATTITUDES (Cultural context)
# ----------------------------------------------------------------------
attitudes = {
    'q2_2a': 'attitude_periods_great_growing_up',
    'q2_2b': 'attitude_periods_proud',
    'q2_2c': 'attitude_sorry_for_young_girls',
    'q2_2d': 'attitude_periods_nuisance',
    'q2_2e': 'attitude_periods_embarrassing',
    'q2_2f': 'attitude_first_period_great_event',
    'q2_2g': 'attitude_keep_quiet_about_periods',
    'q2_2h': 'attitude_periods_uncomfortable',
    'q2_2i': 'attitude_would_rather_stay_girl',
    'q2_2j': 'attitude_periods_make_you_special',
    'q2_2k': 'attitude_periods_exciting_interesting',
}

for col, name in attitudes.items():
    if col in df.columns:
        extracted[f'attitude_{name}'] = df[col]

print("   ✅ Extracted menstrual attitudes")

# ----------------------------------------------------------------------
# 9. SEXUAL & PREGNANCY HISTORY
# ----------------------------------------------------------------------
if 'q3_1' in df.columns:
    extracted['ever_had_sex'] = df['q3_1']
if 'q3_3' in df.columns:
    extracted['age_first_sex'] = df['q3_3']
if 'q3_5' in df.columns:
    extracted['ever_pregnant'] = df['q3_5']
if 'q3_6' in df.columns:
    extracted['number_of_births'] = df['q3_6']

print("   ✅ Extracted sexual history")

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
cycle_cols = ['age', 'cycle_pattern', 'cycle_length_days', 'days_between_periods', 
              'last_period_start', 'next_period_expected', 'menstrual_flow_quantity', 
              'currently_menstruating']
available_cycle = [c for c in cycle_cols if c in df_extracted.columns]
if available_cycle:
    df_cycle = df_extracted[available_cycle].copy()
    cycle_file = OUTPUT_DIR / "mc_baseline_cycle_data.csv"
    df_cycle.to_csv(cycle_file, index=False)
    print(f"✅ Saved menstrual cycle dataset: {cycle_file}")

# 2. Menstrual myths dataset (for educational module)
myth_cols = [c for c in df_extracted.columns if 'myth' in c.lower()]
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

# 4. Attitudes dataset (for cultural context)
attitude_cols = [c for c in df_extracted.columns if 'attitude' in c.lower()]
if attitude_cols:
    df_attitudes = df_extracted[attitude_cols].copy()
    attitudes_file = OUTPUT_DIR / "mc_baseline_attitudes.csv"
    df_attitudes.to_csv(attitudes_file, index=False)
    print(f"✅ Saved attitudes dataset: {attitudes_file}")

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
symptom_cols_list = [c for c in df_extracted.columns if 'symptom_' in c and 'severity' not in c]
if symptom_cols_list:
    print(f"\n📌 Common menstrual symptoms (% experiencing):")
    for col in symptom_cols_list[:5]:
        symptom_name = col.replace('symptom_', '').replace('_', ' ')
        count = df_extracted[col].notna().sum()
        pct = (count / len(df_extracted)) * 100
        print(f"   - {symptom_name}: {pct:.1f}%")

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
print("   5. mc_baseline_attitudes.csv - Menstrual attitudes for cultural context")
print("   6. mc_baseline_summary.txt - Statistics for pitch")