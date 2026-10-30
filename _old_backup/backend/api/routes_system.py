import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.connection import get_db
from backend.database.models import User
from backend.config.settings import settings
from backend.tools.system_tools import OpenApplicationTool, OpenUrlTool, OpenFolderTool

router = APIRouter(tags=["System & Health"])

class OpenAppRequest(BaseModel):
    application_name: str

class OpenUrlRequest(BaseModel):
    url: str

class OpenFolderRequest(BaseModel):
    folder_name: str

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    # 1. Database check
    db_status = "ok"
    try:
        db.query(User).first()
    except Exception as e:
        db_status = f"error: {str(e)}"

    # 2. Ollama & model check
    ollama_status = "offline"
    model_status = "unavailable"
    try:
        r = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=3)
        if r.status_code == 200:
            ollama_status = "ok"
            models = [m.get("name") for m in r.json().get("models", [])]
            if any(settings.OLLAMA_MODEL in m for m in models):
                model_status = "available"
            else:
                model_status = f"model '{settings.OLLAMA_MODEL}' not in tags: {models}"
    except Exception:
        pass

    return {
        "status": "healthy" if db_status == "ok" and ollama_status == "ok" else "degraded",
        "backend": "ok",
        "database": db_status,
        "ollama": ollama_status,
        "model": model_status,
        "configured_model": settings.OLLAMA_MODEL,
        "demo_mode": settings.DEMO_MODE,
        "tts_enabled": settings.TTS_ENABLED
    }

@router.get("/system/apps")
def get_allowed_apps():
    return {
        "allowed_applications": settings.ALLOWED_APP_NAMES
    }

@router.post("/system/open/app")
def open_system_app(req: OpenAppRequest):
    tool = OpenApplicationTool()
    res = tool.execute(application_name=req.application_name)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.post("/system/open/url")
def open_system_url(req: OpenUrlRequest):
    tool = OpenUrlTool()
    res = tool.execute(url=req.url)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.post("/system/open/folder")
def open_system_folder(req: OpenFolderRequest):
    tool = OpenFolderTool()
    res = tool.execute(folder_name=req.folder_name)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.get("/system/telemetry")
def get_system_telemetry():
    import psutil
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("C:\\").percent
    battery = None
    if hasattr(psutil, "sensors_battery"):
        b = psutil.sensors_battery()
        if b:
            battery = {"percent": b.percent, "power_plugged": b.power_plugged}
    return {
        "cpu_percent": cpu,
        "ram_percent": ram,
        "disk_percent": disk,
        "battery": battery,
        "status": "OPERATIONAL"
    }
