"""Student Academic Profile management for JARVIS.

Stores and manages context about the student: college, department, degree,
year, semester, active courses, academic goals, and deadlines.
Persisted locally in the application's data directory.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class StudentProfile:
    name: str = "Student"
    college: str = "National Engineering College"
    department: str = "Computer Science and Engineering"
    degree: str = "B.E. Computer Science and Engineering"
    academic_year: str = "2nd Year"
    semester: str = "Semester IV"
    subjects: list[str] = field(default_factory=lambda: [
        "Database Management Systems",
        "Operating Systems",
        "Computer Networks",
        "Design and Analysis of Algorithms",
        "Artificial Intelligence",
    ])
    academic_goals: list[str] = field(default_factory=lambda: [
        "Maintain GPA above 8.5",
        "Complete all LMS assignments 24h prior to deadline",
        "Master Data Structures and System Design",
    ])
    preferred_learning_style: str = "Interactive with practical coding examples and bulleted summaries"
    preferred_language: str = "English"
    exam_schedule: list[dict[str, str]] = field(default_factory=lambda: [
        {"subject": "Database Management Systems", "date": "2026-11-15", "session": "Forenoon"},
        {"subject": "Operating Systems", "date": "2026-11-18", "session": "Forenoon"},
        {"subject": "Computer Networks", "date": "2026-11-21", "session": "Forenoon"},
    ])
    deadlines: list[dict[str, str]] = field(default_factory=lambda: [
        {"title": "DBMS Normalization Assignment", "subject": "Database Management Systems", "due": "2026-11-05"},
        {"title": "OS Process Scheduling Lab Report", "subject": "Operating Systems", "due": "2026-11-08"},
    ])


class ProfileManager:
    """Manages reading, updating, and saving the student's profile."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or (settings.data_dir / "student_profile.json")
        self._profile: StudentProfile | None = None

    def get_profile(self) -> StudentProfile:
        if self._profile is not None:
            return self._profile
        try:
            if not self._path.exists():
                self._profile = StudentProfile()
                self.save_profile(self._profile)
                return self._profile
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self._profile = StudentProfile(**data)
        except Exception as exc:
            logger.warning("Could not read student profile, using defaults: %s", exc)
            self._profile = StudentProfile()
        return self._profile

    def save_profile(self, profile: StudentProfile) -> None:
        self._profile = profile
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(asdict(profile), indent=2), encoding="utf-8")
        except OSError:
            pass

    def update_profile(self, updates: dict[str, Any]) -> StudentProfile:
        curr = self.get_profile()
        d = asdict(curr)
        for k, v in updates.items():
            if k in d and v is not None:
                d[k] = v
        updated = StudentProfile(**d)
        self.save_profile(updated)
        return updated


_profile_mgr: ProfileManager | None = None


def get_profile_manager() -> ProfileManager:
    global _profile_mgr
    if _profile_mgr is None:
        _profile_mgr = ProfileManager()
    return _profile_mgr
