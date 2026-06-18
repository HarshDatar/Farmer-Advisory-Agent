"""
FarmerAgent.py - Kisan Saathi Backend
ML models for data + Gemini for advice generation.
"""
from __future__ import annotations
import sys
# Force UTF-8 output so Unicode prints safely on Windows
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import pickle
import threading
import urllib.error
import urllib.request
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).resolve().parent
MODEL_DIR   = PROJECT_DIR / "models"
KB_DIR      = PROJECT_DIR / "knowledge_base"

# Load .env file manually if it exists in the project directory
_env_file = PROJECT_DIR / ".env"
if _env_file.exists():
    try:
        with _env_file.open("r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#"):
                    _parts = _line.split("=", 1)
                    if len(_parts) == 2:
                        _k = _parts[0].strip()
                        _v = _parts[1].strip().strip("'\"")
                        os.environ[_k] = _v
    except Exception:
        pass


# ── HARDCODED API KEYS — farmers never see these ──────────────
# Leave this list empty. Set your key in the .env file instead:
#   GEMINI_API_KEY=your_key_here
_GEMINI_API_KEYS  = []
_GEMINI_MODEL     = "gemini-2.0-flash"

# ── Maharashtra districts in weather data ─────────────────────
DISTRICTS = ["Pune", "Nagpur", "Nashik", "Kohlapur", "Satara"]

# ── Crops relevant to Maharashtra ────────────────────────────
MH_CROPS = {
    "blackgram", "chickpea", "cotton", "grapes", "maize",
    "mango", "mothbeans", "mungbean", "orange", "pigeonpeas",
    "pomegranate", "rice", "wheat",
}

# ── Soil types the encoder knows ─────────────────────────────
KNOWN_SOIL_TYPES = ["Clay", "Sandy", "Loamy", "Silty", "Rocky"]

# ── Tool keywords ─────────────────────────────────────────────
TOOL_KEYWORDS = {
    "recommend_crops": [
        "crop", "grow", "plant", "cultivate", "kharif", "rabi",
        "season", "sow", "seed", "which crop", "best crop",
        "what to grow", "farming", "harvest", "sugarcane", "cotton",
    ],
    "classify_soil": [
        "soil", "quality", "fertile", "ph", "nitrogen", "organic",
        "land", "ground", "mitti", "soil health", "potassium",
    ],
    "price_forecast": [
        "price", "mandi", "sell", "market", "cost", "rate",
        "onion", "potato", "money", "selling", "buy", "rupee",
    ],
    "weather_lookup": [
        "weather", "rain", "temperature", "climate", "rainfall",
        "humid", "wind", "cold", "hot", "monsoon", "barish",
    ],
}

# ── LLM system prompt ─────────────────────────────────────────
_SYSTEM = """You are Kisan Saathi, a warm and practical farming advisor for smallholder farmers in Maharashtra, India.
Speak like a knowledgeable neighbour — simple English, friendly, direct.
Rules:
- Never mention AI, models, confidence scores, tools or software.
- Give specific, actionable advice in 3-5 short sentences max.
- Use Indian farming terms naturally (kharif, rabi, mandi, bigha, etc.).
- If farm data is given, reference it specifically.
- End with one encouraging sentence."""


class AgentSetupError(RuntimeError):
    pass


# ── Pickle loader ─────────────────────────────────────────────
def _pkl(filename: str) -> Any:
    path = MODEL_DIR / filename
    if not path.exists():
        raise AgentSetupError(f"Model file missing: {path}. Run training scripts first.")
    with path.open("rb") as f:
        return pickle.load(f)


def _crop_name(raw: Any) -> str:
    return str(raw).replace("_", " ").strip().title()


# ── Groq API call (primary - no daily limits) ────────────────
_GROQ_MODEL = "llama-3.3-70b-versatile"

