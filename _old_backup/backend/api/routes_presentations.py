from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.connection import get_db
from backend.database.models import GeneratedFile
from backend.tools.ppt_tools import GeneratePresentationTool
from backend.tools.system_tools import OpenGeneratedFileTool

router = APIRouter(prefix="/presentations", tags=["Presentations"])

class PresentationRequest(BaseModel):
    topic: str
    slide_count: int = 10
    audience: str = "College Students"
    key_points: Optional[list[str]] = None

class OpenFileRequest(BaseModel):
    file_path: str

@router.get("")
def list_presentations(db: Session = Depends(get_db)):
    files = db.query(GeneratedFile).filter(GeneratedFile.file_type == "pptx").order_by(GeneratedFile.created_at.desc()).all()
    return [
        {
            "id": f.id,
            "title": f.title,
            "file_name": f.file_name,
            "file_path": f.file_path,
            "description": f.description,
            "download_url": f"/generated/presentations/{f.file_name}",
            "created_at": f.created_at.strftime("%Y-%m-%d %I:%M %p")
        }
        for f in files
    ]

@router.post("/generate")
def generate_presentation(req: PresentationRequest):
    tool = GeneratePresentationTool()
    res = tool.execute(
        topic=req.topic,
        slide_count=req.slide_count,
        audience=req.audience,
        key_points=req.key_points
    )
    if not res.get("success"):
        raise HTTPException(status_code=500, detail=res.get("message"))
    return res

@router.post("/open")
def open_presentation_file(req: OpenFileRequest):
    tool = OpenGeneratedFileTool()
    res = tool.execute(file_path=req.file_path)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res
