import uuid
from datetime import datetime, timedelta
from typing import Any, Optional
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import CalendarEvent
from backend.integrations.calendar.base import CalendarProvider

class MockCalendarProvider(CalendarProvider):
    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def _get_db(self):
        return self._db if self._db else SessionLocal()

    def list_events(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            query = db.query(CalendarEvent)
            if start_date:
                query = query.filter(CalendarEvent.end_datetime >= start_date)
            if end_date:
                query = query.filter(CalendarEvent.start_datetime <= end_date)
            events = query.order_by(CalendarEvent.start_datetime.asc()).all()
            return [
                {
                    "id": ev.id,
                    "title": ev.title,
                    "start": ev.start_datetime.strftime("%Y-%m-%d %I:%M %p"),
                    "end": ev.end_datetime.strftime("%Y-%m-%d %I:%M %p"),
                    "location": ev.location,
                    "event_type": ev.event_type,
                    "description": ev.description
                }
                for ev in events
            ]
        finally:
            if not self._db:
                db.close()

    def get_upcoming_events(self, hours_ahead: int = 48) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            now = datetime.now()
            cutoff = now + timedelta(hours=hours_ahead)
            events = db.query(CalendarEvent).filter(
                CalendarEvent.start_datetime >= now,
                CalendarEvent.start_datetime <= cutoff
            ).order_by(CalendarEvent.start_datetime.asc()).all()
            return [
                {
                    "id": ev.id,
                    "title": ev.title,
                    "start": ev.start_datetime.strftime("%Y-%m-%d %I:%M %p"),
                    "end": ev.end_datetime.strftime("%Y-%m-%d %I:%M %p"),
                    "location": ev.location,
                    "event_type": ev.event_type,
                    "description": ev.description
                }
                for ev in events
            ]
        finally:
            if not self._db:
                db.close()

    def create_event(
        self,
        title: str,
        start_datetime: datetime,
        end_datetime: datetime,
        location: str = "Campus",
        event_type: str = "study",
        description: str = ""
    ) -> dict[str, Any]:
        db = self._get_db()
        try:
            ev = CalendarEvent(
                id=str(uuid.uuid4()),
                title=title,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=location,
                event_type=event_type,
                description=description
            )
            db.add(ev)
            db.commit()
            return {
                "success": True,
                "event_id": ev.id,
                "title": ev.title,
                "start": ev.start_datetime.strftime("%Y-%m-%d %I:%M %p"),
                "end": ev.end_datetime.strftime("%Y-%m-%d %I:%M %p"),
                "location": ev.location,
                "message": f"Calendar event '{title}' scheduled for {ev.start_datetime.strftime('%Y-%m-%d %I:%M %p')}."
            }
        finally:
            if not self._db:
                db.close()

    def cancel_event(self, event_id: str) -> dict[str, Any]:
        db = self._get_db()
        try:
            ev = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
            if not ev:
                ev = db.query(CalendarEvent).filter(CalendarEvent.title.ilike(f"%{event_id}%")).first()

            if not ev:
                return {
                    "success": False,
                    "message": f"Event '{event_id}' not found in calendar."
                }

            title = ev.title
            db.delete(ev)
            db.commit()
            return {
                "success": True,
                "event_id": event_id,
                "message": f"Calendar event '{title}' has been canceled."
            }
        finally:
            if not self._db:
                db.close()
