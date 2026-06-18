import pandas as pd
   

print("\n"+"="*60+"n")
print("FARMER AGENT-DAY EDA")
print("="*60)

print("\n DATASET1: Crop Recommendation")
print("--"*60)

crop= pd.read_csv("data/Crop_recommendation.csv")

print(f"Shape        : {crop.shape[0]} rows × {crop.shape[1]} columns")
print(f"Columns      : {crop.columns.tolist()}")
print(f"Missing vals : {crop.isnull().sum().sum()}")
print(f"Unique crops : {crop.iloc[:, -1].nunique()}")
print(f"\nFirst 3 rows:")
print(crop.head(3))
print(f"\nStatistics:")
print(crop.describe())
print(f"\nCrop distribution:")
print(crop.iloc[:, -1].value_counts())

print("\n"+"="*60+"\n")

print("\n DATASET2: Agricultural Prices")
print("--"*60)

prices= pd.read_csv("data/Agriculture_price_dataset.csv")

print(f"Shape        : {prices.shape[0]} rows × {prices.shape[1]} columns")
print(f"Columns      : {prices.columns.tolist()}")
print(f"Missing vals : {prices.isnull().sum().sum()}")
print(f"\nFirst 3 rows:")
print(prices.head(3))
print(f"\nStatistics:")
print(prices.describe())


for col in prices.columns:
    if prices[col].dtype == 'object':
        print(f"\nUnique values in '{col}':")
        print(prices[col].value_counts().head(10))

# ============================================================
# 3. SOIL QUALITY
# ============================================================
print("\n DATASET 3: SOIL QUALITY")
print("-"*60)

soil = pd.read_csv('data/soil_quality_dataset.csv')

print(f"Shape        : {soil.shape[0]} rows × {soil.shape[1]} columns")
print(f"Columns      : {soil.columns.tolist()}")
print(f"Missing vals : {soil.isnull().sum().sum()}")
print(f"\nFirst 3 rows:")
print(soil.head(3))
print(f"\nStatistics:")
print(soil.describe())

for col in soil.columns:
    if soil[col].dtype == 'object':
        print(f"\nUnique values in '{col}':")
        print(soil[col].value_counts())

# ============================================================
# 4. MAHARASHTRA WEATHER
# ============================================================
print("\n DATASET 4: MAHARASHTRA WEATHER")
print("-"*60)

weather = pd.read_csv('data/weather_data.csv')

print(f"Shape        : {weather.shape[0]} rows × {weather.shape[1]} columns")
print(f"Columns      : {weather.columns.tolist()}")
print(f"Missing vals : {weather.isnull().sum().sum()}")
print(f"\nFirst 3 rows:")
print(weather.head(3))
print(f"\nStatistics:")
print(weather.describe())

for col in weather.columns:
    if weather[col].dtype == 'object':
        print(f"\nUnique values in '{col}':")
        print(weather[col].value_counts().head(10))

# ============================================================
# SUMMARY
# ============================================================
print("\n\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"""
1. CROP DATA       → {crop.shape[0]} samples, {crop.iloc[:,-1].nunique()} crops
2. PRICES DATA     → {prices.shape[0]} records
3. SOIL DATA       → {soil.shape[0]} samples
4. WEATHER DATA    → {weather.shape[0]} records

Missing values across all datasets:
  Crop    : {crop.isnull().sum().sum()}
  Prices  : {prices.isnull().sum().sum()}
  Soil    : {soil.isnull().sum().sum()}
  Weather : {weather.isnull().sum().sum()}
""")