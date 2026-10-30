from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.connection import get_db
from backend.integrations.calendar.mock_calendar import MockCalendarProvider

router = APIRouter(prefix="/calendar", tags=["Calendar"])

class EventCreateRequest(BaseModel):
    title: str
    start_time: str
    end_time: str
    location: str = "Campus"
    event_type: str = "study"
    description: str = ""

@router.get("/events")
def list_events(db: Session = Depends(get_db)):
    cal = MockCalendarProvider(db=db)
    return cal.list_events()

@router.get("/upcoming")
def get_upcoming_events(hours_ahead: int = 48, db: Session = Depends(get_db)):
    cal = MockCalendarProvider(db=db)
    return cal.get_upcoming_events(hours_ahead=hours_ahead)

@router.post("/events")
def create_event(req: EventCreateRequest, db: Session = Depends(get_db)):
    cal = MockCalendarProvider(db=db)
    try:
        try:
            start_dt = datetime.fromisoformat(req.start_time)
        except ValueError:
            start_dt = datetime.strptime(req.start_time, "%Y-%m-%d %H:%M")
        try:
            end_dt = datetime.fromisoformat(req.end_time)
        except ValueError:
            end_dt = datetime.strptime(req.end_time, "%Y-%m-%d %H:%M")

        return cal.create_event(
            title=req.title,
            start_datetime=start_dt,
            end_datetime=end_dt,
            location=req.location,
            event_type=req.event_type,
            description=req.description
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/events/{event_id}")
def cancel_event(event_id: str, db: Session = Depends(get_db)):
    cal = MockCalendarProvider(db=db)
    res = cal.cancel_event(event_id)
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res
