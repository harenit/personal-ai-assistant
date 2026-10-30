import os
import uuid
import logging
from pathlib import Path
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class TextToSpeechService:
    def __init__(self):
        self.enabled = settings.TTS_ENABLED
        self.output_dir = settings.GENERATED_DIR / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize_speech(self, text: str, speak_desktop: bool = False) -> tuple[bool, str]:
        """
        Synthesizes text into a .wav file and optionally speaks on Windows.
        Returns: (success: bool, audio_file_path_or_url: str)
        """
        if not self.enabled or not text.strip():
            return False, ""

        clean_text = text.replace("*", "").replace("#", "").strip()[:500]
        file_name = f"tts_{uuid.uuid4().hex[:8]}.wav"
        file_path = self.output_dir / file_name

        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", settings.TTS_VOICE_RATE)
            engine.save_to_file(clean_text, str(file_path))
            engine.runAndWait()

            if speak_desktop:
                try:
                    engine.say(clean_text)
                    engine.runAndWait()
                except Exception:
                    pass

            return True, f"/generated/audio/{file_name}"
        except Exception as e:
            logger.warning(f"pyttsx3 synthesis failed: {e}")
            return False, ""

tts_service = TextToSpeechService()
