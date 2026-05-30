import pandas as pd

# Load the file
df = pd.read_csv(r'C:\Users\brian\Downloads\ddi_pds_data.csv', 
                 encoding='latin1', 
                 nrows=5)

print("=" * 70)
print("ALL COLUMN NAMES IN PROSPECTIVE MORBIDITY DATASET")
print("=" * 70)
print()

for i, col in enumerate(df.columns):
    print(f"{i+1:3d}. {col}")

print()
print(f"Total columns: {len(df.columns)}")

# Show first row of data for context
print("\n" + "=" * 70)
print("FIRST ROW OF DATA (Sample)")
print("=" * 70)
print(df.iloc[0].to_string())