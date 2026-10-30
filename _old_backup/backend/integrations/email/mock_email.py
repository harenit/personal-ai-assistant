import uuid
from datetime import datetime
from typing import Any, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import Email
from backend.integrations.email.base import EmailProvider

class MockEmailProvider(EmailProvider):
    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def _get_db(self):
        return self._db if self._db else SessionLocal()

    def list_emails(self, limit: int = 10, unread_only: bool = False) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            query = db.query(Email)
            if unread_only:
                query = query.filter(Email.is_read == False)
            emails = query.order_by(Email.received_at.desc()).limit(limit).all()
            return [
                {
                    "id": e.id,
                    "sender": e.sender,
                    "sender_name": e.sender_name,
                    "recipient": e.recipient,
                    "subject": e.subject,
                    "snippet": e.body[:120] + "..." if len(e.body) > 120 else e.body,
                    "received_at": e.received_at.strftime("%Y-%m-%d %I:%M %p"),
                    "is_read": e.is_read,
                    "category": e.category
                }
                for e in emails
            ]
        finally:
            if not self._db:
                db.close()

    def search_emails(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            pattern = f"%{query}%"
            emails = db.query(Email).filter(
                or_(
                    Email.subject.ilike(pattern),
                    Email.body.ilike(pattern),
                    Email.sender.ilike(pattern),
                    Email.sender_name.ilike(pattern)
                )
            ).order_by(Email.received_at.desc()).limit(limit).all()

            return [
                {
                    "id": e.id,
                    "sender": e.sender,
                    "sender_name": e.sender_name,
                    "subject": e.subject,
                    "snippet": e.body[:150] + "...",
                    "body": e.body,
                    "received_at": e.received_at.strftime("%Y-%m-%d %I:%M %p")
                }
                for e in emails
            ]
        finally:
            if not self._db:
                db.close()

    def read_email(self, email_id: str) -> Optional[dict[str, Any]]:
        db = self._get_db()
        try:
            email = db.query(Email).filter(Email.id == email_id).first()
            if not email:
                # Try finding by subject search
                email = db.query(Email).filter(Email.subject.ilike(f"%{email_id}%")).first()

            if not email:
                return None

            email.is_read = True
            db.commit()

            return {
                "id": email.id,
                "sender": email.sender,
                "sender_name": email.sender_name,
                "recipient": email.recipient,
                "subject": email.subject,
                "body": email.body,
                "received_at": email.received_at.strftime("%Y-%m-%d %I:%M %p"),
                "category": email.category
            }
        finally:
            if not self._db:
                db.close()

    def draft_reply(self, email_id: str, reply_text: str) -> dict[str, Any]:
        db = self._get_db()
        try:
            email = db.query(Email).filter(Email.id == email_id).first()
            if not email:
                email = db.query(Email).filter(Email.subject.ilike(f"%{email_id}%")).first()

            if not email:
                return {
                    "success": False,
                    "message": f"Reference email '{email_id}' not found to draft reply."
                }

            return {
                "success": True,
                "recipient": email.sender,
                "recipient_name": email.sender_name,
                "subject": f"Re: {email.subject}" if not email.subject.startswith("Re:") else email.subject,
                "draft_body": reply_text,
                "message": f"Draft created for {email.sender_name} ({email.sender}). Explicit permission required to send."
            }
        finally:
            if not self._db:
                db.close()

    def send_email(self, recipient: str, subject: str, body: str) -> dict[str, Any]:
        db = self._get_db()
        try:
            new_email = Email(
                id=str(uuid.uuid4()),
                sender="alex.rivers@university.edu",
                sender_name="Alex Rivers (Student)",
                recipient=recipient,
                subject=subject,
                body=body,
                received_at=datetime.utcnow(),
                is_read=True,
                category="academic"
            )
            db.add(new_email)
            db.commit()

            return {
                "success": True,
                "email_id": new_email.id,
                "recipient": recipient,
                "subject": subject,
                "sent_at": new_email.received_at.strftime("%Y-%m-%d %I:%M %p"),
                "message": f"Email successfully sent to {recipient} with subject '{subject}'."
            }
        finally:
            if not self._db:
                db.close()
