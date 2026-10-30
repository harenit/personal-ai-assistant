"""Process-wide configuration for JARVIS Student Autonomous AI Agent."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _default_data_dir() -> Path:
    env_dir = os.environ.get("JARVIS_DATA_DIR") or os.environ.get("AURA_DATA_DIR")
    if env_dir:
        try:
            p = Path(env_dir)
            p.mkdir(parents=True, exist_ok=True)
            return p
        except OSError:
            pass

    target = Path.home() / "AppData" / "Local" / "JARVIS"
    try:
        target.mkdir(parents=True, exist_ok=True)
        test_file = target / ".write_test"
        test_file.touch(exist_ok=True)
        test_file.unlink(missing_ok=True)
        return target
    except OSError:
        fallback = Path(__file__).resolve().parent.parent.parent / ".jarvis_data"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


@dataclass(frozen=True)
class Settings:
    port: int = 8756
    app_name: str = "JARVIS"
    data_dir: Path = _default_data_dir()
    ollama_host: str = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")


settings = Settings()
