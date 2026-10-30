"""Speech-to-text with Groq Whisper Cloud acceleration and faster-whisper local fallback.

Uses Groq whisper-large-v3-turbo for instantaneous (~100ms) transcription when
GROQ_API_KEY is available; falls back to local faster-whisper offline model.
"""
from __future__ import annotations

import io
import logging
import os
import httpx

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("small.en", device="cpu", compute_type="int8")
    return _model


def transcribe(wav_bytes: bytes) -> str:
    """Transcribes a mono 16-bit PCM WAV clip to text."""
    if not wav_bytes or len(wav_bytes) < 400:
        return ""

    # 1. Try Groq Whisper Cloud first for instantaneous transcription
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    if groq_key and groq_key.startswith("gsk_"):
        try:
            with httpx.Client(timeout=8.0) as client:
                files = {"file": ("audio.wav", wav_bytes, "audio/wav")}
                data = {
                    "model": os.environ.get("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo"),
                    "language": "en",
                    "response_format": "text",
                }
                headers = {"Authorization": f"Bearer {groq_key}"}
                resp = client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    files=files,
                    data=data,
                    headers=headers,
                )
                if resp.status_code == 200:
                    result = resp.text.strip()
                    if result:
                        return result
        except Exception as exc:
            logger.info("Groq STT unavailable (%s), falling back to local Whisper", exc)

    # 2. Local faster-whisper fallback
    try:
        model = _get_model()
        segments, _info = model.transcribe(
            io.BytesIO(wav_bytes), language="en", beam_size=5, vad_filter=True
        )
        return " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as exc:
        logger.error("Local Whisper transcription failed: %s", exc)
        return ""
