import requests
import time
import sys

# Test 5 LMS tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_assignments",
            "description": "Get assignments due in the next N days (default 7).",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days ahead (default 7)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_assignments",
            "description": "Get all assignments optionally filtered by course_id or status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {"type": "string"},
                    "status": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_exams",
            "description": "Get scheduled exams optionally filtered by course_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Launch an authorized Windows application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_name": {"type": "string"}
                },
                "required": ["application_name"]
            }
        }
    }
]

print("Sending chat request with 4 concise tools...", flush=True)
t0 = time.time()
r = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3.1:8b",
        "messages": [
            {"role": "system", "content": "You are JARVIS, an autonomous student assistant. Use tools when needed."},
            {"role": "user", "content": "Do I have any assignments due this week?"}
        ],
        "tools": tools,
        "stream": False
    },
    timeout=60
)
print("Response time:", round(time.time() - t0, 2), "s", flush=True)
msg = r.json().get("message", {})
print("Tool calls:", msg.get("tool_calls"), flush=True)
print("Content:", msg.get("content"), flush=True)
