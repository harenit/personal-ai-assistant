import io
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class SpeechToTextService:
    def __init__(self):
        self._recognizer = None
        self._init_recognizer()

    def _init_recognizer(self):
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
        except Exception as e:
            logger.warning(f"SpeechRecognition not initialized: {e}")

    def transcribe_audio_file(self, file_path: str | Path) -> str:
        """Transcribes audio file to text."""
        if not self._recognizer:
            self._init_recognizer()

        try:
            import speech_recognition as sr
            with sr.AudioFile(str(file_path)) as source:
                audio_data = self._recognizer.record(source)
                text = self._recognizer.recognize_google(audio_data)
                return text.strip()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            logger.warning(f"Speech recognition service error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""

stt_service = SpeechToTextService()
