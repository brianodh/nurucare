import pandas as pd

# Load just the first row
df = pd.read_csv(r'C:\Users\brian\Downloads\Final_women_Data_ANON.csv', 
                 encoding='latin1', 
                 nrows=1)

print("=" * 80)
print("ALL COLUMN NAMES IN YOUR FILE")
print("=" * 80)
print()

# Print all columns with numbers
for i, col in enumerate(df.columns):
    print(f"{i+1:4d}. {col}")

print()
print(f"Total columns: {len(df.columns)}")