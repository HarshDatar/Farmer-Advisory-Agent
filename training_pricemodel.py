import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import pickle
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("FIXING PRICE FORECASTER")
print("="*60)

# Load and filter data
prices = pd.read_csv('data/Agriculture_price_dataset.csv')
mah = prices[prices['STATE'] == 'Maharashtra'].copy()
mah['Price Date'] = pd.to_datetime(mah['Price Date'])
mah = mah.sort_values('Price Date')

top_crops = ['Onion', 'Potato']

# Instead of saving ARIMA model object,
# save the FORECASTED VALUES + historical data
price_data = {}

for crop in top_crops:
    print(f"\nProcessing {crop}...")

    crop_data = mah[mah['Commodity'] == crop].copy()
    crop_data = crop_data.set_index('Price Date')['Modal_Price']
    crop_monthly = crop_data.resample('ME').mean().dropna()

    # Fit ARIMA
    model = ARIMA(crop_monthly, order=(1, 1, 1))
    result = model.fit()

    # Save forecast + historical (not the model object)
    next_month_forecast = float(result.forecast(steps=1).iloc[0])
    last_price = float(crop_monthly.iloc[-1])
    avg_price = float(crop_monthly.mean())

    price_data[crop] = {
        'last_price': last_price,
        'next_month_forecast': next_month_forecast,
        'avg_price': avg_price,
        'trend': 'up' if next_month_forecast > last_price else 'down',
        'historical': crop_monthly.tolist(),
        'dates': [str(d) for d in crop_monthly.index]
    }

    print(f"  Last price     : ₹{last_price:.2f}")
    print(f"  Next month     : ₹{next_month_forecast:.2f}")
    print(f"  Trend          : {price_data[crop]['trend']}")
    print(f"  ✅ Done")

# Save as simple dict (no ARIMA object)
pickle.dump(price_data, open('models/price_forecaster.pkl', 'wb'))
print(f"\n✅ Saved: models/price_forecaster.pkl")

# Verify it loads
loaded = pickle.load(open('models/price_forecaster.pkl', 'rb'))
print(f"\nVerification:")
for crop, data in loaded.items():
    print(f"  {crop}: ₹{data['next_month_forecast']:.2f} ({data['trend']})")

print("\n✅ Price model fixed!")