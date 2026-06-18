# 🌾 Kisan Saathi — AI Farming Advisor

A Streamlit-based AI farming advisory app for smallholder farmers in Maharashtra, India.
Built with ML models (crop recommendation, soil classification, price forecasting, weather lookup) + Gemini AI for natural language advice.

---

## 🚀 Setup & Run

### 1. Clone the repository
```bash
git clone <repo-url>
cd farmer_agent
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API Key
Copy the example env file and fill in your key:
```bash
copy .env.example .env       # Windows
# cp .env.example .env       # Mac/Linux
```
Then open `.env` and replace `your_gemini_api_key_here` with your actual key.

> **Get a free key:** https://aistudio.google.com/app/apikey

### 5. Run the app
```bash
.venv\Scripts\streamlit.exe run app.py    # Windows
# streamlit run app.py                    # Mac/Linux
```

Open your browser at **http://localhost:8501**

---

## 🔑 API Key — Important Notes

- The app works **even without a key** using its built-in ML-based fallback
- The fallback gives real answers using crop/soil/price/weather models
- With a valid Gemini key, answers are richer and more conversational
- Free tier gives **1,500 requests/day** — sufficient for evaluation

---

## 📁 Project Structure

```
farmer_agent/
├── app.py                  # Streamlit frontend
├── FarmerAgent.py          # Core agent: ML tools + Gemini integration
├── models/                 # Pre-trained ML models (.pkl files)
├── knowledge_base/         # Domain knowledge files
├── data/                   # Training datasets
├── requirements.txt        # Python dependencies
├── .env.example            # API key template (copy to .env)
└── .gitignore
```

---

## 🌱 Features

- **Crop Recommendation** — XGBoost model trained on soil + weather data
- **Soil Classification** — Classifies soil quality and gives pH advice
- **Price Forecasting** — Mandi price trends for Onion and Potato
- **Weather Lookup** — District-wise monsoon temperature data
- **Gemini AI Advisor** — Natural language farming advice via Gemini 2.0 Flash
- **Smart Offline Fallback** — Works fully without internet/API using ML outputs
- **Multi-farmer Support** — Login/profile system with per-farmer chat history

---

## 🛠️ Requirements

- Python 3.10+
- See `requirements.txt` for all packages
