"""
debug_test.py - Kisan Saathi sanity check (no live API calls)
Run: .venv\Scripts\python.exe debug_test.py
"""
import sys, json, traceback
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"
results = []

def check(label, fn):
    try:
        val = fn()
        print(f"{PASS}  {label}")
        if val not in (None, True, False, ""):
            print(f"       => {str(val)[:120]}")
        results.append((label, True, None))
        return val
    except Exception as e:
        print(f"{FAIL}  {label}")
        print(f"       => {type(e).__name__}: {e}")
        results.append((label, False, str(e)))
        return None

print("=" * 60)
print("  Kisan Saathi - Debug Check")
print("=" * 60)

# ── 1. Model files ────────────────────────────────────────────
print("\n[1] Model Files")
MODEL_DIR = Path(__file__).parent / "models"
for m in ["crop_recommender.pkl","crop_label_encoder.pkl",
          "soil_classifier.pkl","soil_type_encoder.pkl",
          "soil_quality_encoder.pkl","price_forecaster.pkl",
          "weather_patterns.pkl"]:
    check(f"{m}", lambda m=m: (MODEL_DIR/m).exists()
          or (_ for _ in ()).throw(FileNotFoundError(f"Missing: {m}")))

# ── 2. Agent loading ──────────────────────────────────────────
print("\n[2] Agent Loading")
import FarmerAgent as FA
agent = check("load_agent()", FA.load_agent)
if agent is None:
    print(f"\n{FAIL} Cannot continue - agent failed to load.")
    sys.exit(1)

farmer = FA.FarmerProfile(name="TestFarmer", district="Pune",
                          soil_type="Clay", farm_size=2.0, soil_ph=6.5)

# ── 3. ML Tools ───────────────────────────────────────────────
print("\n[3] ML Tools")
crops  = check("recommend_crops()", lambda: agent.recommend_crops(farmer))
soil   = check("classify_soil()",   lambda: agent.classify_soil(farmer))
prices = check("price_forecasts()", lambda: agent.price_forecasts())
wx     = check("weather_for(Pune)", lambda: agent.weather_for("Pune"))

if crops:  print(f"       Top crop: {crops[0]['name']} ({crops[0]['pct']}%)")
if soil:   print(f"       Soil: {soil['quality']} quality, pH {soil['ph']}")
if prices: print(f"       Prices: {prices}")
if wx:     print(f"       Weather: {wx[:2]}")

# ── 4. Fallback responses (no API) ────────────────────────────
print("\n[4] Fallback Responses (offline mode)")

# Temporarily disable Gemini and Groq so we can test the fallback path directly
original_gemini = FA._call_gemini
original_groq = FA._call_groq
def mock_api(prompt):
    raise RuntimeError("Simulated API unavailable")
FA._call_gemini = mock_api
FA._call_groq = mock_api

test_cases = [
    ("Which crop should I grow this kharif?",   "recommend_crops"),
    ("How is the weather in Pune this monsoon?", "weather_lookup"),
    ("What is the onion price at mandi?",        "price_forecast"),
    ("My soil pH is low, what to do?",           "classify_soil"),
    ("What fertiliser is good for cotton?",      "recommend_crops"),
]
for q, expected_tool in test_cases:
    def run(q=q, t=expected_tool):
        ans, src = agent.answer(q, farmer=farmer)
        assert src == "fallback", f"Expected fallback, got '{src}'"
        assert len(ans) > 30,    f"Answer too short ({len(ans)} chars)"
        assert "unable to connect" not in ans.lower(), "Old error message still present!"
        return f"[{src}] {ans[:100]}..."
    check(f'"{q[:45]}"', run)

FA._call_gemini = original_gemini  # restore
FA._call_groq = original_groq


# ── 5. Config check ───────────────────────────────────────────
print("\n[5] Configuration")
check(f"Model = {FA._GEMINI_MODEL}", lambda: FA._GEMINI_MODEL == "gemini-2.0-flash")
check(f"{len(FA._GEMINI_API_KEYS)} API keys configured",
      lambda: len(FA._GEMINI_API_KEYS) >= 4)

# Quick key status (no retries - just check HTTP status)
import urllib.request, urllib.error
print(f"\n[6] API Key Status (live ping - expect 429 if quota exhausted)")
for i, key in enumerate(FA._GEMINI_API_KEYS):
    def ping(k=key, idx=i):
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{FA._GEMINI_MODEL}:generateContent?key={k}")
        import json as _json
        body = _json.dumps({"contents":[{"parts":[{"text":"Hi"}]}],
                            "generationConfig":{"maxOutputTokens":5}}).encode()
        req = urllib.request.Request(url, data=body,
              headers={"Content-Type":"application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return f"HTTP 200 - LIVE! ({k[:12]}...)"
        except urllib.error.HTTPError as e:
            body_b = e.read().decode("utf-8", errors="replace")
            try:
                err = json.loads(body_b)["error"]
                code, msg = err["code"], err["message"][:50]
            except Exception:
                code, msg = e.code, str(e)
            status = "QUOTA EXHAUSTED (daily)" if code == 429 else f"ERROR {code}"
            return f"{status}: {msg}"
        except Exception as ex:
            return f"NETWORK ERROR: {ex}"
    result = ping()
    icon = "OK " if "200" in result else "429" if "429" in result else "ERR"
    print(f"   [{icon}] Key {i+1} ({key[:10]}...): {result}")

# ── Summary ───────────────────────────────────────────────────
print("\n" + "=" * 60)
passed = sum(1 for _,ok,_ in results if ok)
failed = sum(1 for _,ok,_ in results if not ok)
print(f"  Results: {passed} passed  |  {failed} failed  |  {len(results)} total")
if failed:
    print("\n  FAILED:")
    for label, ok, err in results:
        if not ok:
            print(f"    - {label}: {err}")
else:
    print("  All core systems operational.")
    if any("200" in ping(k) for k in FA._GEMINI_API_KEYS):
        print("  Gemini API: LIVE")
    else:
        print("  Gemini API: Quota exhausted - fallback mode active.")
print("=" * 60)
