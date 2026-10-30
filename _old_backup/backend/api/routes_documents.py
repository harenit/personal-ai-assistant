import shutil
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.connection import get_db
from backend.database.models import Document
from backend.config.settings import settings
from backend.rag.vector_store import vector_store
from backend.tools.study_tools import AskDocumentQuestionTool, GenerateQuizTool, GenerateFlashcardsTool, SummarizeDocumentTool

router = APIRouter(prefix="/documents", tags=["Documents & Study RAG"])

class QuestionRequest(BaseModel):
    question: str

class QuizRequest(BaseModel):
    topic: str
    count: int = 10

class FlashcardsRequest(BaseModel):
    topic: str
    count: int = 8

@router.get("")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "chunk_count": d.chunk_count,
            "summary": d.summary,
            "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d %I:%M %p")
        }
        for d in docs
    ]

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    db: Session = Depends(get_db)
):
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")

    file_id = str(uuid.uuid4())
    clean_filename = f"{file_id}_{file.filename}"
    save_path = settings.DOCUMENTS_DIR / clean_filename

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = save_path.stat().st_size
    doc_title = title or Path(file.filename).stem.replace("_", " ").title()

    # Index into Vector Store
    chunk_count = vector_store.add_document(doc_id=file_id, file_path=save_path)

    # Initial summary
    summary_tool = SummarizeDocumentTool()
    summary_res = summary_tool.execute(document_title=doc_title)
    doc_summary = summary_res.get("summary", "")[:500]

    doc_record = Document(
        id=file_id,
        title=doc_title,
        filename=file.filename,
        file_path=str(save_path),
        file_type=ext.replace(".", ""),
        file_size=file_size,
        summary=doc_summary,
        chunk_count=chunk_count,
        uploaded_at=datetime.utcnow()
    )
    db.add(doc_record)
    db.commit()

    return {
        "success": True,
        "document_id": file_id,
        "title": doc_title,
        "filename": file.filename,
        "chunks_indexed": chunk_count,
        "summary": doc_summary
    }

@router.post("/{doc_id}/ask")
def ask_document_question(doc_id: str, req: QuestionRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    tool = AskDocumentQuestionTool()
    return tool.execute(question=req.question, document_title=doc.title if doc else None)

@router.post("/{doc_id}/quiz")
def generate_doc_quiz(doc_id: str, req: QuizRequest):
    tool = GenerateQuizTool()
    return tool.execute(topic=req.topic, question_count=req.count)

@router.post("/{doc_id}/flashcards")
def generate_doc_flashcards(doc_id: str, req: FlashcardsRequest):
    tool = GenerateFlashcardsTool()
    return tool.execute(topic=req.topic, count=req.count)

@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    vector_store.delete_document(doc_id)
    try:
        Path(doc.file_path).unlink(missing_ok=True)
    except Exception:
        pass

    db.delete(doc)
    db.commit()
    return {"success": True, "message": f"Document '{doc.title}' deleted."}
