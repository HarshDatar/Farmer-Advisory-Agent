import os

# List files in data folder
files = os.listdir('data')
print("Files downloaded:")
for f in files:
    if f.endswith('.csv'):
        print(f"  ✓ {f}")
