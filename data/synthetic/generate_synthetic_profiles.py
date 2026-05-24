"""
Synthetic Data Generator for NuruCare
Creates realistic patient profiles for demo and testing

Run this script: python data/synthetic/generate_synthetic_profiles.py
"""

import json
import random
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================

NUM_PROFILES = 50  # Generate 50 synthetic patients
RANDOM_SEED = 42   # Ensures reproducibility (same random numbers every run)
random.seed(RANDOM_SEED)

# Output file paths
OUTPUT_JSON = Path(__file__).parent / "synthetic_profiles.json"
OUTPUT_CSV = Path(__file__).parent / "synthetic_profiles.csv"

# ============================================
# AGE DISTRIBUTION (Based on Kenya DHS data)
# ============================================
# Percentages of women in each age group
AGE_GROUPS = [
    {"range": (15, 19), "weight": 0.18},   # 18% are 15-19
    {"range": (20, 24), "weight": 0.22},   # 22% are 20-24
    {"range": (25, 29), "weight": 0.20},   # 20% are 25-29
    {"range": (30, 34), "weight": 0.16},   # 16% are 30-34
    {"range": (35, 39), "weight": 0.12},   # 12% are 35-39
    {"range": (40, 44), "weight": 0.08},   # 8% are 40-44
    {"range": (45, 49), "weight": 0.04},   # 4% are 45-49
]

def generate_age():
    """Generate a random age based on realistic distribution"""
    for group in AGE_GROUPS:
        if random.random() < group["weight"]:
            return random.randint(group["range"][0], group["range"][1])
    return random.randint(20, 35)  # Fallback

# ============================================
# BLOOD PRESSURE DISTRIBUTION
# ============================================
# Normal ranges for different ages
BP_NORMAL = {
    "young": {"systolic": (90, 120), "diastolic": (60, 80)},      # 15-30 years
    "adult": {"systolic": (110, 130), "diastolic": (70, 85)},     # 31-40 years
    "older": {"systolic": (120, 140), "diastolic": (80, 90)}      # 41-49 years
}

# Hypertension prevalence (by age)
HYPERTENSION_RATES = {
    (15, 29): 0.05,   # 5% of young women have hypertension
    (30, 39): 0.12,   # 12% of 30-39 year olds
    (40, 49): 0.25,   # 25% of 40-49 year olds
}

def generate_bp(age):
    """Generate blood pressure reading based on age"""
    # Determine age category
    if age <= 30:
        category = "young"
    elif age <= 40:
        category = "adult"
    else:
        category = "older"
    
    # Check if hypertensive
    for (min_age, max_age), rate in HYPERTENSION_RATES.items():
        if min_age <= age <= max_age:
            is_hypertensive = random.random() < rate
            break
    else:
        is_hypertensive = False
    
    if is_hypertensive:
        # Hypertensive range
        systolic = random.randint(140, 180)
        diastolic = random.randint(90, 110)
    else:
        # Normal range
        ranges = BP_NORMAL[category]
        systolic = random.randint(ranges["systolic"][0], ranges["systolic"][1])
        diastolic = random.randint(ranges["diastolic"][0], ranges["diastolic"][1])
    
    return systolic, diastolic

# ============================================
# SMOKING STATUS (Kenya: very low rates)
# ============================================
# WHO data: ~2-3% of Kenyan women smoke
SMOKING_RATE = 0.03  # 3% of women smoke

def generate_smoking(age):
    """Generate smoking status"""
    # Younger women slightly more likely to smoke
    if age < 25:
        rate = 0.04  # 4%
    elif age < 35:
        rate = 0.03  # 3%
    else:
        rate = 0.02  # 2%
    return random.random() < rate

# ============================================
# MIGRAINE DISTRIBUTION
# ============================================
# Based on WHO global estimates
MIGRAINE_TYPES = [
    ("none", 0.70),        # 70% no migraines
    ("without_aura", 0.20), # 20% migraine without aura
    ("with_aura", 0.10)     # 10% migraine with aura
]

