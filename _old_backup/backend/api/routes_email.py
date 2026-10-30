from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.connection import get_db
from backend.integrations.email.mock_email import MockEmailProvider

router = APIRouter(prefix="/emails", tags=["Emails"])

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class DraftRequest(BaseModel):
    email_id: str
    reply_text: str

class SendEmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str

@router.get("")
def list_emails(limit: int = 15, unread_only: bool = False, db: Session = Depends(get_db)):
    email_prov = MockEmailProvider(db=db)
    return email_prov.list_emails(limit=limit, unread_only=unread_only)

@router.post("/search")
def search_emails(req: SearchRequest, db: Session = Depends(get_db)):
    email_prov = MockEmailProvider(db=db)
    return email_prov.search_emails(query=req.query, limit=req.limit)

@router.get("/{email_id}")
def read_email(email_id: str, db: Session = Depends(get_db)):
    email_prov = MockEmailProvider(db=db)
    email = email_prov.read_email(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@router.post("/draft")
def draft_email_reply(req: DraftRequest, db: Session = Depends(get_db)):
    email_prov = MockEmailProvider(db=db)
    res = email_prov.draft_reply(req.email_id, req.reply_text)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.post("/send")
def send_email(req: SendEmailRequest, db: Session = Depends(get_db)):
    email_prov = MockEmailProvider(db=db)
    return email_prov.send_email(req.recipient, req.subject, req.body)
