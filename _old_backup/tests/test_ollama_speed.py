import requests
import time
import json
from backend.tools.registry import tool_registry

print("1. Testing basic prompt to Ollama...")
t0 = time.time()
r = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3.1:8b",
        "messages": [{"role": "user", "content": "Hello! Give me a one sentence greeting."}],
        "stream": False
    },
    timeout=60
)
print("Basic response time:", round(time.time() - t0, 2), "s")
print("Response:", r.json()["message"]["content"])

print("\n2. Testing with tools schema...")
tools = tool_registry.get_openai_tools()
print(f"Total tools count: {len(tools)}")
t1 = time.time()
r2 = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3.1:8b",
        "messages": [{"role": "user", "content": "Do I have any assignments due this week?"}],
        "tools": tools,
        "stream": False
    },
    timeout=180
)
print("Tools response time:", round(time.time() - t1, 2), "s")
print("Response keys:", r2.json()["message"].keys())
if "tool_calls" in r2.json()["message"]:
    print("Tool calls:", r2.json()["message"]["tool_calls"])
else:
    print("Content:", r2.json()["message"]["content"])
