import pandas as pd

print("=" * 70)
print("STUDENT DATASET - QUICK PREVIEW")
print("=" * 70)

# Load just the first 2 rows to see structure
df = pd.read_csv(r'C:\Users\brian\Downloads\Student Dataset.csv', 
                 encoding='latin1', 
                 nrows=2)

print(f"\n📌 File shape: {len(df)} rows (preview), {len(df.columns)} columns")
print(f"\n📋 First 50 column names:")
print("-" * 50)

for i, col in enumerate(df.columns[:50]):
    print(f"{i+1:3d}. {col}")

if len(df.columns) > 50:
    print(f"\n... and {len(df.columns) - 50} more columns")

print(f"\n📋 Total columns: {len(df.columns)}")