def generate_migraine():
    """Generate migraine type based on distribution"""
    rand = random.random()
    cumulative = 0
    for migraine_type, weight in MIGRAINE_TYPES:
        cumulative += weight
        if rand < cumulative:
            return migraine_type
    return "none"

# ============================================
# MENSTRUAL CYCLE REGULARITY
# ============================================
CYCLE_REGULARITY = [
    ("regular", 0.75),    # 75% regular cycles
    ("irregular", 0.25)   # 25% irregular
]

def generate_cycle_regularity():
    """Generate cycle regularity"""
    rand = random.random()
    if rand < 0.75:
        return "regular"
    return "irregular"

# ============================================
# FERTILITY INTENTIONS (Based on Client Service Statistics)
# ============================================
FERTILITY_INTENTS = [
    ("want_soon", 0.20),    # Want children within 1 year
    ("want_later", 0.35),   # Want children in 1-5 years
    ("no_more", 0.35),      # No more children
    ("unsure", 0.10)        # Unsure
]

def generate_fertility_intent(age, parity):
    """Generate fertility intent based on age and number of children"""
    # Older women or women with many children are more likely to want no more
    if age > 40 or parity >= 4:
        return "no_more"
    elif age > 35 and parity >= 2:
        # 70% chance of no_more
        return "no_more" if random.random() < 0.7 else "want_later"
    elif age < 25:
        # Younger women more likely to want later or are unsure
        rand = random.random()
        if rand < 0.3:
            return "want_soon"
        elif rand < 0.7:
            return "want_later"
        else:
            return "unsure"
    else:
        # Default distribution
        rand = random.random()
        if rand < 0.20:
            return "want_soon"
        elif rand < 0.55:
            return "want_later"
        elif rand < 0.85:
            return "no_more"
        else:
            return "unsure"

# ============================================
# BREASTFEEDING STATUS
# ============================================
def generate_breastfeeding(age, parity):
    """Generate breastfeeding status"""
    # Only women with children and in reproductive age can be breastfeeding
    if parity == 0 or age < 15 or age > 45:
        return False
    
    # ~20% of women with children under 1 year are breastfeeding
    # For synthetic purposes, we'll use parity-based probability
    probability = min(0.3, parity * 0.1)  # More children = slightly higher chance
    return random.random() < probability

# ============================================
# PARITY (Number of children)
# ============================================
def generate_parity(age):
    """Generate number of children based on age"""
    if age < 18:
        return 0
    elif age < 22:
        return random.choices([0, 1, 2], weights=[0.4, 0.5, 0.1])[0]
    elif age < 28:
        return random.choices([0, 1, 2, 3], weights=[0.2, 0.3, 0.3, 0.2])[0]
    elif age < 35:
        return random.choices([1, 2, 3, 4], weights=[0.1, 0.3, 0.4, 0.2])[0]
    elif age < 42:
        return random.choices([2, 3, 4, 5, 6], weights=[0.1, 0.2, 0.3, 0.3, 0.1])[0]
    else:
        return random.randint(3, 8)

# ============================================
# SIDE EFFECT CONCERNS
# ============================================
SIDE_EFFECT_CONCERNS = [
    "weight_gain",
    "mood_changes",
    "acne",
    "irregular_bleeding",
    "headaches",
    "none"
]

def generate_side_effect_concerns():
    """Generate 0-3 side effect concerns"""
    num_concerns = random.choices([0, 1, 2, 3], weights=[0.3, 0.4, 0.2, 0.1])[0]
    concerns = random.sample(SIDE_EFFECT_CONCERNS, min(num_concerns, len(SIDE_EFFECT_CONCERNS)))
    if "none" in concerns and len(concerns) > 1:
        concerns.remove("none")
    return concerns

# ============================================
# EDUCATION LEVEL
# ============================================
EDUCATION_LEVELS = [
    "none",
    "primary_incomplete",
    "primary_complete",
    "secondary_incomplete",
    "secondary_complete",
    "tertiary"
]

