"""
Dataset 1: Final Women Data ANON - COMPLETE VARIABLE EXTRACTION
Based on actual column names from the file

This script extracts ALL the variables needed for NuruCare AI engine:
- Demographics (age, education, marital status)
- Contraceptive knowledge and use
- Myths (q378-q384) - CRITICAL for educational module
- Side effects (q334, q336, q351)
- Fertility intentions (q602, q603, q612)
- Why not using FP (q341)
- Partner dynamics (q703-q730)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================

INPUT_FILE = r"C:\Users\brian\Downloads\Final_women_Data_ANON.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("DATASET 1: Final Women Data ANON - COMPLETE EXTRACTION")
print("=" * 70)

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
extracted['woman_id'] = df['womanID']
extracted['hh_id'] = df['hhldID']
extracted['province'] = df['province']
extracted['district'] = df['district']
extracted['division'] = df['division']
extracted['location'] = df['location']
extracted['weight'] = df['weight']
extracted['age'] = df['q102']                    # Age
extracted['age_check'] = df['q103']              # Age check (15-49)
extracted['education_level'] = df['q104']        # Highest education level
extracted['education_completed'] = df['q105']    # Education completed
extracted['reads_newspaper'] = df['q107']        # Reads newspaper
extracted['listens_radio'] = df['q108']          # Listens to radio
extracted['watches_tv'] = df['q109']             # Watches TV
extracted['religion'] = df['q110']               # Religion
extracted['religiosity'] = df['q111']            # How religious
extracted['ethnicity'] = df['q112']              # Ethnic group
extracted['marital_status'] = df['q512']         # Current marital status

print("   ✅ Extracted demographics")

# ----------------------------------------------------------------------
# 2. PREGNANCY & BIRTH HISTORY
# ----------------------------------------------------------------------
extracted['ever_given_birth'] = df['q201']
extracted['children_living_with_you'] = df['q202']
extracted['sons_living_with_you'] = df['q203_son']
extracted['daughters_living_with_you'] = df['q203_daug']
extracted['children_living_elsewhere'] = df['q204']
extracted['sons_elsewhere'] = df['q205_son']
extracted['daughters_elsewhere'] = df['q205_daug']
extracted['children_died'] = df['q206']
extracted['boys_died'] = df['q207_boy']
extracted['girls_died'] = df['q207_girl']
extracted['total_children_ever_born'] = df['q208']
extracted['currently_pregnant'] = df['q227']
extracted['months_pregnant'] = df['q228']
extracted['attended_anc'] = df['q229']

print("   ✅ Extracted pregnancy history")

# ----------------------------------------------------------------------
# 3. CONTRACEPTIVE KNOWLEDGE (q301_01 to q301_16)
# ----------------------------------------------------------------------
contraceptive_methods = {
    'q301_01': 'knows_female_sterilization',
    'q301_02': 'knows_male_sterilization',
    'q301_03': 'knows_pill',
    'q301_04': 'knows_iud',
    'q301_05': 'knows_injectables',
    'q301_06': 'knows_implants',
    'q301_07': 'knows_male_condom',
    'q301_08': 'knows_female_condom',
    'q301_09': 'knows_rhythm',
    'q301_10': 'knows_withdrawal',
    'q301_11': 'knows_emergency',
    'q301_12': 'knows_lam',
}

for col, name in contraceptive_methods.items():
    if col in df.columns:
        extracted[name] = df[col]

print("   ✅ Extracted contraceptive knowledge")

# ----------------------------------------------------------------------
# 4. EVER USED CONTRACEPTION (q302_01 to q302_16)
# ----------------------------------------------------------------------
ever_used_methods = {
    'q302_01': 'ever_used_female_sterilization',
    'q302_02': 'ever_used_male_sterilization',
    'q302_03': 'ever_used_pill',
    'q302_04': 'ever_used_iud',
    'q302_05': 'ever_used_injectables',
    'q302_06': 'ever_used_implants',
    'q302_07': 'ever_used_male_condom',
    'q302_08': 'ever_used_female_condom',
    'q302_09': 'ever_used_rhythm',
    'q302_10': 'ever_used_withdrawal',
    'q302_11': 'ever_used_emergency',
    'q302_12': 'ever_used_lam',
}

for col, name in ever_used_methods.items():
    if col in df.columns:
        extracted[name] = df[col]

print("   ✅ Extracted ever-used contraception")

# ----------------------------------------------------------------------
# 5. CURRENT CONTRACEPTIVE USE
# ----------------------------------------------------------------------
extracted['currently_using_fp'] = df['q310']      # Doing anything to avoid pregnancy
extracted['current_method'] = df['q311']          # Method currently using
extracted['current_method_decided_by'] = df['q312']  # Who decided
extracted['told_about_side_effects'] = df['q313']    # Told about side effects
extracted['told_what_to_do'] = df['q314']            # Told what to do if problems
extracted['told_about_other_methods'] = df['q315']   # Told about other methods

print("   ✅ Extracted current contraceptive use")

# ----------------------------------------------------------------------
# 6. METHOD AT LAST SEX
# ----------------------------------------------------------------------
extracted['fp_used_at_last_sex'] = df['q508']
fp_last_sex = {
    'q509a': 'last_sex_pill',
    'q509c': 'last_sex_male_condom',
    'q509e': 'last_sex_injectables',
    'q509f': 'last_sex_implants',
    'q509g': 'last_sex_iud',
    'q509i': 'last_sex_natural',
    'q509j': 'last_sex_lam',
}
for col, name in fp_last_sex.items():
    if col in df.columns:
        extracted[name] = df[col]

print("   ✅ Extracted last sex method")

# ----------------------------------------------------------------------
# 7. MYTHS (q378 to q384) - GOLD for educational module!
# ----------------------------------------------------------------------
myths = {
    'q378': 'myth_injection_causes_infertility',
    'q379': 'myth_contraceptives_cause_health_problems',
    'q380': 'myth_contraceptives_harm_womb',
    'q381': 'myth_contraceptives_reduce_sexual_urge',
    'q382': 'myth_contraceptives_cause_cancer',
    'q383': 'myth_contraceptives_cause_deformed_babies',
    'q384': 'myth_contraceptives_are_dangerous',
}

for col, name in myths.items():
    if col in df.columns:
        extracted[name] = df[col]
        print(f"   ✅ Found myth: {name}")

print("   ✅ Extracted 7 contraceptive myths")

# ----------------------------------------------------------------------
# 8. SIDE EFFECTS - Why stopped using (q334a to q334x)
# ----------------------------------------------------------------------
stop_reasons = {
    'q334a': 'stop_wanted_pregnant',
    'q334b': 'stop_method_failed',
    'q334c': 'stop_no_sexual_urge',
    'q334d': 'stop_menstrual_problem',
    'q334e': 'stop_health_problem',
    'q334g': 'stop_inconvenient',
    'q334h': 'stop_hard_to_get',
    'q334i': 'stop_weight_change',
    'q334m': 'stop_partner_disapproved',
}
for col, name in stop_reasons.items():
    if col in df.columns:
        extracted[name] = df[col]

# ----------------------------------------------------------------------
# 9. SIDE EFFECTS - Problems with last method (q336a to q336x)
# ----------------------------------------------------------------------
problems = {
    'q336a': 'problem_method_failed',
    'q336b': 'problem_no_sexual_urge',
    'q336c': 'problem_bleeding',
    'q336d': 'problem_backache',
    'q336e': 'problem_headache',
    'q336f': 'problem_nausea',
    'q336j': 'problem_weight_gain',
    'q336k': 'problem_weakness',
}
for col, name in problems.items():
    if col in df.columns:
        extracted[name] = df[col]

# ----------------------------------------------------------------------
# 10. SIDE EFFECTS - Known side effects (q351a to q351x)
# ----------------------------------------------------------------------
known_side_effects = {
    'q351a': 'side_effect_bleeding',
    'q351b': 'side_effect_weight_change',
    'q351c': 'side_effect_headaches',
    'q351d': 'side_effect_backaches',
    'q351e': 'side_effect_nausea',
    'q351f': 'side_effect_sleeplessness',
    'q351g': 'side_effect_weakness',
    'q351h': 'side_effect_no_urge',
    'q351j': 'side_effect_fear_infertility',
    'q351k': 'side_effect_fear_cancer',
}
for col, name in known_side_effects.items():
    if col in df.columns:
        extracted[name] = df[col]

print("   ✅ Extracted side effects")

# ----------------------------------------------------------------------
# 11. WHY NOT USING FAMILY PLANNING (q341a to q341w)
# ----------------------------------------------------------------------
reasons_not_using = {
    'q341a': 'not_using_infrequent_sex',
    'q341b': 'not_using_away_from_spouse',
    'q341c': 'not_using_already_pregnant',
    'q341d': 'not_using_breastfeeding',
    'q341e': 'not_using_wants_more_children',
    'q341h': 'not_using_respondent_opposes',
    'q341i': 'not_using_partner_opposes',
    'q341k': 'not_using_religious',
    'q341l': 'not_using_dont_know_method',
    'q341m': 'not_using_dont_know_how',
    'q341n': 'not_using_knows_no_source',
    'q341o': 'not_using_health_concerns',
    'q341p': 'not_using_fear_side_effects',
    'q341q': 'not_using_too_far',
    'q341r': 'not_using_costs_too_much',
    'q341_1st': 'not_using_reason_1st',
    'q341_2nd': 'not_using_reason_2nd',
    'q341_3rd': 'not_using_reason_3rd',
}
for col, name in reasons_not_using.items():
    if col in df.columns:
        extracted[name] = df[col]

print("   ✅ Extracted reasons for not using FP")

# ----------------------------------------------------------------------
# 12. FERTILITY INTENTIONS
# ----------------------------------------------------------------------
extracted['fertility_preference'] = df['q602_response']      # Prefer more children?
extracted['fertility_timing_value'] = df['q603_value']       # How soon (value)
extracted['fertility_timing_unit'] = df['q603_unit']         # How soon (unit)
extracted['problem_if_pregnant'] = df['q605']                # Problem if pregnant?
extracted['preferred_children_count'] = df['q612_value']     # Preferred number
extracted['preferred_boys'] = df['q613_boys']                # Preferred boys
extracted['preferred_girls'] = df['q613_girls']              # Preferred girls

print("   ✅ Extracted fertility intentions")

# ----------------------------------------------------------------------
# 13. PARTNER DYNAMICS
# ----------------------------------------------------------------------
extracted['discussed_fp_with_spouse'] = df['q704']           # Discussed FP?
extracted['need_permission_for_fp'] = df['q709']             # Need permission?
extracted['permission_from_husband'] = df['q710a']           # Husband permission
extracted['husband_approves_fp'] = df['q731a']               # Husband approves?

print("   ✅ Extracted partner dynamics")

# ============================================
# CREATE DATAFRAME AND SAVE
# ============================================

print("\n💾 Creating final dataset...")

df_extracted = pd.DataFrame(extracted)

# Save main extracted file
output_file = OUTPUT_DIR / "final_women_extracted_complete.csv"
df_extracted.to_csv(output_file, index=False)
print(f"✅ Saved {len(df_extracted):,} rows, {len(df_extracted.columns)} columns to:")
print(f"   {output_file}")

# ----------------------------------------------------------------------
# CREATE SPECIALIZED DATASETS
# ----------------------------------------------------------------------

# 1. Myths only dataset (for educational module)
myth_cols = ['woman_id', 'age'] + [col for col in df_extracted.columns if 'myth_' in col]
if len(myth_cols) > 2:
    df_myths = df_extracted[myth_cols].copy()
    myths_file = OUTPUT_DIR / "final_women_myths.csv"
    df_myths.to_csv(myths_file, index=False)
    print(f"✅ Saved myths dataset: {myths_file}")

# 2. Side effects dataset
side_cols = ['woman_id', 'age'] + [col for col in df_extracted.columns if any(x in col for x in ['stop_', 'problem_', 'side_effect_'])]
if len(side_cols) > 2:
    df_side = df_extracted[side_cols].copy()
    side_file = OUTPUT_DIR / "final_women_side_effects.csv"
    df_side.to_csv(side_file, index=False)
    print(f"✅ Saved side effects dataset: {side_file}")

# 3. Fertility intentions dataset
fert_cols = ['woman_id', 'age'] + [col for col in df_extracted.columns if any(x in col for x in ['fertility_', 'preferred_', 'problem_if_pregnant'])]
if len(fert_cols) > 2:
    df_fert = df_extracted[fert_cols].copy()
    fert_file = OUTPUT_DIR / "final_women_fertility.csv"
    df_fert.to_csv(fert_file, index=False)
    print(f"✅ Saved fertility dataset: {fert_file}")

# 4. Contraceptive use dataset
contra_cols = ['woman_id', 'age'] + [col for col in df_extracted.columns if any(x in col for x in ['knows_', 'ever_used_', 'current_', 'last_sex'])]
if len(contra_cols) > 2:
    df_contra = df_extracted[contra_cols].copy()
    contra_file = OUTPUT_DIR / "final_women_contraceptive_use.csv"
    df_contra.to_csv(contra_file, index=False)
    print(f"✅ Saved contraceptive use dataset: {contra_file}")

# 5. Why not using FP dataset
not_using_cols = ['woman_id', 'age'] + [col for col in df_extracted.columns if 'not_using_' in col]
if len(not_using_cols) > 2:
    df_not_using = df_extracted[not_using_cols].copy()
    not_using_file = OUTPUT_DIR / "final_women_not_using.csv"
    df_not_using.to_csv(not_using_file, index=False)
    print(f"✅ Saved 'why not using' dataset: {not_using_file}")

# ============================================
# PRINT SUMMARY STATISTICS
# ============================================

print("\n" + "=" * 70)
print("📊 SUMMARY STATISTICS")
print("=" * 70)

print(f"\n📌 Total women: {len(df_extracted):,}")

if 'age' in df_extracted.columns:
    print(f"\n📌 Age distribution:")
    print(f"   - Mean: {df_extracted['age'].mean():.1f} years")
    print(f"   - Min: {df_extracted['age'].min():.0f}")
    print(f"   - Max: {df_extracted['age'].max():.0f}")

# Myth agreement rates
myth_columns = [col for col in df_extracted.columns if 'myth_' in col]
if myth_columns:
    print(f"\n📌 Myth agreement rates (percentage who agree/believe):")
    for col in myth_columns[:7]:
        # Count non-null values (those who responded)
        count = df_extracted[col].notna().sum()
        pct = (count / len(df_extracted)) * 100
        myth_name = col.replace('myth_', '').replace('_', ' ')
        print(f"   - {myth_name[:35]}: {pct:.1f}% responded")

# Current contraceptive use
if 'currently_using_fp' in df_extracted.columns:
    using_count = df_extracted['currently_using_fp'].notna().sum()
    print(f"\n📌 Current FP use data available for: {using_count:,} women")

# Fertility intentions
if 'fertility_preference' in df_extracted.columns:
    pref_counts = df_extracted['fertility_preference'].value_counts()
    print(f"\n📌 Fertility preferences:")
    for val, cnt in pref_counts.head(5).items():
        print(f"   - {val}: {cnt} ({cnt/len(df_extracted)*100:.1f}%)")

print("\n" + "=" * 70)
print("✅ EXTRACTION COMPLETE!")
print("=" * 70)

print("\n📁 Output files created in: data/processed/")
print("   1. final_women_extracted_complete.csv - All extracted variables")
print("   2. final_women_myths.csv - 7 myths for educational module")
print("   3. final_women_side_effects.csv - Side effects data")
print("   4. final_women_fertility.csv - Fertility intentions")
print("   5. final_women_contraceptive_use.csv - Contraceptive knowledge & use")
print("   6. final_women_not_using.csv - Reasons for not using FP")