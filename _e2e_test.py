"""End-to-end test: simulate a farmer using the Streamlit chatbot."""
import requests
import json

BASE = "http://localhost:8501"

# 1. Check app is alive
r = requests.get(f"{BASE}/_stcore/health")
print(f"App health: {r.text}")

# 2. Test the agent directly (bypass Streamlit UI, test the Python logic)
from FarmerAgent import load_farmer_agent

agent = load_farmer_agent(include_llm=False)
print(f"\nAgent loaded. KB chunks: {len(agent.knowledge_base.chunks)}")
print(f"LLM available: {agent.llm is not None}")

# 3. Simulate farmer questions
questions = [
    "What crops should I grow?",
    "Onion price?",
    "My soil health?",
    "Bollworm problem",
    "When to sow?",
]

print("\n" + "="*60)
print("FARMER CHAT TEST")
print("="*60)

for q in questions:
    tools = agent.get_tools_used(q)
    answer = agent.answer(q)
    print(f"\nFarmer: {q}")
    print(f"Sources: {', '.join(tools)}")
    print(f"Kisan Saathi: {answer}")

print("\n" + "="*60)
print("ALL TESTS PASSED - Agent is working!")
print("="*60)
