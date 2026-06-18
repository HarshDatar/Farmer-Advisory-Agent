import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

print("="*60)
print("MODEL 1: CROP RECOMMENDATION (XGBoost)")
print("="*60)

# ── LOAD DATA ────────────────────────────────────────────────
print("\n1. Loading data...")
crop = pd.read_csv('data/crop_recommendation.csv')
print(f"   Shape: {crop.shape}")

# ── PREPARE FEATURES ─────────────────────────────────────────
print("\n2. Preparing features...")
X = crop[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = crop['label']

# Encode labels (rice→0, maize→1 etc.)
le = LabelEncoder()
y_encoded = le.fit_transform(y)

print(f"   Features: {X.columns.tolist()}")
print(f"   Target classes: {list(le.classes_)}")

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
print("\n4. Training XGBoost... (takes ~30 seconds)")
model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric='mlogloss'
)
model.fit(X_train, y_train)
print("   Done!")

# ── EVALUATE ─────────────────────────────────────────────────
print("\n5. Evaluating...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n   ✅ Accuracy: {accuracy*100:.2f}%")
print(f"\n   Classification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# ── FEATURE IMPORTANCE ───────────────────────────────────────
print("\n6. Feature Importance:")
importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)
print(importance.to_string(index=False))

# ── SAVE MODEL ───────────────────────────────────────────────
print("\n7. Saving model...")
pickle.dump(model, open('models/crop_recommender.pkl', 'wb'))
pickle.dump(le, open('models/crop_label_encoder.pkl', 'wb'))
print("   ✅ Saved: models/crop_recommender.pkl")
print("   ✅ Saved: models/crop_label_encoder.pkl")

# ── TEST PREDICTION ──────────────────────────────────────────
print("\n8. Test prediction:")
sample = np.array([[50, 40, 50, 25, 70, 6.5, 100]])
pred_encoded = model.predict(sample)[0]
pred_proba = model.predict_proba(sample)[0]

top3_idx = pred_proba.argsort()[-3:][::-1]
top3_crops = le.classes_[top3_idx]
top3_conf = pred_proba[top3_idx]

print(f"   Input: N=50, P=40, K=50, Temp=25, Humidity=70, pH=6.5, Rainfall=100")
print(f"\n   Top 3 Recommendations:")
for i, (crop_name, conf) in enumerate(zip(top3_crops, top3_conf)):
    print(f"   {i+1}. {crop_name:<15} ({conf*100:.1f}% confidence)")

print("\n" + "="*60)
print("✅ MODEL 1 COMPLETE!")
print("="*60)