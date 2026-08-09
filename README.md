# 🌾 Kisan Saathi — AI Farming Advisor

**Kisan Saathi** is a Streamlit-based agricultural advisory application designed around farming scenarios relevant to Maharashtra, India.

It combines **locally trained machine-learning models** with an **LLM-based advisory layer** to turn farm information and model outputs into simple, contextual recommendations.

The system currently provides:

* 🌱 Crop recommendations
* 🧪 Soil-quality classification
* 📈 Mandi price information and forecasting
* 🌦️ Historical weather-pattern lookup
* 💬 Natural-language agricultural advice
* 📴 Rule-based fallback when an LLM API is unavailable

> **Note:** This is a project prototype. Its recommendations are intended for experimentation and demonstration, not as a substitute for professional agricultural, financial, or weather advice.

---

## 🧠 How It Works

Kisan Saathi uses a hybrid architecture in which machine-learning models provide structured agricultural signals and an advisory layer turns those signals into farmer-facing responses.

```text
                         Farmer
                           │
                           ▼
                  Streamlit Dashboard
                           │
                           ▼
                     Farmer Agent
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
       Crop Model     Soil Model    Price / Weather
       XGBoost        Random Forest      Models
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                   Advisory Context
                           │
                  ┌────────┴────────┐
                  ▼                 ▼
             Groq / Gemini      Local / Rule
               LLM Layer          Fallback
                  │                 │
                  └────────┬────────┘
                           ▼
                   Farmer-Facing Advice
```

The application does not require the original training datasets during normal operation because the trained model artifacts are already included in the `models/` directory.

---

# 🤖 Machine Learning Components

| Component               | Model / Method                 | Purpose                                                                         |
| ----------------------- | ------------------------------ | ------------------------------------------------------------------------------- |
| Crop Recommendation     | XGBoost Classifier             | Recommends suitable crops using N, P, K, temperature, humidity, pH and rainfall |
| Soil Classification     | Random Forest Classifier       | Classifies soil quality using soil type and measured soil properties            |
| Mandi Price Forecasting | ARIMA                          | Generates a next-month price forecast for supported commodities                 |
| Weather Patterns        | Aggregated lookup model        | Provides historical temperature and rainfall patterns by location and month     |
| Advisory Generation     | Groq / Gemini / local fallback | Converts structured model outputs into natural-language advice                  |

### Crop Recommendation

The crop model uses:

* Nitrogen
* Phosphorus
* Potassium
* Temperature
* Humidity
* pH
* Rainfall

The XGBoost model produces crop probabilities, allowing the application to surface the highest-ranked recommendations.

### Soil Classification

The soil classifier uses:

* Soil type
* pH
* Electrical conductivity
* Organic carbon
* Nitrogen
* Phosphorus
* Potassium
* Moisture
* Temperature

A Random Forest classifier is used to predict the soil-quality class.

### Mandi Price Forecasting

The current price pipeline filters the agricultural price data for **Maharashtra** and works with **Onion** and **Potato**.

An ARIMA `(1,1,1)` model is fitted to monthly modal-price data. The generated artifact stores the historical series, latest price, next-month forecast and direction of the forecasted trend.

### Weather Patterns

The weather pipeline converts monthly weather records into lookup tables containing historical temperature and rainfall statistics by city and month.

---

# 🏗️ Repository Structure

```text
Farmer-Advisory-Agent/
│
├── app.py
│   └── Streamlit application and dashboard
│
├── farmer_agent.py
│   └── Core agent, ML integration, LLM calls and fallback logic
│
├── models/
│   ├── crop_recommender.pkl
│   ├── crop_label_encoder.pkl
│   ├── soil_classifier.pkl
│   ├── soil_type_encoder.pkl
│   ├── soil_quality_encoder.pkl
│   ├── price_forecaster.pkl
│   └── weather_patterns.pkl
│
├── training/
│   ├── README.md
│   ├── train_crop_model.py
│   ├── train_soil_model.py
│   ├── train_price_model.py
│   └── train_weather_model.py
│
├── tests/
│   ├── README.md
│   └── verify_models.py
│
├── data/
│   └── README.md
│
├── farmers_db.json
├── requirements.txt
├── .gitignore
└── README.md
```

### Important repository notes

* The trained `.pkl` artifacts are included in `models/`.
* The original training CSVs are **not included** because of their large file sizes.
* `data/README.md` documents the datasets required to retrain the models.
* `farmers_db.json` provides local persistence for farmer profiles.
* API credentials are **not stored in the repository**.

