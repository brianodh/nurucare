"""
Dataset 5: Student Dataset - Variable Extraction
Extracts variables for: Adolescent myths, knowledge gaps, contraceptive use, 
preferred information sources, and demographics.

This dataset has 2,484 students - critical for the adolescent perspective!
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================

INPUT_FILE = r"C:\Users\brian\Downloads\Student Dataset.csv"

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("DATASET 5: Student Dataset - EXTRACTION")
print("=" * 70)
print("📚 This dataset contains adolescent perspectives on contraception!")

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
        print("\n📌 Please check: The file should be in C:\\Users\\brian\\Downloads\\")
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
# 1. DEMOGRAPHICS
# ----------------------------------------------------------------------
if 's701' in df.columns:
    extracted['gender'] = df['s701']
    print("   ✅ Found gender (s701)")
elif 'gender' in df.columns:
    extracted['gender'] = df['gender']

if 's702' in df.columns:
    extracted['age'] = df['s702']
    print("   ✅ Found age (s702)")
elif 'age' in df.columns:
    extracted['age'] = df['age']

if 's703' in df.columns:
    extracted['class'] = df['s703']
    print("   ✅ Found class (s703)")

if 's704' in df.columns:
    extracted['religion'] = df['s704']
    print("   ✅ Found religion (s704)")

# ----------------------------------------------------------------------
# 2. CONTRACEPTIVE KNOWLEDGE (What methods have they heard of?)
# ----------------------------------------------------------------------
contra_knowledge = {
    's504a': 'heard_of_pill',
    's504b': 'heard_of_condoms',
    's504c': 'heard_of_injectables',
    's504d': 'heard_of_iud',
    's504e': 'heard_of_implants',
    's504f': 'heard_of_emergency_pill',
    's504g': 'heard_of_female_sterilization',
    's504h': 'heard_of_male_sterilization',
    's504i': 'heard_of_withdrawal',
    's504j': 'heard_of_rhythm',
}

for col, name in contra_knowledge.items():
    if col in df.columns:
        extracted[name] = df[col]

print("   ✅ Extracted contraceptive knowledge")

# ----------------------------------------------------------------------
# 3. CONTRACEPTIVE USE AT LAST SEX
# ----------------------------------------------------------------------
if 's809a' in df.columns:
    extracted['last_sex_condom'] = df['s809a']
if 's809b' in df.columns:
    extracted['last_sex_pill'] = df['s809b']
if 's809c' in df.columns:
    extracted['last_sex_implant'] = df['s809c']
if 's809d' in df.columns:
    extracted['last_sex_iud'] = df['s809d']
if 's809e' in df.columns:
    extracted['last_sex_injectable'] = df['s809e']
if 's809f' in df.columns:
    extracted['last_sex_emergency'] = df['s809f']
if 's809g' in df.columns:
    extracted['last_sex_withdrawal'] = df['s809g']
if 's809h' in df.columns:
    extracted['last_sex_rhythm'] = df['s809h']
if 's809j' in df.columns:
    extracted['last_sex_no_method'] = df['s809j']

print("   ✅ Extracted last sex contraceptive use")

# ----------------------------------------------------------------------
# 4. WHY NOT USING CONTRACEPTION (Barriers)
# ----------------------------------------------------------------------
if 's8010' in df.columns:
    extracted['reason_not_using'] = df['s8010']
    print("   ✅ Found reason for not using (s8010)")

# ----------------------------------------------------------------------
# 5. ACCESS TO CONTRACEPTIVES
# ----------------------------------------------------------------------
if 's505' in df.columns:
    extracted['knows_fp_source'] = df['s505']
    print("   ✅ Found FP access knowledge (s505)")
if 's506' in df.columns:
    extracted['knows_condom_source'] = df['s506']
    print("   ✅ Found condom access knowledge (s506)")

# ----------------------------------------------------------------------
# 6. SEXUAL ACTIVITY STATUS
# ----------------------------------------------------------------------
if 's804' in df.columns:
    extracted['ever_had_sex'] = df['s804']
    print("   ✅ Found sexual activity status (s804)")

# ----------------------------------------------------------------------
# 7. MYTHS & MISCONCEPTIONS (GOLD for educational module!)
# ----------------------------------------------------------------------
myths = {
    's801b': 'myth_condoms_mean_promiscuous',
    's801c': 'myth_condoms_mean_no_trust',
    's801e': 'myth_contraceptives_encourage_sex',
    's801h': 'myth_acceptable_to_beat_wife',
    's801i': 'myth_sex_only_man_woman',
}

for col, name in myths.items():
    if col in df.columns:
        extracted[f'{name}'] = df[col]
        print(f"   ✅ Found myth: {name}")

# ----------------------------------------------------------------------
# 8. HIV KNOWLEDGE (Health literacy)
# ----------------------------------------------------------------------
hiv_knowledge = {
    's501a': 'hiv_unprotected_sex',
    's501b': 'hiv_shared_needles',
    's501c': 'hiv_mosquito_bites',
    's501d': 'hiv_mother_to_child',
    's501e': 'hiv_shaking_hands',
    's501f': 'hiv_blood_transfusion',
}

for col, name in hiv_knowledge.items():
    if col in df.columns:
        extracted[f'hiv_{name}'] = df[col]

hiv_prevention = {
    's502a': 'prevent_hiv_abstinence',
    's502b': 'prevent_hiv_condoms',
    's502c': 'prevent_hiv_one_partner',
}

for col, name in hiv_prevention.items():
    if col in df.columns:
        extracted[f'{name}'] = df[col]

print("   ✅ Extracted HIV knowledge")

# ----------------------------------------------------------------------
# 9. PREFERRED INFORMATION SOURCES (For product design!)
# ----------------------------------------------------------------------
info_sources = {
    's601ai': 'source_teacher',
    's601an': 'source_health_center',
    's601ar': 'source_internet',
    's601as': 'source_radio_tv',
    's601aa': 'source_father',
    's601ab': 'source_mother',
    's601ag': 'source_friend',
    's601ah': 'source_partner',
}

for col, name in info_sources.items():
    if col in df.columns:
        extracted[f'info_{name}'] = df[col]

print("   ✅ Extracted preferred information sources")

# ----------------------------------------------------------------------
# 10. OPINIONS ON RH EDUCATION
# ----------------------------------------------------------------------
if 's401' in df.columns:
    extracted['should_rh_be_taught'] = df['s401']
    print("   ✅ Found opinion on RH education (s401)")

# ----------------------------------------------------------------------
# 11. PREGNANCY PREVENTION KNOWLEDGE
# ----------------------------------------------------------------------
if 's504a' in df.columns:
    extracted['knows_any_method'] = df[['s504a','s504b','s504c','s504d','s504e','s504f','s504g','s504h','s504i','s504j']].any(axis=1).astype(int)

# ============================================
# CREATE DATAFRAME
# ============================================

print("\n💾 Creating dataset...")

df_extracted = pd.DataFrame(extracted)

# Save main extracted file
output_file = OUTPUT_DIR / "student_dataset_extracted.csv"
df_extracted.to_csv(output_file, index=False)
print(f"✅ Saved {len(df_extracted):,} rows, {len(df_extracted.columns)} columns to:")
print(f"   {output_file}")

# ============================================
# CREATE SPECIALIZED DATASETS
# ============================================

# 1. Myths dataset (for educational module)
myth_cols = [c for c in df_extracted.columns if 'myth_' in c]
if myth_cols:
    # Also include demographics
    demo_cols = [c for c in ['gender', 'age', 'class'] if c in df_extracted.columns]
    cols_to_save = demo_cols + myth_cols
    df_myths = df_extracted[cols_to_save].copy()
    myths_file = OUTPUT_DIR / "student_myths.csv"
    df_myths.to_csv(myths_file, index=False)
    print(f"✅ Saved student myths dataset: {myths_file}")

# 2. Knowledge gaps dataset (for educational prioritization)
knowledge_cols = [c for c in df_extracted.columns if c.startswith('heard_of_') or c.startswith('knows_')]
if knowledge_cols:
    df_knowledge = df_extracted[knowledge_cols].copy()
    knowledge_file = OUTPUT_DIR / "student_knowledge_gaps.csv"
    df_knowledge.to_csv(knowledge_file, index=False)
    print(f"✅ Saved knowledge gaps dataset: {knowledge_file}")

# 3. Information sources dataset (for product design)
source_cols = [c for c in df_extracted.columns if c.startswith('info_')]
if source_cols:
    df_sources = df_extracted[source_cols].copy()
    sources_file = OUTPUT_DIR / "student_info_sources.csv"
    df_sources.to_csv(sources_file, index=False)
    print(f"✅ Saved information sources dataset: {sources_file}")

# 4. Contraceptive use dataset
contra_cols = [c for c in df_extracted.columns if c.startswith('last_sex_') or c == 'reason_not_using' or c == 'ever_had_sex']
if contra_cols:
    df_contra = df_extracted[contra_cols].copy()
    contra_file = OUTPUT_DIR / "student_contraceptive_use.csv"
    df_contra.to_csv(contra_file, index=False)
    print(f"✅ Saved contraceptive use dataset: {contra_file}")

# ============================================
# CALCULATE KEY STATISTICS FOR PITCH
# ============================================

print("\n" + "=" * 70)
print("📊 KEY STATISTICS FOR YOUR PITCH")
print("=" * 70)

print(f"\n📌 Total students: {len(df_extracted):,}")

if 'gender' in df_extracted.columns:
    print(f"\n📌 Gender distribution:")
    gender_counts = df_extracted['gender'].value_counts()
    for gender, count in gender_counts.head(3).items():
        print(f"   - {gender}: {count:,} ({count/len(df_extracted)*100:.1f}%)")

if 'age' in df_extracted.columns:
    # Try to convert age to numeric
    try:
        age_numeric = pd.to_numeric(df_extracted['age'], errors='coerce')
        valid_ages = age_numeric.dropna()
        if len(valid_ages) > 0:
            print(f"\n📌 Age distribution:")
            print(f"   - Mean age: {valid_ages.mean():.1f}")
            print(f"   - Age range: {valid_ages.min():.0f} - {valid_ages.max():.0f}")
    except:
        print(f"\n📌 Age column contains: {df_extracted['age'].iloc[0] if len(df_extracted) > 0 else 'No data'}")

# Myth agreement rates
myth_columns = [c for c in df_extracted.columns if 'myth_' in c]
if myth_columns:
    print(f"\n📌 Student myth agreement rates:")
    for col in myth_columns[:5]:
        count = df_extracted[col].notna().sum()
        pct = (count / len(df_extracted)) * 100
        myth_name = col.replace('myth_', '').replace('_', ' ')
        print(f"   - {myth_name[:35]}: {pct:.1f}% responded")

# Contraceptive knowledge gaps
knowledge_cols = [c for c in df_extracted.columns if c.startswith('heard_of_')]
if knowledge_cols:
    print(f"\n📌 Contraceptive awareness:")
    for col in knowledge_cols[:7]:
        count = df_extracted[col].notna().sum()
        pct = (count / len(df_extracted)) * 100
        method_name = col.replace('heard_of_', '').replace('_', ' ')
        print(f"   - {method_name[:20]}: {pct:.1f}% heard of")

# Preferred information sources
source_cols = [c for c in df_extracted.columns if c.startswith('info_')]
if source_cols:
    print(f"\n📌 Preferred information sources:")
    for col in source_cols[:8]:
        count = df_extracted[col].notna().sum()
        pct = (count / len(df_extracted)) * 100
        source_name = col.replace('info_', '').replace('_', ' ')
        print(f"   - {source_name[:20]}: {pct:.1f}%")

# Sexual activity
if 'ever_had_sex' in df_extracted.columns:
    sexually_active = df_extracted['ever_had_sex'].notna().sum()
    print(f"\n📌 Sexual activity:")
    print(f"   - Reported sexual activity: {sexually_active:,} ({sexually_active/len(df_extracted)*100:.1f}%)")

# ============================================
# SAVE SUMMARY REPORT
# ============================================

summary_file = OUTPUT_DIR / "student_dataset_summary.txt"
with open(summary_file, 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("DATASET 5: Student Dataset - SUMMARY\n")
    f.write("=" * 70 + "\n\n")
    
    f.write(f"Total students: {len(df_extracted):,}\n")
    f.write(f"Total columns extracted: {len(df_extracted.columns)}\n\n")
    
    if 'gender' in df_extracted.columns:
        f.write("Gender distribution:\n")
        for gender, count in df_extracted['gender'].value_counts().items():
            f.write(f"  {gender}: {count} ({count/len(df_extracted)*100:.1f}%)\n")
        f.write("\n")
    
    if 'ever_had_sex' in df_extracted.columns:
        sexually_active = df_extracted['ever_had_sex'].notna().sum()
        f.write(f"Sexually active students: {sexually_active} ({sexually_active/len(df_extracted)*100:.1f}%)\n\n")
    
    if knowledge_cols:
        f.write("Contraceptive awareness (% who have heard of):\n")
        for col in knowledge_cols:
            count = df_extracted[col].notna().sum()
            pct = (count / len(df_extracted)) * 100
            method_name = col.replace('heard_of_', '').replace('_', ' ')
            f.write(f"  {method_name}: {pct:.1f}%\n")

print(f"\n✅ Saved summary report to: {summary_file}")

print("\n" + "=" * 70)
print("✅ EXTRACTION COMPLETE!")
print("=" * 70)

print("\n📁 Output files created in: data/processed/")
print("   1. student_dataset_extracted.csv - All extracted variables")
print("   2. student_myths.csv - Adolescent myths for educational module")
print("   3. student_knowledge_gaps.csv - Contraceptive awareness gaps")
print("   4. student_info_sources.csv - Preferred information sources")
print("   5. student_contraceptive_use.csv - Contraceptive use data")
print("   6. student_dataset_summary.txt - Statistics for pitch")