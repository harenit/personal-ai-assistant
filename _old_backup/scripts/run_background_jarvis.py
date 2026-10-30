"""
JARVIS Background Service & System Controller
Keeps the JARVIS AI Agent running continuously in the background on Windows.
"""
import sys
import time
import socket
import webbrowser
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def is_port_in_use(port: int = 8000) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_server():
    if is_port_in_use(8000):
        print("[JARVIS] Unified Server is already active on http://127.0.0.1:8000.")
        return None
    print("[JARVIS] Launching JARVIS background server process...")
    cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"]
    proc = subprocess.Popen(cmd, cwd=str(BASE_DIR))
    time.sleep(3)
    return proc

def main():
    print("==============================================================")
    print(" JARVIS — Background Assistant & Futuristic Arc Reactor HUD")
    print("==============================================================")
    print("Status: RUNNING IN BACKGROUND")
    print("Endpoint: http://127.0.0.1:8000")
    print("Wake Word: 'Hey JARVIS' (Active)")
    print("Global Hotkey: Ctrl + Space (Active in Web HUD)")
    print("Press Ctrl + C in this terminal to stop.")
    print("==============================================================")

    proc = start_server()
    webbrowser.open("http://127.0.0.1:8000")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[JARVIS] Shutting down background service...")
        if proc:
            proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
