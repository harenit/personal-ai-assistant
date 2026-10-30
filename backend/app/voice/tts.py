"""Text-to-speech with Fish Audio neural generation and pyttsx3 offline fallback.

Uses high-fidelity neural voice synthesis via Fish Audio API when configured,
and seamlessly falls back to Windows SAPI5 pyttsx3 locally if offline.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
import urllib.request
import pyttsx3

logger = logging.getLogger(__name__)


def synthesize(text: str) -> bytes:
    """Synthesizes `text` to speech, returning WAV audio bytes."""
    clean = text.strip()
    if not clean:
        return b""

    # Try Fish Audio neural generation first if configured
    api_key = os.environ.get("FISH_AUDIO_API_KEY", "").strip()
    if api_key:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "JARVIS-Student-Agent/1.0",
                "model": "s2.1-pro-free",
            }
            payload = {"text": clean, "format": "wav"}
            req = urllib.request.Request(
                "https://api.fish.audio/v1/tts",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status == 200:
                    data = resp.read()
                    if len(data) > 100:
                        return data
        except Exception as exc:
            logger.info("Fish Audio unavailable (%s), falling back to local pyttsx3", exc)

    # Local pyttsx3 fallback
    engine = pyttsx3.init()
    fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        engine.save_to_file(clean, tmp_path)
        engine.runAndWait()
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        engine.stop()
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except OSError:
            pass
