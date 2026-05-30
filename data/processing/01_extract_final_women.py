"""
Dataset 1: Final Women Data ANON - Variable Extraction
Extracts variables for: Myths, Side Effects, Fertility Intentions, Why Not Using FP

Author: Brian
Date: May 24, 2026
Purpose: Extract key variables for NuruCare AI engine
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURATION - UPDATE THIS PATH
# ============================================

# TODO: Change this to where YOUR file is located
INPUT_FILE = r"C:\Users\brian\Downloads\Final_women_Data_ANON.csv"

# Output files
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "final_women_extracted.csv"
MYTHS_FILE = OUTPUT_DIR / "final_women_myths.csv"
SIDE_EFFECTS_FILE = OUTPUT_DIR / "final_women_side_effects.csv"
FERTILITY_FILE = OUTPUT_DIR / "final_women_fertility.csv"

print("=" * 60)
print("DATASET 1: Final Women Data ANON - Variable Extraction")
print("=" * 60)

# ============================================
# STEP 1: LOAD THE DATASET
# ============================================

print("\n📂 Loading dataset...")

try:
    # Try CSV with different encodings
    encodings_to_try = ['utf-8', 'latin1', 'cp1252', 'ISO-8859-1', 'utf-16']
    
    df = None
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(INPUT_FILE, encoding=encoding)
            print(f"✅ Loaded CSV with {encoding} encoding: {len(df)} rows, {len(df.columns)} columns")
            break
        except UnicodeDecodeError:
            print(f"   Failed with {encoding}, trying next...")
            continue
        except Exception as e:
            print(f"   Error with {encoding}: {e}")
            continue
    
    if df is None:
        raise Exception("Could not read file with any encoding")
        
except FileNotFoundError:
    try:
        # Try Excel if CSV not found
        df = pd.read_excel(INPUT_FILE)
        print(f"✅ Loaded Excel: {len(df)} rows, {len(df.columns)} columns")
    except:
        print(f"❌ File not found at: {INPUT_FILE}")
        print("\n📌 Please update the INPUT_FILE path to where your file is located.")
        print("   Current path:", INPUT_FILE)
        exit(1)
except FileNotFoundError:
    try:
        # Try Excel if CSV not found
        df = pd.read_excel(INPUT_FILE)
        print(f"✅ Loaded Excel: {len(df)} rows, {len(df.columns)} columns")
    except:
        print(f"❌ File not found at: {INPUT_FILE}")
        print("\n📌 Please update the INPUT_FILE path to where your file is located.")
        print("   Current path:", INPUT_FILE)
        exit(1)

# ============================================
# STEP 2: IDENTIFY VARIABLES TO EXTRACT
# ============================================

print("\n🔍 Identifying variables to extract...")

# Based on the documentation, here are the key variables:
#
# For Myths (v378-v384):
#   v378 - "Contraceptive injection can make a woman permanently infertile"
#   v379 - "People who use contraception end up with health problems"
#   v380 - "Contraceptives can harm your womb"
#   v381 - "Contraceptives reduce sexual urge"
#   v382 - "Contraceptives can cause cancer"
#   v383 - "Contraceptives can give you deformed babies"
#   v384 - "Contraceptives are dangerous to your health"
#
# For Side Effects (v334, v336, v351):
#   v334a-v334x - Why stopped using method
#   v336a-v336x - Problems experienced with last method
#   v351a-v351x - Known side effects
#
# For Fertility Intentions (v602, v603, v604, v608, v609, v612):
#   v602 - Prefer to have another child?
#   v603 - How soon?
#   v612 - Preferred number of children
#
# For Why Not Using FP (v341a-v341w):
#   v341a-v341w - Reasons for not using contraception
#   v3411st, v3412nd, v3413rd - Top 3 reasons

# Let's list all variables we want to extract
VARIABLES_TO_EXTRACT = {
    # Demographics (for context)
    'vq01': 'woman_id',
    'v102': 'age',
    'v104': 'education_level',
    'v105': 'education_completed',
    'v512': 'marital_status',
    
    # Fertility Intentions
    'v602': 'prefer_more_children',
    'v603': 'how_soon_years',
    'v612': 'preferred_children_count',
    'v608': 'partner_prefer_more_children',
    'v609': 'partner_how_soon_years',
    'v604': 'problem_if_pregnant',
    
    # Current Contraceptive Use
    'v310': 'currently_doing_to_avoid_pregnancy',
    'v311': 'current_method',
    'v312': 'who_decided_current_method',
    
    # Method History
    'v302a': 'ever_used_female_sterilization',
    'v302b': 'ever_used_male_sterilization',
    'v302c': 'ever_used_pill',
    'v302d': 'ever_used_iud',
    'v302e': 'ever_used_injectables',
    'v302f': 'ever_used_implants',
    'v302g': 'ever_used_male_condom',
    'v302h': 'ever_used_female_condom',
    'v302i': 'ever_used_rhythm',
    'v302j': 'ever_used_withdrawal',
    'v302k': 'ever_used_emergency',
    'v302l': 'ever_used_lam',
    
    # Method at Last Sex
    'v508': 'fp_used_at_last_sex',
    'v509a': 'last_sex_pill',
    'v509c': 'last_sex_male_condom',
    'v509e': 'last_sex_injectables',
    'v509f': 'last_sex_implants',
    'v509g': 'last_sex_iud',
    'v509i': 'last_sex_natural',
    'v509j': 'last_sex_lam',
    
    # MYTHS (v378-v384)
    'v378': 'myth_injection_infertility',
    'v379': 'myth_contraceptives_health_problems',
    'v380': 'myth_contraceptives_harm_womb',
    'v381': 'myth_contraceptives_reduce_urge',
    'v382': 'myth_contraceptives_cause_cancer',
    'v383': 'myth_contraceptives_deformed_babies',
    'v384': 'myth_contraceptives_dangerous',
    
    # SIDE EFFECTS - Why stopped using method (v334)
    'v334a': 'stop_reason_wanted_pregnant',
    'v334b': 'stop_reason_method_failed',
    'v334c': 'stop_reason_no_sexual_urge',
    'v334d': 'stop_reason_menstrual_problem',
    'v334e': 'stop_reason_health_problem',
    'v334g': 'stop_reason_inconvenient',
    'v334h': 'stop_reason_hard_to_get',
    'v334i': 'stop_reason_weight_change',
    'v334m': 'stop_reason_partner_disapprove',
    
    # SIDE EFFECTS - Problems with last method (v336)
    'v336a': 'problem_method_failed',
    'v336b': 'problem_no_sexual_urge',
    'v336c': 'problem_bleeding',
    'v336d': 'problem_backache',
    'v336e': 'problem_headache',
    'v336f': 'problem_nausea',
    'v336j': 'problem_weight_gain',
    'v336k': 'problem_weakness',
    
    # SIDE EFFECTS - Known side effects (v351)
    'v351a': 'side_effect_bleeding',
    'v351b': 'side_effect_weight_change',
    'v351c': 'side_effect_headaches',
    'v351d': 'side_effect_backaches',
    'v351e': 'side_effect_nausea',
    'v351f': 'side_effect_sleeplessness',
    'v351g': 'side_effect_weakness',
    'v351h': 'side_effect_no_urge',
    'v351i': 'side_effect_other_health',
    'v351j': 'side_effect_infertility_fear',
    'v351k': 'side_effect_cancer_fear',
    
    # WHY NOT USING FP (v341)
    'v341a': 'not_using_infrequent_sex',
    'v341b': 'not_using_away_from_spouse',
    'v341c': 'not_using_already_pregnant',
    'v341d': 'not_using_breastfeeding',
    'v341e': 'not_using_wants_more_children',
    'v341f': 'not_using_menopausal',
    'v341h': 'not_using_respondent_opposes',
    'v341i': 'not_using_partner_opposes',
    'v341k': 'not_using_religious',
    'v341l': 'not_using_dont_know_method',
    'v341m': 'not_using_dont_know_how',
    'v341n': 'not_using_knows_no_source',
    'v341o': 'not_using_health_concerns',
    'v341p': 'not_using_fear_side_effects',
    'v341q': 'not_using_too_far',
    'v341r': 'not_using_costs_too_much',
    'v3411st': 'not_using_reason_1st',
    'v3412nd': 'not_using_reason_2nd',
    'v3413rd': 'not_using_reason_3rd',
    
    # PARTNER DYNAMICS
    'v703': 'discussed_fp_with_spouse',
    'v704': 'discussed_fp_frequency',
    'v709': 'need_permission_for_fp',
    'v710a': 'permission_needed_husband',
    'v710b': 'permission_needed_father',
    'v710c': 'permission_needed_mother',
    
    # PREGNANCY HISTORY
    'v201': 'ever_given_birth',
    'v202': 'children_living_with_you',
    'v203son': 'sons_living_with_you',
    'v203dau': 'daughters_living_with_you',
    'v227': 'currently_pregnant',
    'v228': 'months_pregnant',
}

# ============================================
# STEP 3: EXTRACT ONLY VARIABLES THAT EXIST
# ============================================

print("\n📊 Extracting available variables...")

extracted_data = {}
extracted_vars = []
missing_vars = []

for var, new_name in VARIABLES_TO_EXTRACT.items():
    if var in df.columns:
        extracted_data[new_name] = df[var]
        extracted_vars.append(f"{var} → {new_name}")
    else:
        missing_vars.append(var)

print(f"\n✅ Found {len(extracted_vars)} variables")
print(f"⚠️ Missing {len(missing_vars)} variables (they may have different names)")

# Create extracted DataFrame
df_extracted = pd.DataFrame(extracted_data)

# ============================================
# STEP 4: CREATE MYTHS-ONLY DATAFRAME
# ============================================

print("\n📖 Creating myths-only dataset...")

myth_columns = [col for col in df_extracted.columns if col.startswith('myth_')]
if myth_columns:
    df_myths = df_extracted[['woman_id', 'age'] + myth_columns].copy()
    df_myths.to_csv(MYTHS_FILE, index=False)
    print(f"✅ Saved {len(df_myths)} rows with {len(myth_columns)} myths to {MYTHS_FILE}")
else:
    print("⚠️ No myth columns found")

# ============================================
# STEP 5: CREATE SIDE EFFECTS DATAFRAME
# ============================================

print("\n💊 Creating side effects dataset...")

side_effect_columns = [col for col in df_extracted.columns if col.startswith('side_effect_') or 
                       col.startswith('problem_') or col.startswith('stop_reason_')]

if side_effect_columns:
    df_side_effects = df_extracted[['woman_id', 'age'] + side_effect_columns].copy()
    df_side_effects.to_csv(SIDE_EFFECTS_FILE, index=False)
    print(f"✅ Saved {len(df_side_effects)} rows with {len(side_effect_columns)} side effects")
else:
    print("⚠️ No side effect columns found")

# ============================================
# STEP 6: CREATE FERTILITY DATAFRAME
# ============================================

print("\n👶 Creating fertility intentions dataset...")

fertility_columns = [col for col in df_extracted.columns if 'fertility' in col.lower() or 
                     'prefer_' in col or 'children' in col or 'pregnant' in col]

if fertility_columns:
    df_fertility = df_extracted[['woman_id', 'age'] + fertility_columns].copy()
    df_fertility.to_csv(FERTILITY_FILE, index=False)
    print(f"✅ Saved {len(df_fertility)} rows with fertility data")
else:
    print("⚠️ No fertility columns found")

# ============================================
# STEP 7: SAVE MAIN EXTRACTED FILE
# ============================================

print("\n💾 Saving main extracted dataset...")

df_extracted.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Saved {len(df_extracted)} rows, {len(df_extracted.columns)} columns to:")
print(f"   {OUTPUT_FILE}")

# ============================================
# STEP 8: PRINT SUMMARY STATISTICS
# ============================================

print("\n" + "=" * 60)
print("📊 SUMMARY STATISTICS - Final Women Dataset")
print("=" * 60)

print(f"\n📌 Total women: {len(df_extracted):,}")

# Age distribution
if 'age' in df_extracted.columns:
    print(f"\n📌 Age distribution:")
    print(f"   - Mean age: {df_extracted['age'].mean():.1f} years")
    print(f"   - Age range: {df_extracted['age'].min()} - {df_extracted['age'].max()} years")

# Myth agreement rates
if myth_columns:
    print(f"\n📌 Myth agreement rates (percentage who agree/believe):")
    for col in myth_columns[:7]:  # Show first 7 myths
        if col in df_extracted.columns:
            # Count non-null and non-empty responses that indicate agreement
            # (1 or "yes" or "agree" typically means believes the myth)
            myth_name = col.replace('myth_', '').replace('_', ' ')
            # Simple count of responses (you may need to adjust based on actual values)
            count = df_extracted[col].notna().sum()
            pct = (count / len(df_extracted)) * 100
            print(f"   - {myth_name[:40]}: {pct:.1f}% responded")

# Reasons for not using
if 'not_using_breastfeeding' in df_extracted.columns:
    bf_count = df_extracted['not_using_breastfeeding'].sum() if df_extracted['not_using_breastfeeding'].dtype in ['int64', 'float64'] else df_extracted['not_using_breastfeeding'].notna().sum()
    print(f"\n📌 Breastfeeding as reason for non-use: {bf_count} women")

# Fertility intentions
if 'prefer_more_children' in df_extracted.columns:
    prefer_counts = df_extracted['prefer_more_children'].value_counts()
    print(f"\n📌 Fertility intentions:")
    for intent, count in prefer_counts.head(5).items():
        print(f"   - {intent}: {count} ({count/len(df_extracted)*100:.1f}%)")

print("\n" + "=" * 60)
print("✅ EXTRACTION COMPLETE - Final Women Dataset")
print("=" * 60)
print(f"\n📁 Output files:")
print(f"   Main: {OUTPUT_FILE}")
print(f"   Myths: {MYTHS_FILE}")
print(f"   Side Effects: {SIDE_EFFECTS_FILE}")
print(f"   Fertility: {FERTILITY_FILE}")