from datetime import datetime, timedelta
from typing import Any, Optional
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import Course, Assignment, Exam, Announcement
from backend.integrations.lms.base import LMSProvider

class MockLMSProvider(LMSProvider):
    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def _get_db(self):
        return self._db if self._db else SessionLocal()

    def get_courses(self) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            courses = db.query(Course).all()
            return [
                {
                    "id": c.id,
                    "code": c.code,
                    "name": c.name,
                    "instructor": c.instructor,
                    "instructor_email": c.instructor_email,
                    "room": c.room,
                    "schedule": c.schedule,
                    "description": c.description
                }
                for c in courses
            ]
        finally:
            if not self._db:
                db.close()

    def get_assignments(self, course_id: Optional[str] = None) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            query = db.query(Assignment).join(Course)
            if course_id:
                query = query.filter(Assignment.course_id == course_id)
            assignments = query.order_by(Assignment.due_date.asc()).all()
            return [
                {
                    "id": a.id,
                    "course_code": a.course.code,
                    "course_name": a.course.name,
                    "title": a.title,
                    "description": a.description,
                    "due_date": a.due_date.isoformat(),
                    "points": a.points,
                    "status": a.status,
                    "grade": a.grade
                }
                for a in assignments
            ]
        finally:
            if not self._db:
                db.close()

    def get_upcoming_assignments(self, days_ahead: int = 7) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            now = datetime.now()
            cutoff = now + timedelta(days=days_ahead)
            assignments = db.query(Assignment).join(Course).filter(
                Assignment.due_date >= now,
                Assignment.due_date <= cutoff,
                Assignment.status == "pending"
            ).order_by(Assignment.due_date.asc()).all()
            return [
                {
                    "id": a.id,
                    "course_code": a.course.code,
                    "course_name": a.course.name,
                    "title": a.title,
                    "description": a.description,
                    "due_date": a.due_date.strftime("%Y-%m-%d %I:%M %p"),
                    "points": a.points,
                    "status": a.status
                }
                for a in assignments
            ]
        finally:
            if not self._db:
                db.close()

    def get_overdue_assignments(self) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            now = datetime.now()
            assignments = db.query(Assignment).join(Course).filter(
                Assignment.due_date < now,
                Assignment.status == "pending"
            ).order_by(Assignment.due_date.asc()).all()
            return [
                {
                    "id": a.id,
                    "course_code": a.course.code,
                    "title": a.title,
                    "due_date": a.due_date.strftime("%Y-%m-%d %I:%M %p"),
                    "points": a.points
                }
                for a in assignments
            ]
        finally:
            if not self._db:
                db.close()

    def get_exams(self) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            exams = db.query(Exam).join(Course).order_by(Exam.date.asc()).all()
            return [
                {
                    "id": e.id,
                    "course_code": e.course.code,
                    "course_name": e.course.name,
                    "title": e.title,
                    "date": e.date.strftime("%Y-%m-%d"),
                    "start_time": e.start_time,
                    "end_time": e.end_time,
                    "room": e.room,
                    "topics": e.topics,
                    "weight_percent": e.weight_percent
                }
                for e in exams
            ]
        finally:
            if not self._db:
                db.close()

    def get_announcements(self) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
            return [
                {
                    "id": an.id,
                    "course_code": an.course.code if an.course else "GENERAL",
                    "title": an.title,
                    "content": an.content,
                    "author": an.author,
                    "is_urgent": an.is_urgent,
                    "created_at": an.created_at.strftime("%Y-%m-%d %I:%M %p")
                }
                for an in announcements
            ]
        finally:
            if not self._db:
                db.close()

    def submit_assignment(self, assignment_id: str, submission_text: str) -> dict[str, Any]:
        db = self._get_db()
        try:
            assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
            if not assignment:
                # Try finding by partial title
                assignment = db.query(Assignment).filter(Assignment.title.ilike(f"%{assignment_id}%")).first()
            
            if not assignment:
                return {
                    "success": False,
                    "message": f"Assignment '{assignment_id}' was not found in LMS records."
                }
            
            assignment.status = "submitted"
            assignment.submission_text = submission_text
            assignment.submitted_at = datetime.utcnow()
            db.commit()

            return {
                "success": True,
                "assignment_id": assignment.id,
                "assignment_title": assignment.title,
                "course_code": assignment.course.code,
                "submitted_at": assignment.submitted_at.strftime("%Y-%m-%d %I:%M %p"),
                "message": f"Assignment '{assignment.title}' successfully submitted."
            }
        finally:
            if not self._db:
                db.close()
