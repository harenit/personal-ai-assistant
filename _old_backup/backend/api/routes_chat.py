from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agent.engine import agent_engine
from backend.voice.tts import tts_service

router = APIRouter(prefix="/chat", tags=["Chat & Agent"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    voice_mode: bool = False

@router.post("")
def chat_with_agent(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    state = agent_engine.run_task(
        task=req.message,
        conversation_id=req.conversation_id
    )

    audio_url = None
    if req.voice_mode and state.final_response:
        success, url = tts_service.synthesize_speech(state.final_response)
        if success:
            audio_url = url

    return {
        "conversation_id": state.conversation_id,
        "status": state.status,
        "final_response": state.final_response,
        "steps": [s.model_dump() for s in state.steps],
        "permission_request": state.permission_request,
        "referenced_files": state.referenced_files,
        "audio_url": audio_url
    }