---

# 🚀 Running the Application

## 1. Clone the repository

```bash
git clone https://github.com/HarshDatar/Farmer-Advisory-Agent.git
cd Farmer-Advisory-Agent
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure optional LLM API keys

The application can use external LLM APIs for natural-language advisory generation.

Create a local `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
```

**Do not commit `.env` or API keys to GitHub.**

The repository intentionally does not contain a `.env` file or API credentials.

If no API key is available, the application can fall back to its local rule-based advisory logic.

## 5. Run the application

```bash
streamlit run app.py
```

Then open the local Streamlit address shown in the terminal, normally:

```text
http://localhost:8501
```

---

# 🧪 Verifying the Trained Models

The repository contains a model verification script:

```text
tests/verify_models.py
```

Run it from the project root:

```bash
python tests/verify_models.py
```

The script loads the serialized artifacts and performs sample predictions / lookups for:

* Crop recommendation
* Soil classification
* Price forecasting
* Weather patterns

The trained models must exist in `models/` for this verification step to work.

---

# 🔄 Retraining the Models

Retraining is **optional** for normal application use because pre-trained artifacts are already included.

The training scripts require the original datasets.

Because the datasets are too large to store directly in this repository, they must be obtained separately and placed inside:

```text
data/
```

See [`data/README.md`](data/README.md) for the expected files and suggested Kaggle search keywords.

The expected datasets are:

```text
data/
├── crop_recommendation.csv
├── soil_quality_dataset.csv
├── Agriculture_price_dataset.csv
└── weather_data.csv
```

After obtaining the required datasets, run the scripts from the **repository root**:

```bash
python training/train_crop_model.py
python training/train_soil_model.py
python training/train_price_model.py
python training/train_weather_model.py
```

The scripts write their resulting artifacts into:

```text
models/
```

> The training scripts currently use paths relative to the repository root, so run them from the root directory as shown above.

---

# 🔐 API and Offline Behaviour

The advisory layer can use external APIs when configured:

* **Groq** — primary LLM provider
* **Google Gemini** — alternative LLM provider

The project also contains local/fallback logic so that core functionality does not depend entirely on an external LLM service.

The machine-learning components remain locally available through the serialized models in `models/`.

This means the application can still perform its structured agricultural predictions even when an external LLM service is unavailable.

---

# 🛠️ Technology Stack

### Frontend

* Streamlit
* Custom CSS

### Machine Learning

* Python
* Scikit-learn
* XGBoost
* Statsmodels

### AI / LLM

* Groq API
* Google Gemini API
* GPT4All / local model support

### Data Processing

* Pandas
* NumPy

### Persistence

* JSON-based local farmer profile storage

### Model Serialization

* Python `pickle`

---

# 📌 Current Scope

The current prototype focuses on four main agricultural information flows:

1. **Crop selection**
2. **Soil-quality assessment**
3. **Mandi price forecasting**
4. **Weather-pattern lookup**

These outputs are combined with farmer information and user questions to produce contextual advisory responses.

The current implementation is primarily oriented toward **Maharashtra-focused use cases** and should not be interpreted as a generalized agricultural recommendation system for every region or crop.

---

# 🔮 Future Improvements

Potential future work includes:

* More Maharashtra districts and regional datasets
* More crop-specific recommendations
* Live weather API integration
* Live mandi-price data instead of stored forecasts
* Better uncertainty/calibration for model predictions
* Database-backed farmer profiles
* Multilingual Marathi/Hindi advisory responses
* More robust automated testing
* Containerized deployment
* Improved retrieval of agricultural domain knowledge
* Better monitoring and evaluation of advisory quality

---

# ⚠️ Limitations

This project has several important limitations:

* Training datasets are not included in the repository.
* Price forecasts are based on the available historical dataset rather than a live mandi feed.
* Weather information is based on stored historical patterns rather than a real-time weather service.
* Model predictions depend on the quality and distribution of their training data.
* LLM-generated advice can be incorrect and should be independently verified before making real-world farming decisions.
* The current system is a prototype and has not been validated as a production agricultural decision-support system.

---

# 👨‍💻 Project

**Kisan Saathi — Farmer Advisory Agent**

Built as an AI/ML project exploring the combination of traditional machine learning, local data processing, LLM orchestration and deterministic fallback systems for agricultural decision support.

**Repository:**
https://github.com/HarshDatar/Farmer-Advisory-Agent
