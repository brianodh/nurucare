"""
Dataset 3: Prospective Morbidity Survey - Variable Extraction
Extracts variables for: Blood pressure (WHO MEC), pregnancy history, clinical data

This dataset has ACTUAL BP READINGS for WHO MEC safety rules!
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURATION - UPDATE THIS PATH
# ============================================

# TODO: Change this to where YOUR file is located
INPUT_FILE = r"C:\Users\brian\Downloads\ddi_pds_data.csv"

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("DATASET 3: Prospective Morbidity Survey - COMPLETE EXTRACTION")
print("=" * 70)
print("🔬 This dataset contains ACTUAL BLOOD PRESSURE READINGS for WHO MEC rules!")

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
# LOOK FOR BP COLUMNS (CRITICAL!)
# ============================================

print("\n🔍 Searching for blood pressure columns...")

bp_sys_col = None
bp_dia_col = None

for col in df.columns:
    col_lower = col.lower()
    if 'sys' in col_lower and ('bp' in col_lower or 'blood' in col_lower):
        bp_sys_col = col
        print(f"   ✅ Found systolic BP column: {col}")
    if 'dia' in col_lower and ('bp' in col_lower or 'blood' in col_lower):
        bp_dia_col = col
        print(f"   ✅ Found diastolic BP column: {col}")
    if 'v315' in col_lower:
        if 's' in col_lower or 'sys' in col_lower:
            bp_sys_col = col
            print(f"   ✅ Found systolic BP column: {col}")
        elif 'd' in col_lower or 'dia' in col_lower:
            bp_dia_col = col
            print(f"   ✅ Found diastolic BP column: {col}")

# ============================================
# MAP VARIABLES
# ============================================

print("\n📊 Extracting variables...")

extracted = {}

# ----------------------------------------------------------------------
# 1. IDENTIFIERS & GEOGRAPHY
# ----------------------------------------------------------------------
if 'vq01' in df.columns:
    extracted['record_id'] = df['vq01']
if 'vq04' in df.columns:
    extracted['county'] = df['vq04']
if 'vq05' in df.columns:
    extracted['district'] = df['vq05']

# ----------------------------------------------------------------------
# 2. DEMOGRAPHICS
# ----------------------------------------------------------------------
if 'v101' in df.columns:
    extracted['age'] = df['v101']
    print("   ✅ Found age (v101)")
elif 'age' in df.columns:
    extracted['age'] = df['age']

if 'v104' in df.columns:
    extracted['education'] = df['v104']
if 'v103' in df.columns:
    extracted['marital_status'] = df['v103']
if 'v105' in df.columns:
    extracted['religion'] = df['v105']
if 'v106' in df.columns:
    extracted['occupation'] = df['v106']

# ----------------------------------------------------------------------
# 3. BLOOD PRESSURE (CRITICAL for WHO MEC!)
# ----------------------------------------------------------------------
if bp_sys_col:
    extracted['systolic_bp'] = df[bp_sys_col]
    print(f"   ✅ Extracted systolic BP: {bp_sys_col}")
else:
    # Try common column names
    for col in ['v315s', 'systolic_bp', 'systolic', 'bp_systolic', 'sbp']:
        if col in df.columns:
            extracted['systolic_bp'] = df[col]
            print(f"   ✅ Found systolic BP: {col}")
            break

if bp_dia_col:
    extracted['diastolic_bp'] = df[bp_dia_col]
    print(f"   ✅ Extracted diastolic BP: {bp_dia_col}")
else:
    # Try common column names
    for col in ['v315d', 'diastolic_bp', 'diastolic', 'bp_diastolic', 'dbp']:
        if col in df.columns:
            extracted['diastolic_bp'] = df[col]
            print(f"   ✅ Found diastolic BP: {col}")
            break

# Clinical vitals
if 'v313' in df.columns:
    extracted['temperature'] = df['v313']
if 'v314' in df.columns:
    extracted['pulse_rate'] = df['v314']

# ----------------------------------------------------------------------
# 4. PREGNANCY HISTORY
# ----------------------------------------------------------------------
if 'v201' in df.columns:
    extracted['total_pregnancies'] = df['v201']
if 'v202' in df.columns:
    extracted['live_births'] = df['v202']
if 'v203' in df.columns:
    extracted['living_children'] = df['v203']
if 'v204' in df.columns:
    extracted['miscarriages'] = df['v204']
if 'v205' in df.columns:
    extracted['induced_abortions'] = df['v205']
if 'v206' in df.columns:
    extracted['using_contraception_before_pregnancy'] = df['v206']
if 'v302' in df.columns:
    extracted['gestational_age_weeks'] = df['v302']

print("   ✅ Extracted pregnancy history")

# ----------------------------------------------------------------------
# 5. CONTRACEPTIVE USE BEFORE PREGNANCY
# ----------------------------------------------------------------------
contra_methods = {
    'v207a': 'contraceptive_pills',
    'v207b': 'contraceptive_injectables',
    'v207c': 'contraceptive_implants',
    'v207d': 'contraceptive_female_sterilization',
    'v207f': 'contraceptive_iud',
    'v207g': 'contraceptive_male_condom',
    'v207h': 'contraceptive_female_condom',
    'v207k': 'contraceptive_rhythm',
    'v207l': 'contraceptive_lam',
    'v207m': 'contraceptive_withdrawal',
    'v207n': 'contraceptive_emergency',
}

for col, name in contra_methods.items():
    if col in df.columns:
        extracted[name] = df[col]

print("   ✅ Extracted contraceptive history")

# ----------------------------------------------------------------------
# 6. FERTILITY INTENTIONS
# ----------------------------------------------------------------------
if 'v208' in df.columns:
    extracted['wanted_pregnancy'] = df['v208']
    print("   ✅ Found fertility intentions (v208)")

# ----------------------------------------------------------------------
# 7. FP COUNSELING & DISCHARGE
# ----------------------------------------------------------------------
if 'v701' in df.columns:
    extracted['counseled_on_fp'] = df['v701']
if 'v702' in df.columns:
    extracted['given_fp_method'] = df['v702']

# ----------------------------------------------------------------------
# 8. ADMISSION/DIAGNOSIS
# ----------------------------------------------------------------------
if 'v301' in df.columns:
    extracted['reason_for_care'] = df['v301']
if 'v401' in df.columns:
    extracted['diagnosis'] = df['v401']

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
bp_cols = [c for c in df_extracted.columns if any(x in c.lower() for x in ['bp', 'systolic', 'diastolic', 'age'])]
if bp_cols:
    df_bp = df_extracted[bp_cols].copy()
    bp_file = OUTPUT_DIR / "prospective_morbidity_blood_pressure.csv"
    df_bp.to_csv(bp_file, index=False)
    print(f"✅ Saved blood pressure dataset: {bp_file}")

# 2. Clinical dataset (for WHO MEC rules)
clinical_cols = ['age', 'systolic_bp', 'diastolic_bp', 'temperature', 'pulse_rate']
available_clinical = [c for c in clinical_cols if c in df_extracted.columns]
if available_clinical:
    df_clinical = df_extracted[available_clinical].copy()
    clinical_file = OUTPUT_DIR / "prospective_morbidity_clinical.csv"
    df_clinical.to_csv(clinical_file, index=False)
    print(f"✅ Saved clinical dataset: {clinical_file}")

# 3. Pregnancy history dataset
preg_cols = ['total_pregnancies', 'live_births', 'living_children', 'miscarriages', 
             'induced_abortions', 'gestational_age_weeks', 'wanted_pregnancy']
available_preg = [c for c in preg_cols if c in df_extracted.columns]
if available_preg:
    df_preg = df_extracted[available_preg].copy()
    preg_file = OUTPUT_DIR / "prospective_morbidity_pregnancy.csv"
    df_preg.to_csv(preg_file, index=False)
    print(f"✅ Saved pregnancy history dataset: {preg_file}")

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

if 'systolic_bp' in df_extracted.columns and 'diastolic_bp' in df_extracted.columns:
    # Calculate hypertension prevalence
    systolic_valid = df_extracted['systolic_bp'].dropna()
    diastolic_valid = df_extracted['diastolic_bp'].dropna()
    
    if len(systolic_valid) > 0 and len(diastolic_valid) > 0:
        hypertension = ((df_extracted['systolic_bp'] >= 140) | (df_extracted['diastolic_bp'] >= 90)).sum()
        hypertension_pct = (hypertension / len(df_extracted)) * 100
        
        print(f"\n📌 Blood Pressure Statistics:")
        print(f"   - Mean systolic: {df_extracted['systolic_bp'].mean():.1f} mmHg")
        print(f"   - Mean diastolic: {df_extracted['diastolic_bp'].mean():.1f} mmHg")
        print(f"   - Hypertension prevalence (≥140/90): {hypertension:,} ({hypertension_pct:.1f}%)")

if 'total_pregnancies' in df_extracted.columns:
    print(f"\n📌 Reproductive history:")
    print(f"   - Mean pregnancies: {df_extracted['total_pregnancies'].mean():.1f}")
    print(f"   - Women with prior miscarriages: {df_extracted['miscarriages'].notna().sum():,}" if 'miscarriages' in df_extracted.columns else "")

if 'counseled_on_fp' in df_extracted.columns:
    counseled_count = df_extracted['counseled_on_fp'].notna().sum()
    counseled_pct = (counseled_count / len(df_extracted)) * 100
    print(f"\n📌 FP Counseling at discharge:")
    print(f"   - Counseled: {counseled_count:,} ({counseled_pct:.1f}%)")

if 'given_fp_method' in df_extracted.columns:
    given_count = df_extracted['given_fp_method'].notna().sum()
    given_pct = (given_count / len(df_extracted)) * 100
    print(f"\n📌 FP method provided at discharge:")
    print(f"   - Received method: {given_count:,} ({given_pct:.1f}%)")

# ============================================
# SAVE SUMMARY REPORT
# ============================================

summary_file = OUTPUT_DIR / "prospective_morbidity_summary.txt"
with open(summary_file, 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("DATASET 3: Prospective Morbidity Survey - SUMMARY\n")
    f.write("=" * 70 + "\n\n")
    
    f.write(f"Total records: {len(df_extracted):,}\n")
    f.write(f"Total columns extracted: {len(df_extracted.columns)}\n\n")
    
    if 'age' in df_extracted.columns:
        f.write(f"Age range: {df_extracted['age'].min():.0f} - {df_extracted['age'].max():.0f}\n")
        f.write(f"Mean age: {df_extracted['age'].mean():.1f}\n\n")
    
    if 'systolic_bp' in df_extracted.columns:
        f.write(f"Mean systolic BP: {df_extracted['systolic_bp'].mean():.1f} mmHg\n")
        f.write(f"Mean diastolic BP: {df_extracted['diastolic_bp'].mean():.1f} mmHg\n\n")
    
    if 'total_pregnancies' in df_extracted.columns:
        f.write(f"Mean total pregnancies: {df_extracted['total_pregnancies'].mean():.1f}\n")
        f.write(f"Mean live births: {df_extracted['live_births'].mean():.1f}\n\n")

print(f"\n✅ Saved summary report to: {summary_file}")

# ============================================
# WHO MEC RULE DEMONSTRATION
# ============================================

print("\n" + "=" * 70)
print("🏥 WHO MEC RULE DEMONSTRATION")
print("=" * 70)
print("\nWith this dataset, you can demonstrate REAL WHO MEC rules:")

if 'age' in df_extracted.columns and 'systolic_bp' in df_extracted.columns:
    # Find candidates for combined pill restriction
    high_risk = ((df_extracted['age'] > 35) | (df_extracted['systolic_bp'] >= 140) | (df_extracted['diastolic_bp'] >= 90))
    high_risk_count = high_risk.sum()
    high_risk_pct = (high_risk_count / len(df_extracted)) * 100
    
    print(f"\n   🔬 Women needing combined pill restriction:")
    print(f"      - {high_risk_count:,} ({high_risk_pct:.1f}%) would be restricted from combined pills")

print("\n" + "=" * 70)
print("✅ EXTRACTION COMPLETE!")
print("=" * 70)

print("\n📁 Output files created in: data/processed/")
print("   1. prospective_morbidity_extracted.csv - All extracted variables")
print("   2. prospective_morbidity_blood_pressure.csv - BP data for WHO MEC")
print("   3. prospective_morbidity_clinical.csv - Clinical vitals")
print("   4. prospective_morbidity_pregnancy.csv - Pregnancy history")
print("   5. prospective_morbidity_summary.txt - Statistics for pitch")