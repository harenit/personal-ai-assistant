import pytest
from backend.database.connection import SessionLocal
from backend.database.models import User, Course, Assignment, Exam, Announcement, Email, CalendarEvent, Reminder

def test_database_seeded_data():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        assert user is not None
        assert user.name == "Alex Rivers"

        courses = db.query(Course).all()
        assert len(courses) >= 4

        assignments = db.query(Assignment).all()
        assert len(assignments) >= 4

        exams = db.query(Exam).all()
        assert len(exams) >= 2

        emails = db.query(Email).all()
        assert len(emails) >= 3

        events = db.query(CalendarEvent).all()
        assert len(events) >= 4

        reminders = db.query(Reminder).all()
        assert len(reminders) >= 2
    finally:
        db.close()
