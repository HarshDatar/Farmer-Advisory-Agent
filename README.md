# 🌾 Kisan Saathi (किसान साथी) — AI Farming Advisor
Kisan Saathi is a responsive, web-based dashboard and intelligent farming advisor tailored for smallholder farmers in Maharashtra, India. It combines local machine learning models with Large Language Model (LLM) orchestration to deliver contextual, actionable, and warm agricultural advice.
The application operates with a **resilient hybrid backend**: it uses state-of-the-art APIs (Groq and Gemini) when online, automatically checks for local GGUF models, and falls back on built-in heuristic engines when fully offline.
---
## 🔑 API Keys & Environment Configuration
To use the AI conversational features, you need to provide your own API keys. 
### 1. Set Up Your Environment File
1. Copy the template environment file:
   ```bash
   # On Windows:
   copy .env.example .env
   # On Mac/Linux:
   cp .env.example .env
Open the newly created .env file in a text editor.
2. Add Your API Keys
Fill in the following variables inside .env:

env


GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
Where to get a GROQ API key (Primary): Sign up and create a free key at the Groq Console. (Highly recommended as it provides high rate limits for development).
Where to get a Gemini API key (Backup): Create a free key at Google AI Studio.
🌾 Smart Offline Fallback Mode
If you do not have API keys (or if your internet connection is down), the app will still run perfectly.

Kisan Saathi detects the lack of keys and automatically activates Heuristic Fallback Mode. In this mode, the core ML models will still recommend crops, classify soil, and forecast mandi prices, and our built-in rules engine will generate natural agricultural advice from those outputs locally.

📁 Project Structure
text


farmer_agent/
├── app.py                  # Streamlit frontend, customized styling & dashboard
├── FarmerAgent.py          # Core AI agent & backend orchestrator (ML tools + APIs)
├── Crop_model.py           # Training pipeline for the XGBoost Crop Recommender
├── train_soil_model.py     # Training pipeline for the RF Soil Classifier
├── training_pricemodel.py  # Training pipeline for the ARIMA Price Forecaster
├── Train_Weather_Model.py  # Data aggregator for district weather trends
├── ModelsMerged.py         # Testing script to verify all ML models load & predict
├── data/                   # Raw training datasets (.csv)
├── models/                 # Serialized model pickles (.pkl)
├── knowledge_base/         # Local files for domain knowledge lookup
├── requirements.txt        # Python library dependencies
├── .env.example            # Environment variables configuration template
└── farmers_db.json         # Local database storing registered farmer profiles
🚀 Setup & Installation
1. Clone the repository
bash


git clone <your-github-repo-url>
cd farmer_agent
2. Create and activate a virtual environment
bash


python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate
3. Install required packages
bash


pip install -r requirements.txt
4. Train the ML models
Before launching the application, you must train the machine learning models to generate the required .pkl files in the models/ folder:

bash


python Crop_model.py
python train_soil_model.py
python training_pricemodel.py
python Train_Weather_Model.py
(Optional) Verify that all models are successfully trained and matching target schemas:

bash


python ModelsMerged.py
5. Run the App
Start the Streamlit dashboard:

bash


streamlit run app.py
Open http://localhost:8501 in your browser.

🛠️ Built With
Frontend: Streamlit with customized CSS styling
Machine Learning: Scikit-learn, XGBoost, Statsmodels
LLM APIs: Groq & Google Gemini
Local LLMs: GPT4All
Data Wrangling: Pandas & NumPy


### Summary of Work Done:
- Added a dedicated, prominent **API Keys & Environment Configuration** section explaining how to copy [.env.example](file:///c:/Users/Admin/farmer_agent/.env.example) and populate the keys.
- Provided direct links to obtain free API credentials for Groq and Gemini.
- Clearly explained the **Smart Offline Fallback Mode** so users know they can evaluate the application even without setting up API keys.
