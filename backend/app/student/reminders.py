"""Student productivity module: Timers, Reminders, and Study Notes.

Runs a background thread that monitors active timers and rings/announces when time is up.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

_DATA_FILE = settings.data_dir / "reminders.json"

def _get_notes_dir() -> Path:
    env_dir = os.environ.get("AURA_NOTES_DIR")
    if env_dir:
        p = Path(env_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p
    target = Path.home() / "Documents" / "AURA Notes"
    try:
        target.mkdir(parents=True, exist_ok=True)
        return target
    except OSError:
        fallback = Path.cwd() / "generated_notes"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback

_lock = threading.Lock()
_active_reminders: list[dict] = []
_thread_started = False


def _load_reminders() -> list[dict]:
    if not _DATA_FILE.exists():
        return []
    try:
        return json.loads(_DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_reminders(items: list[dict]) -> None:
    try:
        _DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        _DATA_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")
    except OSError:
        pass


def _trigger_alert(reminder: dict) -> None:
    label = reminder.get("label", "Timer")
    logger.info("Timer/Reminder alert: %s", label)
    
    # Run sound/speech alert in worker thread so we don't stall the loop
    def _announce():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(f"Alert! Time is up for {label}.")
            engine.runAndWait()
        except Exception:
            try:
                import winsound
                winsound.Beep(1000, 1000)
            except Exception:
                pass

    threading.Thread(target=_announce, daemon=True).start()


def _monitor_loop():
    while True:
        now = time.time()
        due = []
        with _lock:
            remaining = []
            for item in _active_reminders:
                if item["due_timestamp"] <= now:
                    due.append(item)
                else:
                    remaining.append(item)
            if due:
                _active_reminders.clear()
                _active_reminders.extend(remaining)
                _save_reminders(_active_reminders)

        for item in due:
            _trigger_alert(item)

        time.sleep(1.0)


def ensure_monitor():
    global _thread_started, _active_reminders
    with _lock:
        if not _thread_started:
            _active_reminders = _load_reminders()
            t = threading.Thread(target=_monitor_loop, daemon=True)
            t.start()
            _thread_started = True


def set_timer(seconds: int, label: str = "Timer") -> str:
    ensure_monitor()
    due_ts = time.time() + max(1, seconds)
    due_time_str = datetime.fromtimestamp(due_ts).strftime("%I:%M:%S %p")
    
    item = {
        "id": f"timer-{int(time.time()*1000)}",
        "kind": "timer",
        "label": label,
        "seconds": seconds,
        "due_timestamp": due_ts,
        "due_time_str": due_time_str,
    }
    
    with _lock:
        _active_reminders.append(item)
        _save_reminders(_active_reminders)
        
    mins = seconds // 60
    secs = seconds % 60
    dur = f"{mins} minute{'s' if mins != 1 else ''}" if mins else f"{secs} seconds"
    return f"Timer set for {dur} ({label}) — due at {due_time_str}."


def set_reminder(label: str, delay_minutes: int) -> str:
    return set_timer(delay_minutes * 60, label=label)


def list_reminders() -> str:
    ensure_monitor()
    with _lock:
        now = time.time()
        active = [x for x in _active_reminders if x["due_timestamp"] > now]
    if not active:
        return "You have no active timers or reminders."
    lines = []
    for x in active:
        remaining_secs = max(0, int(x["due_timestamp"] - now))
        mins, secs = divmod(remaining_secs, 60)
        lines.append(f"- {x['label']} (in {mins}m {secs}s, due at {x['due_time_str']})")
    return "Active timers & reminders:\n" + "\n".join(lines)


# ---------------- Student Study Notes ----------------
def save_study_note(title: str, content: str) -> str:
    notes_dir = _get_notes_dir()
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip() or "Note"
    file_path = notes_dir / f"{safe_title}_{datetime.now():%Y%m%d_%H%M%S}.txt"
    file_path.write_text(f"Title: {title}\nDate: {datetime.now():%Y-%m-%d %H:%M}\n\n{content}", encoding="utf-8")
    return f"Study note saved to: {file_path}"


def list_study_notes() -> str:
    notes_dir = _get_notes_dir()
    if not notes_dir.exists():
        return "You don't have any saved study notes yet."
    notes = list(notes_dir.glob("*.txt"))
    if not notes:
        return "No study notes found."
    return f"Found {len(notes)} study note(s):\n" + "\n".join(f"- {n.name}" for n in notes[:10])
