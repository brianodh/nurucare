"""
Dataset 2: Client Service Statistics - Variable Extraction
Extracts variables for: Method adoption, fertility intentions, counseling impact

This dataset has 216,539 REAL family planning service records
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURATION - UPDATE THIS PATH
# ============================================

# TODO: Change this to where YOUR file is located
INPUT_FILE = r"C:\Users\brian\Downloads\Client_Service_Statistics.csv"

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("DATASET 2: Client Service Statistics - COMPLETE EXTRACTION")
print("=" * 70)

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
    exit(1)

# ============================================
# SEE WHAT COLUMNS WE HAVE
# ============================================

print("\n📋 Columns in this dataset:")
for i, col in enumerate(df.columns):
    print(f"   {i+1:2d}. {col}")

# ============================================
# MAP VARIABLES (Based on documentation)
# ============================================

print("\n📊 Extracting variables...")

extracted = {}

# ----------------------------------------------------------------------
# 1. IDENTIFIERS & DEMOGRAPHICS
# ----------------------------------------------------------------------
if 'visitid' in df.columns:
    extracted['visit_id'] = df['visitid']
if 'uniqueid' in df.columns:
    extracted['unique_id'] = df['uniqueid']
if 'county' in df.columns:
    extracted['county'] = df['county']
if 'division' in df.columns:
    extracted['division'] = df['division']
if 'facilityname' in df.columns:
    extracted['facility_name'] = df['facilityname']
if 'organization' in df.columns:
    extracted['organization'] = df['organization']
if 'year' in df.columns:
    extracted['year'] = df['year']
if 'month' in df.columns:
    extracted['month'] = df['month']

# ----------------------------------------------------------------------
# 2. CLIENT DEMOGRAPHICS
# ----------------------------------------------------------------------
if 'gender' in df.columns:
    extracted['gender'] = df['gender']
if 'age' in df.columns:
    extracted['age'] = df['age']
elif 'client_age' in df.columns:
    extracted['age'] = df['client_age']
elif 'client_age2' in df.columns:
    extracted['age'] = df['client_age2']

if 'educationlevel' in df.columns:
    extracted['education_level'] = df['educationlevel']

if 'noofchildren' in df.columns:
    extracted['number_of_children'] = df['noofchildren']
elif 'no_children' in df.columns:
    extracted['number_of_children'] = df['no_children']

# ----------------------------------------------------------------------
# 3. FERTILITY INTENTIONS (CRITICAL for personalization)
# ----------------------------------------------------------------------
if 'fertilityintention' in df.columns:
    extracted['fertility_intention'] = df['fertilityintention']
    print("   ✅ Found fertility intention variable")

# ----------------------------------------------------------------------
# 4. FP STATUS (Current user, new user, etc.)
# ----------------------------------------------------------------------
if 'fpstatus' in df.columns:
    extracted['fp_status'] = df['fpstatus']
    print("   ✅ Found FP status variable")
if 'projectstatus' in df.columns:
    extracted['project_status'] = df['projectstatus']
if 'projectfpstatus' in df.columns:
    extracted['project_fp_status'] = df['projectfpstatus']

# ----------------------------------------------------------------------
# 5. PREVIOUS METHOD (For understanding switching patterns)
# ----------------------------------------------------------------------
if 'previousmethod' in df.columns:
    extracted['previous_method'] = df['previousmethod']
    print("   ✅ Found previous method variable")
if 'prev_fp' in df.columns:
    extracted['previous_method_recoded'] = df['prev_fp']

# ----------------------------------------------------------------------
# 6. COUNSELING (Impact metric)
# ----------------------------------------------------------------------
if 'counseled' in df.columns:
    extracted['counseled'] = df['counseled']
    print("   ✅ Found counseling variable")
if 'new_counselled' in df.columns:
    extracted['counseled_recoded'] = df['new_counselled']

# ----------------------------------------------------------------------
# 7. METHOD ADOPTED (The OUTCOME - what your AI would recommend)
# ----------------------------------------------------------------------
if 'methodadopted' in df.columns:
    extracted['method_adopted'] = df['methodadopted']
    print("   ✅ Found method adopted variable")
if 'fp_adopted' in df.columns:
    extracted['method_adopted_recoded'] = df['fp_adopted']

# ----------------------------------------------------------------------
# 8. REFERRALS (Integration with health system)
# ----------------------------------------------------------------------
if 'referred' in df.columns:
    extracted['referred'] = df['referred']
if 'fp_referred' in df.columns:
    extracted['referred_method'] = df['fp_referred']

# ----------------------------------------------------------------------
# 9. LONG-ACTING METHOD ADOPTION
# ----------------------------------------------------------------------
if 'lapm' in df.columns:
    extracted['adopted_long_acting'] = df['lapm']

# ----------------------------------------------------------------------
# 10. QUANTITIES (For understanding usage patterns)
# ----------------------------------------------------------------------
if 'pillquantity' in df.columns:
    extracted['pill_quantity'] = df['pillquantity']
if 'condomquantity' in df.columns:
    extracted['condom_quantity'] = df['condomquantity']

# ----------------------------------------------------------------------
# 11. DELIVERY CHANNEL (How clients access services)
# ----------------------------------------------------------------------
if 'delivery' in df.columns:
    extracted['delivery_channel'] = df['delivery']
if 'delivery_channel' in df.columns:
    extracted['delivery_channel_recoded'] = df['delivery_channel']

print("   ✅ Extracted all available variables")

# ============================================
# CREATE DATAFRAME
# ============================================

print("\n💾 Creating dataset...")

df_extracted = pd.DataFrame(extracted)

# Save main extracted file
output_file = OUTPUT_DIR / "client_service_extracted.csv"
df_extracted.to_csv(output_file, index=False)
print(f"✅ Saved {len(df_extracted):,} rows, {len(df_extracted.columns)} columns to:")
print(f"   {output_file}")

# ============================================
# CREATE SPECIALIZED DATASETS
# ============================================

# 1. Method adoption patterns
method_cols = ['method_adopted', 'method_adopted_recoded', 'previous_method', 
               'previous_method_recoded', 'fp_status', 'age', 'gender']
available_method_cols = [c for c in method_cols if c in df_extracted.columns]
if available_method_cols:
    df_methods = df_extracted[available_method_cols].copy()
    methods_file = OUTPUT_DIR / "client_service_method_adoption.csv"
    df_methods.to_csv(methods_file, index=False)
    print(f"✅ Saved method adoption dataset: {methods_file}")

# 2. Fertility intentions
fert_cols = ['fertility_intention', 'age', 'number_of_children', 'fp_status']
available_fert_cols = [c for c in fert_cols if c in df_extracted.columns]
if available_fert_cols:
    df_fert = df_extracted[available_fert_cols].copy()
    fert_file = OUTPUT_DIR / "client_service_fertility.csv"
    df_fert.to_csv(fert_file, index=False)
    print(f"✅ Saved fertility intentions dataset: {fert_file}")

# 3. Counseling impact
counsel_cols = ['counseled', 'counseled_recoded', 'method_adopted', 'referred', 'age']
available_counsel_cols = [c for c in counsel_cols if c in df_extracted.columns]
if available_counsel_cols:
    df_counsel = df_extracted[available_counsel_cols].copy()
    counsel_file = OUTPUT_DIR / "client_service_counseling.csv"
    df_counsel.to_csv(counsel_file, index=False)
    print(f"✅ Saved counseling impact dataset: {counsel_file}")

# 4. Geographic distribution (for pitch map)
geo_cols = ['county', 'division', 'facility_name', 'organization', 'year', 'month']
available_geo_cols = [c for c in geo_cols if c in df_extracted.columns]
if available_geo_cols:
    df_geo = df_extracted[available_geo_cols].copy()
    geo_file = OUTPUT_DIR / "client_service_geography.csv"
    df_geo.to_csv(geo_file, index=False)
    print(f"✅ Saved geographic dataset: {geo_file}")

# ============================================
# CALCULATE KEY STATISTICS FOR PITCH
# ============================================

print("\n" + "=" * 70)
print("📊 KEY STATISTICS FOR YOUR PITCH")
print("=" * 70)

print(f"\n📌 Total service records: {len(df_extracted):,}")

if 'age' in df_extracted.columns:
    print(f"\n📌 Age distribution:")
    print(f"   - Mean age: {df_extracted['age'].mean():.1f}")
    print(f"   - Min age: {df_extracted['age'].min():.0f}")
    print(f"   - Max age: {df_extracted['age'].max():.0f}")

if 'gender' in df_extracted.columns:
    gender_counts = df_extracted['gender'].value_counts()
    print(f"\n📌 Gender distribution:")
    for gender, count in gender_counts.head(5).items():
        print(f"   - {gender}: {count:,} ({count/len(df_extracted)*100:.1f}%)")

if 'fp_status' in df_extracted.columns:
    status_counts = df_extracted['fp_status'].value_counts()
    print(f"\n📌 FP Status distribution:")
    for status, count in status_counts.head(5).items():
        print(f"   - {status}: {count:,} ({count/len(df_extracted)*100:.1f}%)")

if 'fertility_intention' in df_extracted.columns:
    fert_counts = df_extracted['fertility_intention'].value_counts()
    print(f"\n📌 Fertility intentions:")
    for intent, count in fert_counts.head(5).items():
        print(f"   - {intent}: {count:,} ({count/len(df_extracted)*100:.1f}%)")

if 'method_adopted' in df_extracted.columns:
    method_counts = df_extracted['method_adopted'].value_counts()
    print(f"\n📌 Top 5 methods adopted:")
    for method, count in method_counts.head(5).items():
        print(f"   - {method}: {count:,} ({count/len(df_extracted)*100:.1f}%)")

if 'counseled' in df_extracted.columns:
    counseled_count = df_extracted['counseled'].notna().sum()
    counseled_pct = (counseled_count / len(df_extracted)) * 100
    print(f"\n📌 Counseling coverage:")
    print(f"   - Clients counseled: {counseled_count:,} ({counseled_pct:.1f}%)")

if 'referred' in df_extracted.columns:
    referred_count = df_extracted['referred'].notna().sum()
    referred_pct = (referred_count / len(df_extracted)) * 100
    print(f"\n📌 Referrals needed:")
    print(f"   - Clients requiring referral: {referred_count:,} ({referred_pct:.1f}%)")

if 'adopted_long_acting' in df_extracted.columns:
    lapm_count = df_extracted['adopted_long_acting'].sum() if df_extracted['adopted_long_acting'].dtype in ['int64', 'float64'] else df_extracted['adopted_long_acting'].notna().sum()
    lapm_pct = (lapm_count / len(df_extracted)) * 100
    print(f"\n📌 Long-acting method adoption:")
    print(f"   - LAPM adopters: {lapm_count:,} ({lapm_pct:.1f}%)")

# ============================================
# SAVE SUMMARY REPORT
# ============================================

summary_file = OUTPUT_DIR / "client_service_summary.txt"
with open(summary_file, 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("DATASET 2: Client Service Statistics - SUMMARY\n")
    f.write("=" * 70 + "\n\n")
    
    f.write(f"Total records: {len(df_extracted):,}\n")
    f.write(f"Total columns extracted: {len(df_extracted.columns)}\n\n")
    
    if 'age' in df_extracted.columns:
        f.write(f"Age range: {df_extracted['age'].min():.0f} - {df_extracted['age'].max():.0f}\n")
        f.write(f"Mean age: {df_extracted['age'].mean():.1f}\n\n")
    
    if 'fp_status' in df_extracted.columns:
        f.write("FP Status distribution:\n")
        for status, count in df_extracted['fp_status'].value_counts().head(10).items():
            f.write(f"  {status}: {count:,} ({count/len(df_extracted)*100:.1f}%)\n")
        f.write("\n")
    
    if 'method_adopted' in df_extracted.columns:
        f.write("Top 10 methods adopted:\n")
        for method, count in df_extracted['method_adopted'].value_counts().head(10).items():
            f.write(f"  {method}: {count:,} ({count/len(df_extracted)*100:.1f}%)\n")

print(f"\n✅ Saved summary report to: {summary_file}")

print("\n" + "=" * 70)
print("✅ EXTRACTION COMPLETE!")
print("=" * 70)

print("\n📁 Output files created in: data/processed/")
print("   1. client_service_extracted.csv - All extracted variables")
print("   2. client_service_method_adoption.csv - Method adoption patterns")
print("   3. client_service_fertility.csv - Fertility intentions")
print("   4. client_service_counseling.csv - Counseling impact data")
print("   5. client_service_geography.csv - Geographic distribution")
print("   6. client_service_summary.txt - Statistics for pitch")