"""Four-tier persistent student memory engine for JARVIS.

Tiers:
1. Conversational Memory: Turn history, user instructions, conversation summaries.
2. Academic Memory: Subjects, syllabus units, notes references, test preparation context.
3. Personal Preferences: Explanation style, document formats, schedule preferences.
4. Episodic Memory: Past completed tasks, generated deliverables, verified outcomes.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class AcademicMemoryManager:
    """Unified access to all four memory tiers."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._dir = data_dir or (settings.data_dir / "academic_memory")
        self._academic_path = self._dir / "academic_memory.json"
        self._preferences_path = self._dir / "preferences_memory.json"
        self._episodic_path = self._dir / "episodic_memory.json"

    def _load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return default

    def _save_json(self, path: Path, data: Any) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass

    # --- Academic Memory ---
    def get_academic_memory(self) -> dict[str, Any]:
        return self._load_json(self._academic_path, {
            "subjects": {},
            "syllabus_units": {},
            "active_assignments": [],
            "exam_prep": {},
        })

    def record_subject_topic(self, subject: str, topic: str, notes_summary: str = "") -> None:
        data = self.get_academic_memory()
        s_key = subject.strip().lower()
        if s_key not in data["subjects"]:
            data["subjects"][s_key] = {"name": subject, "topics": []}
        data["subjects"][s_key]["topics"].append({
            "topic": topic,
            "summary": notes_summary,
            "recorded_at": datetime.now().isoformat(),
        })
        self._save_json(self._academic_path, data)

    # --- Personal Preference Memory ---
    def get_preferences(self) -> dict[str, str]:
        return self._load_json(self._preferences_path, {
            "explanation_style": "Clear, structured, with step-by-step logic",
            "preferred_editor": "VS Code",
            "preferred_browser": "Chrome",
            "output_format": "Markdown & DOCX",
        })

    def set_preference(self, key: str, value: str) -> None:
        prefs = self.get_preferences()
        prefs[key.strip().lower()] = value.strip()
        self._save_json(self._preferences_path, prefs)

    def delete_preference(self, key: str) -> bool:
        prefs = self.get_preferences()
        k = key.strip().lower()
        if k in prefs:
            del prefs[k]
            self._save_json(self._preferences_path, prefs)
            return True
        return False

    # --- Episodic Memory ---
    def get_episodic_memory(self, limit: int = 50) -> list[dict[str, Any]]:
        episodes = self._load_json(self._episodic_path, [])
        return episodes[-limit:]

    def record_episode(self, action: str, details: str, outcome: str) -> None:
        episodes = self._load_json(self._episodic_path, [])
        episodes.append({
            "id": uuid.uuid4().hex[:8],
            "action": action,
            "details": details,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat(),
        })
        self._save_json(self._episodic_path, episodes[-100:])

    def get_memory_context_string(self) -> str:
        """Constructs concise prompt context summarizing student preferences and current subjects."""
        prefs = self.get_preferences()
        acad = self.get_academic_memory()
        subjects = [s["name"] for s in acad.get("subjects", {}).values()]
        parts = []
        if prefs:
            pref_str = ", ".join(f"{k}: {v}" for k, v in prefs.items())
            parts.append(f"Student Preferences: {pref_str}")
        if subjects:
            parts.append(f"Enrolled Subjects: {', '.join(subjects)}")
        return "\n".join(parts)


_academic_memory: AcademicMemoryManager | None = None


def get_academic_memory() -> AcademicMemoryManager:
    global _academic_memory
    if _academic_memory is None:
        _academic_memory = AcademicMemoryManager()
    return _academic_memory
