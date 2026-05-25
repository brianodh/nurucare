"""
Dataset 3: Prospective Morbidity Survey - CORRECTED EXTRACTION
Based on actual column names from the file

This dataset has ACTUAL BP READINGS for WHO MEC safety rules!
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================

INPUT_FILE = r"C:\Users\brian\Downloads\ddi_pds_data.csv"

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("DATASET 3: Prospective Morbidity Survey - CORRECTED EXTRACTION")
print("=" * 70)
print("🔬 This dataset contains ACTUAL BLOOD PRESSURE READINGS for WHO MEC rules!")

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
extracted['record_id'] = df['clientid']
extracted['province'] = df['province']
extracted['county'] = df['county']
extracted['district'] = df['district']
extracted['facility_type'] = df['type']

# Age (CRITICAL for WHO MEC)
extracted['age'] = df['pds101']
print("   ✅ Extracted age (pds101)")

# Residence, marital status, education, religion, occupation
extracted['residence'] = df['pds102']
extracted['marital_status'] = df['pds103']
extracted['education'] = df['pds104']
extracted['religion'] = df['pds105']
extracted['occupation'] = df['pds106']

print("   ✅ Extracted demographics")

# ----------------------------------------------------------------------
# 2. BLOOD PRESSURE (GOLD for WHO MEC!)
# ----------------------------------------------------------------------
extracted['systolic_bp'] = df['pds315s']
extracted['diastolic_bp'] = df['pds315d']
extracted['bp_reading'] = df['pds315_blodpressure']

print("   ✅✅ Extracted BLOOD PRESSURE (pds315s/pds315d)")

# Calculate hypertension flag
extracted['has_hypertension'] = ((df['pds315s'] >= 140) | (df['pds315d'] >= 90)).astype(int)

# ----------------------------------------------------------------------
# 3. PREGNANCY HISTORY
# ----------------------------------------------------------------------
extracted['total_pregnancies'] = df['pds201']
extracted['live_births'] = df['pds202']
extracted['living_children'] = df['pds203']
extracted['miscarriages'] = df['pds204']
extracted['induced_abortions'] = df['pds205']

print("   ✅ Extracted pregnancy history")

# ----------------------------------------------------------------------
# 4. CONTRACEPTIVE USE BEFORE PREGNANCY
# ----------------------------------------------------------------------
extracted['used_contraception_before'] = df['pds206']

# Method used (various)
if 'pds207a' in df.columns:
    extracted['contraceptive_pills'] = df['pds207a']
if 'pds207b' in df.columns:
    extracted['contraceptive_injectables'] = df['pds207b']
if 'pds207c' in df.columns:
    extracted['contraceptive_implants'] = df['pds207c']
if 'pds207d' in df.columns:
    extracted['contraceptive_female_sterilization'] = df['pds207d']
if 'pds207f' in df.columns:
    extracted['contraceptive_iud'] = df['pds207f']
if 'pds207g' in df.columns:
    extracted['contraceptive_male_condom'] = df['pds207g']
if 'pds207k' in df.columns:
    extracted['contraceptive_rhythm'] = df['pds207k']
if 'pds207l' in df.columns:
    extracted['contraceptive_withdrawal'] = df['pds207l']
if 'pds207m' in df.columns:
    extracted['contraceptive_emergency'] = df['pds207m']

print("   ✅ Extracted contraceptive history")

# ----------------------------------------------------------------------
# 5. FERTILITY INTENTIONS (CRITICAL for personalization)
# ----------------------------------------------------------------------
extracted['fertility_intention'] = df['pds208']
print("   ✅ Extracted fertility intentions (pds208)")

# ----------------------------------------------------------------------
# 6. GESTATIONAL AGE
# ----------------------------------------------------------------------
if 'pds302' in df.columns:
    extracted['gestational_age_weeks'] = df['pds302']

# ----------------------------------------------------------------------
# 7. FP COUNSELING & DISCHARGE
# ----------------------------------------------------------------------
extracted['counseled_on_fp'] = df['pds701']
extracted['given_fp_method'] = df['pds702']

# ----------------------------------------------------------------------
# 8. REASON FOR CARE & DIAGNOSIS
# ----------------------------------------------------------------------
extracted['reason_for_care'] = df['pds301']
extracted['diagnosis'] = df['pds401']

print("   ✅ Extracted clinical data")

# ============================================
# CREATE DATAFRAME
# ============================================

print("\n💾 Creating dataset...")

df_extracted = pd.DataFrame(extracted)

# Save main extracted file
output_file = OUTPUT_DIR / "prospective_morbidity_extracted.csv"
df_extracted.to_csv(output_file, index=False)
print(f"✅ Saved {len(df_extracted):,} rows, {len(df_extracted.columns)} columns to:")
print(f"   {output_file}")

# ============================================
# CREATE SPECIALIZED DATASETS
# ============================================

# 1. BP-only dataset (for WHO MEC rule demonstration)
bp_cols = ['age', 'systolic_bp', 'diastolic_bp', 'has_hypertension']
df_bp = df_extracted[bp_cols].copy()
bp_file = OUTPUT_DIR / "prospective_morbidity_blood_pressure.csv"
df_bp.to_csv(bp_file, index=False)
print(f"✅ Saved blood pressure dataset: {bp_file}")

# 2. Fertility intentions dataset
fert_cols = ['age', 'fertility_intention', 'live_births', 'living_children']
df_fert = df_extracted[fert_cols].copy()
fert_file = OUTPUT_DIR / "prospective_morbidity_fertility.csv"
df_fert.to_csv(fert_file, index=False)
print(f"✅ Saved fertility dataset: {fert_file}")

# 3. Clinical dataset for WHO MEC
clinical_cols = ['age', 'systolic_bp', 'diastolic_bp', 'has_hypertension', 
                 'total_pregnancies', 'live_births', 'miscarriages']
df_clinical = df_extracted[clinical_cols].copy()
clinical_file = OUTPUT_DIR / "prospective_morbidity_clinical.csv"
df_clinical.to_csv(clinical_file, index=False)
print(f"✅ Saved clinical dataset: {clinical_file}")

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

if 'systolic_bp' in df_extracted.columns:
    print(f"\n📌 Blood Pressure Statistics:")
    print(f"   - Mean systolic: {df_extracted['systolic_bp'].mean():.1f} mmHg")
    print(f"   - Mean diastolic: {df_extracted['diastolic_bp'].mean():.1f} mmHg")
    
    hypertension_count = df_extracted['has_hypertension'].sum()
    hypertension_pct = (hypertension_count / len(df_extracted)) * 100
    print(f"   - Hypertension (≥140/90): {hypertension_count:,} ({hypertension_pct:.1f}%)")

if 'total_pregnancies' in df_extracted.columns:
    print(f"\n📌 Reproductive history:")
    print(f"   - Mean pregnancies: {df_extracted['total_pregnancies'].mean():.1f}")
    print(f"   - Mean live births: {df_extracted['live_births'].mean():.1f}")
    print(f"   - Women with miscarriages: {df_extracted['miscarriages'].gt(0).sum():,}")

if 'fertility_intention' in df_extracted.columns:
    print(f"\n📌 Fertility intentions:")
    intent_counts = df_extracted['fertility_intention'].value_counts()
    for intent, count in intent_counts.head(5).items():
        print(f"   - {intent[:40]}: {count:,} ({count/len(df_extracted)*100:.1f}%)")

if 'counseled_on_fp' in df_extracted.columns:
    counseled_count = df_extracted['counseled_on_fp'].notna().sum()
    counseled_pct = (counseled_count / len(df_extracted)) * 100
    print(f"\n📌 FP Counseling at discharge:")
    print(f"   - Counseled: {counseled_count:,} ({counseled_pct:.1f}%)")

# ============================================
# WHO MEC RULE DEMONSTRATION
# ============================================

print("\n" + "=" * 70)
print("🏥 WHO MEC RULE DEMONSTRATION")
print("=" * 70)

if 'age' in df_extracted.columns and 'systolic_bp' in df_extracted.columns:
    # Women who would be restricted from combined pills
    # Rule: Age >35 OR Hypertension
    high_risk = ((df_extracted['age'] > 35) | (df_extracted['has_hypertension'] == 1))
    high_risk_count = high_risk.sum()
    high_risk_pct = (high_risk_count / len(df_extracted)) * 100
    
    print(f"\n   🔬 Women needing combined pill restriction (WHO MEC Category 3-4):")
    print(f"      - {high_risk_count:,} ({high_risk_pct:.1f}%) would be restricted from combined pills")
    print(f"      - These women need progestin-only or non-hormonal methods")
    
    # Women with hypertension only
    hyp_only = df_extracted['has_hypertension'].sum()
    print(f"\n   🔬 Women with hypertension (≥140/90):")
    print(f"      - {hyp_only:,} ({hyp_only/len(df_extracted)*100:.1f}%)")
    
    # Women over 35
    over35 = (df_extracted['age'] > 35).sum()
    print(f"\n   🔬 Women over 35:")
    print(f"      - {over35:,} ({over35/len(df_extracted)*100:.1f}%)")

print("\n" + "=" * 70)
print("✅ EXTRACTION COMPLETE!")
print("=" * 70)

print("\n📁 Output files created in: data/processed/")
print("   1. prospective_morbidity_extracted.csv - All variables")
print("   2. prospective_morbidity_blood_pressure.csv - BP data for WHO MEC")
print("   3. prospective_morbidity_fertility.csv - Fertility intentions")
print("   4. prospective_morbidity_clinical.csv - Clinical summary")