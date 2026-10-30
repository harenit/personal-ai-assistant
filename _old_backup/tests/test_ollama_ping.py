import requests
import time
import sys

print("Checking Ollama /api/tags...", flush=True)
try:
    r = requests.get("http://localhost:11434/api/tags", timeout=5)
    print("Tags status:", r.status_code, "Models:", [m["name"] for m in r.json().get("models", [])], flush=True)
except Exception as e:
    print("Error connecting to Ollama:", e, flush=True)
    sys.exit(1)

print("\nSending simple ping to llama3.1:8b...", flush=True)
t0 = time.time()
try:
    r = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.1:8b",
            "messages": [{"role": "user", "content": "Say 'ready' and nothing else."}],
            "stream": False
        },
        timeout=60
    )
    print("Ping response in", round(time.time() - t0, 2), "s:", r.json()["message"]["content"], flush=True)
except Exception as e:
    print("Error during chat ping:", e, flush=True)
