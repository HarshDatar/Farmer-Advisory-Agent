import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import pickle

print("="*60)
print("MODEL 2: SOIL QUALITY CLASSIFIER (Random Forest)")
print("="*60)

# ── LOAD DATA ────────────────────────────────────────────────
print("\n1. Loading data...")
soil = pd.read_csv('data/soil_quality_dataset.csv')
print(f"   Shape: {soil.shape}")
print(f"   Columns: {soil.columns.tolist()}")

# ── PREPARE FEATURES ─────────────────────────────────────────
print("\n2. Preparing features...")

# Encode Soil_Type (categorical → numbers)
soil_type_enc = LabelEncoder()
soil['Soil_Type_encoded'] = soil_type_enc.fit_transform(soil['Soil_Type'])

# Features and target
X = soil[['Soil_Type_encoded', 'pH', 'EC', 'Organic_Carbon',
          'Nitrogen', 'Phosphorus', 'Potassium',
          'Moisture', 'Temperature']]
y = soil['Soil_Quality']

# Encode target
quality_enc = LabelEncoder()
y_encoded = quality_enc.fit_transform(y)

print(f"   Features : {X.columns.tolist()}")
print(f"   Classes  : {list(quality_enc.classes_)}")
print(f"   Distribution:\n{soil['Soil_Quality'].value_counts()}")

# ── SPLIT DATA ───────────────────────────────────────────────
print("\n3. Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.2,
    random_state=42
)
print(f"   Train: {X_train.shape[0]} samples")
print(f"   Test : {X_test.shape[0]} samples")

# ── TRAIN MODEL ──────────────────────────────────────────────
print("\n4. Training Random Forest...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=8,
    random_state=42
)
model.fit(X_train, y_train)
print("   Done!")

# ── EVALUATE ─────────────────────────────────────────────────
print("\n5. Evaluating...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n   ✅ Accuracy: {accuracy*100:.2f}%")
print(f"\n   Classification Report:")
print(classification_report(y_test, y_pred,
      target_names=quality_enc.classes_))

# ── FEATURE IMPORTANCE ───────────────────────────────────────
print("\n6. Feature Importance:")
importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)
print(importance.to_string(index=False))

# ── SAVE MODEL ───────────────────────────────────────────────
print("\n7. Saving model...")
pickle.dump(model, open('models/soil_classifier.pkl', 'wb'))
pickle.dump(soil_type_enc, open('models/soil_type_encoder.pkl', 'wb'))
pickle.dump(quality_enc, open('models/soil_quality_encoder.pkl', 'wb'))
print("   ✅ Saved: models/soil_classifier.pkl")
print("   ✅ Saved: models/soil_type_encoder.pkl")
print("   ✅ Saved: models/soil_quality_encoder.pkl")

# ── TEST PREDICTION ──────────────────────────────────────────
print("\n8. Test prediction:")
# Clay soil, pH 6.5, typical Maharashtra values
sample_soil_type = soil_type_enc.transform(['Clay'])[0]
sample = np.array([[sample_soil_type, 6.5, 1.2, 1.0, 200, 40, 300, 25, 24]])

pred = model.predict(sample)[0]
pred_proba = model.predict_proba(sample)[0]
pred_label = quality_enc.inverse_transform([pred])[0]

print(f"   Input: Clay soil, pH=6.5, EC=1.2, OC=1.0")
print(f"          N=200, P=40, K=300, Moisture=25, Temp=24")
print(f"\n   Predicted Quality: {pred_label}")
print(f"   Confidence:")
for label, prob in zip(quality_enc.classes_, pred_proba):
    print(f"     {label:<10} {prob*100:.1f}%")

print("\n" + "="*60)
print("✅ MODEL 2 COMPLETE!")
print("="*60)