def generate_education(age):
    """Generate education level based on age"""
    if age < 18:
        return random.choice(["primary_complete", "secondary_incomplete"])
    elif age < 25:
        return random.choice(["secondary_complete", "tertiary"])
    else:
        # Older women more likely to have lower education (historical trends)
        return random.choice(["primary_complete", "secondary_incomplete", "secondary_complete"])

# ============================================
# LOCATION (Urban/Rural)
# ============================================
# Kenya: ~27% urban, 73% rural (approx)
def generate_location():
    """Generate urban/rural location"""
    return "urban" if random.random() < 0.27 else "rural"

# ============================================
# MAIN GENERATION FUNCTION
# ============================================

def generate_synthetic_profile(profile_id):
    """Generate a single synthetic patient profile"""
    
    # Step 1: Generate age first (many other variables depend on it)
    age = generate_age()
    
    # Step 2: Generate parity based on age
    parity = generate_parity(age)
    
    # Step 3: Generate blood pressure
    systolic_bp, diastolic_bp = generate_bp(age)
    
    # Step 4: Generate remaining variables
    profile = {
        "profile_id": f"SYN_{profile_id:03d}",
        "age": age,
        "parity": parity,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "smoking": generate_smoking(age),
        "migraine_type": generate_migraine(),
        "cycle_regularity": generate_cycle_regularity(),
        "fertility_intent": generate_fertility_intent(age, parity),
        "breastfeeding": generate_breastfeeding(age, parity),
        "side_effect_concerns": generate_side_effect_concerns(),
        "education": generate_education(age),
        "location": generate_location(),
    }
    
    # Add calculated fields (for convenience)
    profile["has_hypertension"] = (profile["systolic_bp"] >= 140 or profile["diastolic_bp"] >= 90)
    profile["is_high_risk_for_combined"] = (
        (profile["age"] > 35 and profile["smoking"]) or
        (profile["migraine_type"] == "with_aura") or
        profile["has_hypertension"]
    )
    
    return profile

# ============================================
# GENERATE ALL PROFILES
# ============================================

def generate_all_profiles(num_profiles=NUM_PROFILES):
    """Generate multiple synthetic profiles"""
    profiles = []
    for i in range(1, num_profiles + 1):
        profile = generate_synthetic_profile(i)
        profiles.append(profile)
    return profiles

# ============================================
# EDGE CASES (For testing specific scenarios)
# ============================================

def generate_edge_cases():
    """Generate specific edge cases for testing"""
    edge_cases = [
        {
            "profile_id": "EDGE_001",
            "age": 36,
            "parity": 2,
            "systolic_bp": 125,
            "diastolic_bp": 82,
            "smoking": True,
            "migraine_type": "none",
            "cycle_regularity": "regular",
            "fertility_intent": "want_later",
            "breastfeeding": False,
            "side_effect_concerns": ["weight_gain"],
            "education": "secondary_complete",
            "location": "urban",
            "description": "Age >35 + smoking → combined pills restricted"
        },
        {
            "profile_id": "EDGE_002",
            "age": 28,
            "parity": 1,
            "systolic_bp": 145,
            "diastolic_bp": 95,
            "smoking": False,
            "migraine_type": "none",
            "cycle_regularity": "regular",
            "fertility_intent": "no_more",
            "breastfeeding": False,
            "side_effect_concerns": ["headaches"],
            "education": "tertiary",
            "location": "urban",
            "description": "Hypertension → combined hormonal restricted"
        },
        {
            "profile_id": "EDGE_003",
            "age": 24,
            "parity": 0,
            "systolic_bp": 110,
            "diastolic_bp": 70,
            "smoking": False,
            "migraine_type": "with_aura",
            "cycle_regularity": "regular",
            "fertility_intent": "want_later",
            "breastfeeding": False,
            "side_effect_concerns": [],
            "education": "secondary_complete",
            "location": "rural",
            "description": "Migraine with aura → combined pills restricted"
        },
        {
            "profile_id": "EDGE_004",
            "age": 22,
            "parity": 0,
            "systolic_bp": 108,
            "diastolic_bp": 68,
            "smoking": False,
            "migraine_type": "none",
            "cycle_regularity": "irregular",
            "fertility_intent": "unsure",
            "breastfeeding": False,
            "side_effect_concerns": ["mood_changes"],
            "education": "secondary_incomplete",
            "location": "rural",
            "description": "Young, irregular cycles, unsure about fertility"
        },
        {
            "profile_id": "EDGE_005",
            "age": 32,
            "parity": 3,
            "systolic_bp": 118,
            "diastolic_bp": 75,
            "smoking": False,
            "migraine_type": "none",
            "cycle_regularity": "regular",
            "fertility_intent": "no_more",
            "breastfeeding": True,
            "side_effect_concerns": [],
            "education": "primary_complete",
            "location": "rural",
            "description": "Breastfeeding + no more children"
        }
    ]
    
    # Add calculated fields to edge cases
    for case in edge_cases:
        case["has_hypertension"] = (case["systolic_bp"] >= 140 or case["diastolic_bp"] >= 90)
        case["is_high_risk_for_combined"] = (
            (case["age"] > 35 and case["smoking"]) or
            (case["migraine_type"] == "with_aura") or
            case["has_hypertension"]
        )
    
    return edge_cases

