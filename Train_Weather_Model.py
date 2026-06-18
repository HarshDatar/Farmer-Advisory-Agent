import pandas as pd
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("MODEL 4: WEATHER PATTERN AGGREGATOR")
print("="*60)

# ── LOAD DATA ────────────────────────────────────────────────
print("\n1. Loading data...")
weather = pd.read_csv('data/weather_data.csv')
print(f"   Shape: {weather.shape}")
print(f"   Columns: {weather.columns.tolist()}")
print(f"   Cities: {weather['cities'].unique()}")
print(f"   Parameters: {weather['PARAMETER'].unique()}")

# ── CLEAN DATA ───────────────────────────────────────────────
print("\n2. Cleaning data...")

# Drop garbage column
if 'Unnamed: 15' in weather.columns:
    weather = weather.drop(columns=['Unnamed: 15'])
    print("   Dropped: Unnamed: 15")

# Check remaining nulls
print(f"   Missing values: {weather.isnull().sum().sum()}")

# ── RESHAPE TO LONG FORMAT ───────────────────────────────────
print("\n3. Reshaping wide → long format...")

month_cols = ['JAN','FEB','MAR','APR','MAY','JUN',
              'JUL','AUG','SEP','OCT','NOV','DEC']

month_map = {
    'JAN':1,'FEB':2,'MAR':3,'APR':4,
    'MAY':5,'JUN':6,'JUL':7,'AUG':8,
    'SEP':9,'OCT':10,'NOV':11,'DEC':12
}

# Melt to long format
weather_long = weather.melt(
    id_vars=['cities', 'PARAMETER', 'YEAR'],
    value_vars=month_cols,
    var_name='Month_Name',
    value_name='Value'
)

# Add month number
weather_long['Month'] = weather_long['Month_Name'].map(month_map)

# Drop nulls
weather_long = weather_long.dropna(subset=['Value'])
weather_long = weather_long[weather_long['Value'] > 0]

print(f"   Long format shape: {weather_long.shape}")
print(f"\n   Sample:")
print(weather_long.head(5).to_string(index=False))

# ── BUILD LOOKUP TABLES ──────────────────────────────────────
print("\n4. Building lookup tables...")

# Separate Temperature and Rainfall
temp_data = weather_long[weather_long['PARAMETER'] == 'Temperature']
rain_data = weather_long[weather_long['PARAMETER'] == 'Rainfall']

print(f"   Temperature records: {len(temp_data)}")
print(f"   Rainfall records   : {len(rain_data)}")

# Aggregate by city + month (average across years)
temp_lookup = temp_data.groupby(['cities', 'Month'])['Value'].agg(
    ['mean', 'min', 'max']
).round(2)

rain_lookup = rain_data.groupby(['cities', 'Month'])['Value'].agg(
    ['mean', 'min', 'max']
).round(2)

print(f"\n   Temperature lookup shape: {temp_lookup.shape}")
print(f"   Rainfall lookup shape   : {rain_lookup.shape}")

# ── PREVIEW ──────────────────────────────────────────────────
print("\n5. Sample lookups:")
print("\n   Temperature (Pune, all months):")
if 'Pune' in temp_lookup.index.get_level_values('cities'):
    print(temp_lookup.loc['Pune'].to_string())

print("\n   Rainfall (Pune, all months):")
if 'Pune' in rain_lookup.index.get_level_values('cities'):
    print(rain_lookup.loc['Pune'].to_string())

# ── SAVE ─────────────────────────────────────────────────────
print("\n6. Saving...")
weather_patterns = {
    'temperature': temp_lookup.to_dict(orient='index'),
    'rainfall': rain_lookup.to_dict(orient='index'),
    'cities': list(weather['cities'].unique()),
    'months': month_map
}

pickle.dump(weather_patterns, open('models/weather_patterns.pkl', 'wb'))
print("   ✅ Saved: models/weather_patterns.pkl")

# ── TEST LOOKUP ───────────────────────────────────────────────
print("\n7. Test lookup:")

def get_weather(city, month):
    try:
        temp = weather_patterns['temperature'][('Pune', month)]['mean']
        rain = weather_patterns['rainfall'][('Pune', month)]['mean']
        return temp, rain
    except:
        return None, None

cities = weather_patterns['cities']
print(f"   Available cities: {cities}")

for city in cities[:2]:
    temp, rain = get_weather(city, 6)  # June
    if temp:
        print(f"   {city} June → Temp: {temp}°C, Rainfall: {rain}mm")

print("\n" + "="*60)
print("✅ MODEL 4 COMPLETE!")
print("="*60)