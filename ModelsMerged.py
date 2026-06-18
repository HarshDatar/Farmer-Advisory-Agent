import pickle
import numpy as np
import pandas as pd

print("="*60)
print("VERIFYING ALL TRAINED MODELS")
print("="*60)

# ── MODEL 1: CROP RECOMMENDER ────────────────────────────────
print("\n1. Crop Recommender (XGBoost)")
crop_model = pickle.load(open('models/crop_recommender.pkl', 'rb'))
crop_le = pickle.load(open('models/crop_label_encoder.pkl', 'rb'))

sample = pd.DataFrame([[90, 42, 43, 20.8, 82.0, 6.5, 202.9]],
    columns=['N','P','K','temperature','humidity','ph','rainfall'])

probs = crop_model.predict_proba(sample)[0]
top3_idx = probs.argsort()[-3:][::-1]
top3 = crop_le.classes_[top3_idx]
top3_conf = probs[top3_idx]

print(f"   Input : N=90, P=42, K=43, Temp=20.8, Humidity=82, pH=6.5, Rainfall=202")
print(f"   Top 3 crops:")
for crop, conf in zip(top3, top3_conf):
    print(f"     → {crop:<15} ({conf*100:.1f}%)")

# ── MODEL 2: SOIL CLASSIFIER ─────────────────────────────────
print("\n2. Soil Classifier (Random Forest)")
soil_model = pickle.load(open('models/soil_classifier.pkl', 'rb'))
soil_type_enc = pickle.load(open('models/soil_type_encoder.pkl', 'rb'))
soil_quality_enc = pickle.load(open('models/soil_quality_encoder.pkl', 'rb'))

soil_type_encoded = soil_type_enc.transform(['Clay'])[0]
sample_soil = pd.DataFrame(
    [[soil_type_encoded, 6.5, 1.2, 1.0, 200, 40, 300, 25, 24]],
    columns=['Soil_Type_encoded','pH','EC','Organic_Carbon',
             'Nitrogen','Phosphorus','Potassium','Moisture','Temperature']
)

pred = soil_model.predict(sample_soil)[0]
quality = soil_quality_enc.inverse_transform([pred])[0]
probs = soil_model.predict_proba(sample_soil)[0]

print(f"   Input : Clay, pH=6.5, N=200, P=40, K=300")
print(f"   Result: {quality}")
print(f"   Confidence:")
for label, prob in zip(soil_quality_enc.classes_, probs):
    print(f"     → {label:<12} {prob*100:.1f}%")

# ── MODEL 3: PRICE FORECASTER ────────────────────────────────
print("\n3. Price Forecaster (ARIMA)")
price_data = pickle.load(open('models/price_forecaster.pkl', 'rb'))

for crop, data in price_data.items():
    print(f"   {crop:<10} → Last: ₹{data['last_price']:.2f} | Next month: ₹{data['next_month_forecast']:.2f} | Trend: {data['trend']}")

# ── MODEL 4: WEATHER PATTERNS ────────────────────────────────
print("\n4. Weather Patterns")
weather = pickle.load(open('models/weather_patterns.pkl', 'rb'))

print(f"   Cities: {weather['cities']}")

# Lookup Pune June temperature
key = ('Pune', 6)
if key in weather['temperature']:
    temp = weather['temperature'][key]['mean']
    print(f"   Pune June avg temp: {temp}°C")

print("\n" + "="*60)
print("✅ ALL MODELS VERIFIED!")
print("="*60)