# ============================================
# SAVE TO FILES
# ============================================

def save_profiles(profiles, edge_cases):
    """Save profiles to JSON and CSV"""
    
    # Combine regular and edge cases
    all_profiles = profiles + edge_cases
    
    # Save as JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_profiles, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(all_profiles)} profiles to {OUTPUT_JSON}")
    
    # Save as CSV (for Excel viewing)
    df = pd.DataFrame(all_profiles)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Saved to {OUTPUT_CSV}")
    
    # Print summary statistics
    print("\n" + "="*50)
    print("SYNTHETIC DATA SUMMARY")
    print("="*50)
    print(f"Total profiles: {len(all_profiles)}")
    print(f"  - Regular synthetic: {len(profiles)}")
    print(f"  - Edge cases: {len(edge_cases)}")
    print(f"\nAge range: {min(p['age'] for p in all_profiles)} - {max(p['age'] for p in all_profiles)}")
    print(f"Mean age: {sum(p['age'] for p in all_profiles) / len(all_profiles):.1f}")
    print(f"\nSmoking rate: {sum(1 for p in all_profiles if p['smoking']) / len(all_profiles) * 100:.1f}%")
    print(f"Hypertension rate: {sum(1 for p in all_profiles if p['has_hypertension']) / len(all_profiles) * 100:.1f}%")
    print(f"Migraine with aura: {sum(1 for p in all_profiles if p['migraine_type'] == 'with_aura') / len(all_profiles) * 100:.1f}%")
    print(f"\nFertility intent distribution:")
    for intent in ["want_soon", "want_later", "no_more", "unsure"]:
        count = sum(1 for p in all_profiles if p['fertility_intent'] == intent)
        print(f"  - {intent}: {count} ({count/len(all_profiles)*100:.1f}%)")
    
    return all_profiles

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("🚀 Generating synthetic patient profiles for NuruCare...")
    print(f"📊 Generating {NUM_PROFILES} regular profiles...")
    
    # Generate regular profiles
    regular_profiles = generate_all_profiles(NUM_PROFILES)
    
    # Generate edge cases
    print("⚠️ Generating edge cases...")
    edge_case_profiles = generate_edge_cases()
    
    # Save all profiles
    all_profiles = save_profiles(regular_profiles, edge_case_profiles)
    
    print("\n✨ Done! These profiles can now be used for testing the AI engine.")
    print("\n📁 Files created:")
    print(f"   - {OUTPUT_JSON}")
    print(f"   - {OUTPUT_CSV}")