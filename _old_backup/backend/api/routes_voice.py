import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from backend.config.settings import settings
from backend.voice.stt import stt_service
from backend.voice.tts import tts_service

router = APIRouter(prefix="/voice", tags=["Voice"])

class SynthesizeRequest(BaseModel):
    text: str
    speak_desktop: bool = False

@router.get("/status")
def voice_status():
    return {
        "stt_available": True,
        "tts_available": settings.TTS_ENABLED,
        "wake_word_enabled": settings.WAKE_WORD_ENABLED,
        "wake_word": settings.WAKE_WORD
    }

@router.post("/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
    temp_dir = settings.DATA_DIR / "temp_audio"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{uuid.uuid4().hex}_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = stt_service.transcribe_audio_file(temp_path)
        return {
            "success": True,
            "transcription": text
        }
    finally:
        temp_path.unlink(missing_ok=True)

@router.post("/synthesize")
def synthesize_voice(req: SynthesizeRequest):
    success, audio_url = tts_service.synthesize_speech(req.text, speak_desktop=req.speak_desktop)
    if not success:
        raise HTTPException(status_code=500, detail="Text-to-speech synthesis failed.")
    return {
        "success": True,
        "audio_url": audio_url
    }
