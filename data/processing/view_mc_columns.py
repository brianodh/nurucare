import pandas as pd

# Load the file
df = pd.read_csv(r'C:\Users\brian\Downloads\MC_Baseline_final_ANON.csv', 
                 encoding='latin1', 
                 nrows=5)

print("=" * 70)
print("ALL COLUMN NAMES IN MC BASELINE DATASET")
print("=" * 70)
print()

for i, col in enumerate(df.columns):
    print(f"{i+1:3d}. {col}")

print()
print(f"Total columns: {len(df.columns)}")

# Show first row of data for context
print("\n" + "=" * 70)
print("FIRST ROW OF DATA (Sample - Key Columns)")
print("=" * 70)

# Look for columns that might contain menstrual cycle data
key_patterns = ['cycle', 'period', 'menstru', 'q1_', 'q2_', 'q3_', 'q4_', 'age', 'symptom']
for col in df.columns[:100]:  # Check first 100 columns
    if any(pattern in col.lower() for pattern in key_patterns):
        value = df[col].iloc[0] if len(df[col].dropna()) > 0 else "NaN"
        print(f"{col}: {value}")