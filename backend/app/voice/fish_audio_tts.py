"""Fish Audio Text-To-Speech integration with fallback to pyttsx3.

Uses Fish Audio API for realistic neural voice synthesis.
Falls back seamlessly to local Windows pyttsx3 offline synthesis.
"""
from __future__ import annotations

import logging
import os
import urllib.request
import json
from app.voice import tts as local_tts

logger = logging.getLogger(__name__)

FISH_AUDIO_URL = "https://api.fish.audio/v1/tts"


def synthesize_speech(text: str) -> bytes:
    """Synthesize speech into WAV audio bytes.
    
    Attempts Fish Audio neural synthesis first if configured; falls back
    to pyttsx3 locally if offline or on error.
    """
    clean_text = text.strip()
    if not clean_text:
        return b""

    api_key = os.environ.get("FISH_AUDIO_API_KEY", "").strip()
    if api_key:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "JARVIS-Student-Agent/1.0",
                "model": "s2.1-pro-free",
            }
            payload = {
                "text": clean_text,
                "format": "wav",
            }
            req = urllib.request.Request(
                FISH_AUDIO_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status == 200:
                    data = resp.read()
                    if len(data) > 100:
                        return data
        except Exception as exc:
            logger.info("Fish Audio unavailable (%s), using local pyttsx3 engine", exc)

    # Local fallback
    return local_tts.synthesize_speech(clean_text)
