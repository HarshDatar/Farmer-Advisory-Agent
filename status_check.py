# status_check.py
import os

print("=== PROJECT STATUS CHECK ===\n")

# Check folders
folders = ['data', 'models', 'notebooks', 'knowledge_base']
print("FOLDERS:")
for f in folders:
    exists = "✅" if os.path.exists(f) else "❌ MISSING"
    print(f"  {exists} {f}/")

# Check datasets
print("\nDATASETS:")
datasets = {
    'Crop_recommendation.csv': 'Crop Recommendation',
    'Agriculture_price_dataset.csv': 'Agricultural Prices',
    'soil_quality_dataset.csv': 'Soil Quality',
    'weather_data.csv': 'Maharashtra Weather'
}

missing_datasets = []
for filename, label in datasets.items():
    path = f'data/{filename}'
    if os.path.exists(path):
        size = os.path.getsize(path) / (1024*1024)
        print(f"  ✅ {label} ({size:.1f} MB)")
    else:
        print(f"  ❌ {label} — MISSING")
        missing_datasets.append(filename)

# Check Python packages
print("\nPACKAGES:")
packages = ['pandas', 'numpy', 'sklearn', 'xgboost', 'statsmodels', 'gpt4all']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  ✅ {pkg}")
    except ImportError:
        print(f"  ❌ {pkg} — NOT INSTALLED")

print("\n=== DONE ===")