def _call_groq(prompt: str) -> str | None:
    """Call Groq API (OpenAI-compatible). Raises on failure."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("No GROQ_API_KEY set")
    url = "https://api.groq.com/openai/v1/chat/completions"
    body = json.dumps({
        "model": _GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 220,
        "temperature": 0.65,
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return str(data["choices"][0]["message"]["content"]).strip()
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = str(e.reason)
        raise RuntimeError(f"Groq HTTP {e.code}: {err_body[:200]}")


# ── Gemini API call (backup) ──────────────────────────────────
_RETRY_ATTEMPTS = 2          # retries per key on 429 / 5xx
_RETRY_BASE_DELAY = 2.0      # seconds; doubles each retry (2 -> 4)

def _call_gemini(prompt: str) -> str | None:
    import time

    # 1. Collect all available keys from environment and fallbacks
    keys = []
    for var in ["GEMINI_API_KEY", "GEMINI_API_KEY_1", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"]:
        val = os.environ.get(var)
        if val and val not in keys:
            keys.append(val)

    # Add hardcoded fallbacks
    for key in _GEMINI_API_KEYS:
        if key and key not in keys and not key.startswith("REPLACE_"):
            keys.append(key)

    errors = []
    body_bytes = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 220,
            "temperature": 0.65,
        },
    }).encode("utf-8")

    # 2. Iterate through each key, retrying on transient rate-limit errors
    for i, api_key in enumerate(keys):
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{_GEMINI_MODEL}:generateContent?key={api_key}"
        )
        delay = _RETRY_BASE_DELAY
        for attempt in range(1, _RETRY_ATTEMPTS + 2):  # attempts: 1, 2, 3
            req = urllib.request.Request(
                url, data=body_bytes,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                return str(data["candidates"][0]["content"]["parts"][0]["text"]).strip()
            except urllib.error.HTTPError as e:
                status_code = e.code
                try:
                    err_body = e.read().decode("utf-8")
                except Exception:
                    err_body = e.reason
                # Retry on 429 (rate limit) or 5xx (server error)
                if status_code in (429, 500, 502, 503) and attempt <= _RETRY_ATTEMPTS:
                    print(
                        f"[Gemini API] Key {i+1}, attempt {attempt} -> HTTP {status_code}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= 2  # exponential back-off
                    continue
                # Non-retryable or retries exhausted - record and move to next key
                errors.append(f"Key {i+1} ({api_key[:8]}...): {err_body}")
                print(f"[Gemini API Warning] Key {i+1} failed (HTTP {status_code}). Moving to next key.")
                break
            except Exception as e:
                err_msg = str(e)
                errors.append(f"Key {i+1} ({api_key[:8]}...): {err_msg}")
                print(f"[Gemini API Warning] Key {i+1} failed. Error: {err_msg}")
                break

    # Raise error if all keys failed
    raise RuntimeError("All configured API keys failed to connect or authenticate.\n" + "\n".join(errors))


# ── Local LLM loader ──────────────────────────────────────────
def _find_local_llm() -> Any | None:
    search = [
        MODEL_DIR,
        Path.home() / "AppData" / "Local" / "nomic.ai" / "GPT4All",
        Path.home() / ".cache" / "gpt4all",
    ]
    found: list[Path] = []
    for d in search:
        try:
            if d.exists():
                found.extend(d.glob("*.gguf"))
        except OSError:
            pass
    if not found:
        return None
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    chosen = found[0]
    for token in ("llama-3.2-3b", "phi-3-mini", "phi-2", "instruct"):
        for p in found:
            if token in p.name.lower():
                chosen = p
                break
    try:
        from gpt4all import GPT4All
        return GPT4All(
            model_name=chosen.name,
            model_path=str(chosen.parent),
            allow_download=False,
            n_threads=4,
            n_ctx=768,
            verbose=False,
        )
    except Exception:
        return None


# ── Farmer Profile ────────────────────────────────────────────
@dataclass
class FarmerProfile:
    name:      str   = "Farmer"
    district:  str   = "Pune"
    soil_type: str   = "Clay"
    farm_size: float = 2.0
    soil_ph:   float = 6.5

    def summary(self) -> str:
        return (
            f"Farmer {self.name} from {self.district}, "
            f"{self.farm_size} acre {self.soil_type} soil at pH {self.soil_ph}."
        )


# ── The Agent ─────────────────────────────────────────────────
@dataclass
class FarmerAgent:
    crop_model:           Any
    crop_le:              Any
    soil_model:           Any
    soil_type_enc:        Any
    soil_quality_enc:     Any
    price_data:           dict
    weather_data:         dict
    local_llm:            Any | None = None
    _llm_loading:         bool = field(default=False, repr=False)
    _memory:              list = field(default_factory=list, repr=False)
    last_source:          str = "none"
    last_error:           str = ""

    # ── Memory ─────────────────────────────────────────────
    def _remember(self, role: str, text: str) -> None:
        self._memory.append({"role": role, "text": text[:200]})
        if len(self._memory) > 10:
            self._memory = self._memory[-10:]

    def memory_context(self) -> str:
        if len(self._memory) < 2:
            return ""
        lines = ["Previous conversation:"]
        for m in self._memory[-4:]:
            lines.append(f"{m['role']}: {m['text']}")
        return "\n".join(lines)

    def clear_memory(self) -> None:
        self._memory.clear()

    # ── Start local LLM in background ──────────────────────
    def start_local_async(self) -> None:
        if self.local_llm is not None or self._llm_loading:
            return
        def _load():
            self._llm_loading = True
            try:
                self.local_llm = _find_local_llm()
            except Exception:
                self.local_llm = None
            finally:
                self._llm_loading = False
        threading.Thread(target=_load, daemon=True).start()

    # ── Status label ────────────────────────────────────────
    def status(self) -> dict:
        if self.local_llm:
            return {"label": "Local AI + Groq", "color": "green", "ok": True}
        if self._llm_loading:
            return {"label": "Groq AI (local loading...)", "color": "orange", "ok": True}
        groq_key = os.environ.get("GROQ_API_KEY", "")
        if groq_key:
            return {"label": "Groq AI (Llama 3.3)", "color": "green", "ok": True}
        return {"label": "Gemini AI", "color": "green", "ok": True}

    # ── ML Tools ────────────────────────────────────────────
    def recommend_crops(self, farmer: FarmerProfile | None = None) -> list[dict]:
        temp  = 28.0
        ph    = farmer.soil_ph if farmer else 7.5
        sample = pd.DataFrame(
            [[50, 40, 20, temp, 65, ph, 150]],
            columns=["N","P","K","temperature","humidity","ph","rainfall"],
        )
        probs   = self.crop_model.predict_proba(sample)[0]
        classes = self.crop_le.classes_
        mh_idx  = [i for i, c in enumerate(classes) if str(c).lower() in MH_CROPS]
        ranked  = sorted(mh_idx or range(len(probs)), key=lambda i: probs[i], reverse=True)
        return [
            {"name": _crop_name(classes[i]), "pct": round(float(probs[i]) * 100, 1)}
            for i in ranked[:3]
        ]

    def classify_soil(self, farmer: FarmerProfile | None = None) -> dict:
        soil_type = farmer.soil_type if farmer else "Clay"
        ph        = farmer.soil_ph   if farmer else 6.5
        known     = list(self.soil_type_enc.classes_)
        if soil_type not in known:
            soil_type = known[0]
        enc = self.soil_type_enc.transform([soil_type])[0]
        sample = pd.DataFrame(
            [[enc, ph, 1.2, 1.0, 200, 40, 300, 25, 24]],
            columns=["Soil_Type_encoded","pH","EC","Organic_Carbon",
                     "Nitrogen","Phosphorus","Potassium","Moisture","Temperature"],
        )
        pred    = self.soil_model.predict(sample)[0]
        probs   = self.soil_model.predict_proba(sample)[0]
        quality = str(self.soil_quality_enc.inverse_transform([pred])[0]).title()
        return {
            "quality":    quality,
            "confidence": round(float(max(probs)) * 100, 1),
            "soil_type":  soil_type,
            "ph":         ph,
        }

    def price_forecasts(self) -> list[dict]:
        rows = []
        for crop in ["Onion", "Potato"]:
            d = self.price_data.get(crop)
            if d:
                rows.append({
                    "crop":     crop,
                    "current":  round(float(d["last_price"])),
                    "forecast": round(float(d["next_month_forecast"])),
                    "trend":    str(d.get("trend", "flat")).lower(),
                })
        return rows

    def weather_for(self, district: str = "Pune",
                    months: tuple = (6, 7, 8, 9)) -> list[dict]:
        month_names = {
            1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
            7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec",
        }
        temp_data = self.weather_data.get("temperature", {})
        results = []
        for m in months:
            entry = temp_data.get((district, m))
            if not entry and district != "Pune":
                entry = temp_data.get(("Pune", m))
            if entry:
                results.append({
                    "month": month_names[m],
                    "temp":  round(float(entry["mean"]), 1),
                })
        return results

    # ── Tool selector ────────────────────────────────────────
    def select_tools(self, query: str) -> list[str]:
        q = query.lower()
        selected = [t for t, kws in TOOL_KEYWORDS.items() if any(kw in q for kw in kws)]
        return selected or ["recommend_crops"]

    def tools_labels(self, query: str) -> list[str]:
        m = {
            "recommend_crops": "Crop Model",
            "classify_soil":   "Soil Model",
            "price_forecast":  "Price Forecast",
            "weather_lookup":  "Weather Data",
        }
        return [m[t] for t in self.select_tools(query)]

    # ── Build ML context ─────────────────────────────────────
    def _build_context(self, query: str, farmer: FarmerProfile | None) -> str:
        selected = self.select_tools(query)
        parts = []

        if farmer:
            parts.append(farmer.summary())

        if "recommend_crops" in selected:
            crops = self.recommend_crops(farmer)
            parts.append("Best crops: " + ", ".join(c["name"] for c in crops) + ".")

        if "classify_soil" in selected:
            s = self.classify_soil(farmer)
            parts.append(f"Soil: {s['quality']} quality, {s['soil_type']}, pH {s['ph']}.")

        if "price_forecast" in selected:
            for row in self.price_forecasts():
                trend = "rising" if row["trend"] == "up" else "falling"
                parts.append(
                    f"{row['crop']} price: Rs.{row['current']} now, "
                    f"Rs.{row['forecast']} next month ({trend})."
                )

        if "weather_lookup" in selected:
            district = farmer.district if farmer else "Pune"
            weather  = self.weather_for(district)
            if weather:
                bits = ", ".join(f"{w['month']} {w['temp']}°C" for w in weather)
                parts.append(f"Weather in {district}: {bits}.")

        return "\n".join(parts)

    # ── Generate with local LLM ──────────────────────────────
    def _gen_local(self, prompt: str) -> str | None:
        if not self.local_llm:
            return None
        try:
            with self.local_llm.chat_session():
                raw = self.local_llm.generate(prompt=prompt, max_tokens=180, temp=0.65)
            for tag in ["<|assistant|>","<|end|>","<|im_end|>","Farmer:","Kisan Saathi:"]:
                if tag in raw:
                    raw = raw.split(tag)[0]
            return raw.strip() or None
        except Exception:
            return None

    # ── Smart fallback when no LLM is available ────────────
    def _fallback(self, query: str, farmer: FarmerProfile | None) -> str:
        """Generate a helpful, natural-sounding response using only ML model outputs."""
        selected = self.select_tools(query)
        parts = []

        if "price_forecast" in selected:
            rows = self.price_forecasts()
            if rows:
                advice_bits = []
                for r in rows:
                    direction = "likely to rise" if r["trend"] == "up" else "expected to fall"
                    advice_bits.append(
                        f"{r['crop']} is at Rs.{r['current']}/quintal now and {direction} "
                        f"to around Rs.{r['forecast']} next month"
                    )
                parts.append(
                    "Regarding mandi prices - " + "; ".join(advice_bits) + ". "
                    "Check local mandi arrivals before deciding when to sell, "
                    "as prices can vary by 10-15% between districts."
                )

        if "classify_soil" in selected:
            s = self.classify_soil(farmer)
            quality = s["quality"].lower()
            ph_tip = (
                "Your pH is in the ideal range - most crops will do well."
                if 6.0 <= s["ph"] <= 7.5
                else ("Consider adding lime to raise pH before the next season."
                      if s["ph"] < 6.0
                      else "Add gypsum or organic matter to bring pH down gradually.")
            )
            parts.append(
                f"Your {s['soil_type']} soil is showing {quality} health at pH {s['ph']}. "
                + ph_tip
                + " Adding well-composted FYM each season will steadily improve soil structure."
            )

        if "weather_lookup" in selected:
            district = farmer.district if farmer else "Pune"
            weather  = self.weather_for(district)
            if weather:
                bits = ", ".join(f"{w['month']} {w['temp']}°C" for w in weather)
                hottest = max(weather, key=lambda w: w["temp"])
                parts.append(
                    f"Weather in {district} during the monsoon months: {bits}. "
                    f"{hottest['month']} tends to be the hottest - ensure your crops "
                    "have enough moisture during this period. "
                    "Sow after the first strong rains when the soil is well-wetted."
                )

        if "recommend_crops" in selected or not parts:
            crops = self.recommend_crops(farmer)
            ph    = farmer.soil_ph if farmer else 7.0
            dist  = farmer.district if farmer else "your area"
            top   = crops[0]["name"]
            alt1  = crops[1]["name"] if len(crops) > 1 else ""
            alt2  = crops[2]["name"] if len(crops) > 2 else ""
            alts  = f"{alt1} and {alt2}" if alt1 and alt2 else (alt1 or "")
            ph_note = (
                "" if 6.0 <= ph <= 7.5
                else " - though correcting your soil pH first will give better yields"
            )
            parts.append(
                f"Based on your soil and local conditions in {dist}, "
                f"{top} looks like the strongest choice for you right now{ph_note}. "
                + (f"{alts} are solid alternatives worth considering. " if alts else "")
                + "Discuss with your local agriculture officer for seed variety recommendations."
            )

        response = " ".join(parts)
        return response + " Keep at it - every good season starts with a good plan!"

    # ── Main answer ──────────────────────────────────────────
    def answer(self, query: str, farmer: FarmerProfile | None = None) -> tuple[str, str]:
        """Returns (answer, source) where source = gemini / local / fallback."""
        query = query.strip()
        if not query:
            return "Please ask me about crops, soil, weather, or mandi prices.", "none"

        self._remember("Farmer", query)
        context = self._build_context(query, farmer)
        memory  = self.memory_context()

        prompt = "\n".join(filter(None, [
            _SYSTEM, "",
            memory if memory else None,
            "Farm data:",
            context, "",
            f"Farmer asks: {query}",
            "Kisan Saathi:",
        ]))

        response: str | None = None

        # 1. Try Groq (primary - fast, no daily limits)
        try:
            response = _call_groq(prompt)
            self.last_source = "groq"
            self.last_error = ""
        except Exception as e:
            print(f"[Kisan Saathi] Groq unavailable: {type(e).__name__}: {str(e)[:80]}")

        # 2. Try Gemini (backup)
        if response is None:
            try:
                response = _call_gemini(prompt)
                self.last_source = "gemini"
                self.last_error = ""
            except Exception as e:
                self.last_error = str(e)
                print(f"[Kisan Saathi] Gemini unavailable: {type(e).__name__}")

        # 3. Try local LLM
        if response is None and self.local_llm:
            response = self._gen_local(prompt)
            if response:
                self.last_source = "local"
                self.last_error = ""

        # 4. Smart ML-based fallback -- always gives a useful answer
        if response is None:
            response = self._fallback(query, farmer)
            self.last_source = "fallback"

        # Clean any leftover LLM artefacts
        for tag in ["<|assistant|>", "<|end|>", "Kisan Saathi:", "Assistant:"]:
            if tag in response:
                response = response.split(tag)[0].strip()

        self._remember("Kisan Saathi", response)
        return response, self.last_source



# ── Factory ───────────────────────────────────────────────────
def load_agent() -> FarmerAgent:
    agent = FarmerAgent(
        crop_model=       _pkl("crop_recommender.pkl"),
        crop_le=          _pkl("crop_label_encoder.pkl"),
        soil_model=       _pkl("soil_classifier.pkl"),
        soil_type_enc=    _pkl("soil_type_encoder.pkl"),
        soil_quality_enc= _pkl("soil_quality_encoder.pkl"),
        price_data=       _pkl("price_forecaster.pkl"),
        weather_data=     _pkl("weather_patterns.pkl"),
    )
    return agent


if __name__ == "__main__":
    print("Loading Kisan Saathi...")
    ag = load_agent()
    fp = FarmerProfile(name="Ramesh", district="Nashik", soil_type="Clay")
    print("Ready. Type 'quit' to exit.\n")
    while True:
        q = input("You: ").strip()
        if q.lower() in {"quit","exit"}:
            break
        ans, src = ag.answer(q, farmer=fp)
        print(f"[{src}] Kisan Saathi: {ans}\n")