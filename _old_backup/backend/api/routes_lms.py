from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.integrations.lms.mock_lms import MockLMSProvider
from pydantic import BaseModel

router = APIRouter(tags=["LMS"])

class SubmissionRequest(BaseModel):
    submission_text: str

@router.get("/courses")
def get_courses(db: Session = Depends(get_db)):
    lms = MockLMSProvider(db=db)
    return lms.get_courses()

@router.get("/assignments")
def get_assignments(course_id: Optional[str] = None, db: Session = Depends(get_db)):
    lms = MockLMSProvider(db=db)
    return lms.get_assignments(course_id=course_id)

@router.get("/assignments/upcoming")
def get_upcoming_assignments(days_ahead: int = 7, db: Session = Depends(get_db)):
    lms = MockLMSProvider(db=db)
    return lms.get_upcoming_assignments(days_ahead=days_ahead)

@router.get("/exams")
def get_exams(db: Session = Depends(get_db)):
    lms = MockLMSProvider(db=db)
    return lms.get_exams()

@router.get("/announcements")
def get_announcements(db: Session = Depends(get_db)):
    lms = MockLMSProvider(db=db)
    return lms.get_announcements()

@router.post("/assignments/{assignment_id}/submit")
def submit_assignment(assignment_id: str, req: SubmissionRequest, db: Session = Depends(get_db)):
    lms = MockLMSProvider(db=db)
    res = lms.submit_assignment(assignment_id, req.submission_text)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res
