import uuid
from datetime import datetime, timedelta
from typing import Any, Optional
from backend.tools.base import BaseTool
from backend.permissions.models import RiskLevel
from backend.database.connection import SessionLocal
from backend.database.models import Reminder

class CreateReminderTool(BaseTool):
    name = "create_reminder"
    description = "Create a persistent study reminder or task alert for a specific date and time."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "What to be reminded about (e.g. 'Study AI Midterm', 'Submit Algorithms code')"
            },
            "due_datetime": {
                "type": "string",
                "description": "Due date and time in 'YYYY-MM-DD HH:MM' or ISO format, or relative e.g. 'tomorrow at 7 PM'"
            },
            "description": {
                "type": "string",
                "description": "Optional notes or details for the reminder",
                "default": ""
            }
        },
        "required": ["title", "due_datetime"]
    }

    def execute(self, title: str, due_datetime: str, description: str = "", **kwargs) -> dict[str, Any]:
        db = SessionLocal()
        try:
            # Parse datetime flexibly
            dt = self._parse_datetime(due_datetime)
            rem = Reminder(
                id=str(uuid.uuid4()),
                title=title,
                description=description,
                due_datetime=dt,
                recurrence="none",
                is_completed=False,
                created_at=datetime.utcnow()
            )
            db.add(rem)
            db.commit()

            return {
                "success": True,
                "reminder_id": rem.id,
                "title": rem.title,
                "due": rem.due_datetime.strftime("%Y-%m-%d %I:%M %p"),
                "message": f"Reminder set for {rem.due_datetime.strftime('%A, %b %d at %I:%M %p')}: '{title}'."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to set reminder: {str(e)}"
            }
        finally:
            db.close()

    def _parse_datetime(self, val: str) -> datetime:
        now = datetime.now()
        lowered = val.lower().strip()
        
        # Relative dates: tomorrow, today, in X hours
        if "tomorrow" in lowered:
            target = now + timedelta(days=1)
            # Check for hour e.g. "7 pm", "19:00"
            if "pm" in lowered or "am" in lowered:
                # simple extract
                import re
                match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', lowered)
                if match:
                    hour = int(match.group(1))
                    minute = int(match.group(2) or 0)
                    ampm = match.group(3)
                    if ampm == "pm" and hour < 12:
                        hour += 12
                    elif ampm == "am" and hour == 12:
                        hour = 0
                    return target.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return target.replace(hour=19, minute=0, second=0, microsecond=0)
        
        if "today" in lowered:
            import re
            match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', lowered)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2) or 0)
                ampm = match.group(3)
                if ampm == "pm" and hour < 12:
                    hour += 12
                elif ampm == "am" and hour == 12:
                    hour = 0
                return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return now + timedelta(hours=2)

        try:
            return datetime.fromisoformat(val)
        except ValueError:
            pass

        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %I:%M %p", "%Y-%m-%d"):
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                continue

        # Default fallback: 2 hours from now
        return now + timedelta(hours=2)

class ListRemindersTool(BaseTool):
    name = "list_reminders"
    description = "List all active reminders and study tasks."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "include_completed": {
                "type": "boolean",
                "description": "Whether to include already completed reminders",
                "default": False
            }
        }
    }

    def execute(self, include_completed: bool = False, **kwargs) -> dict[str, Any]:
        db = SessionLocal()
        try:
            query = db.query(Reminder)
            if not include_completed:
                query = query.filter(Reminder.is_completed == False)
            reminders = query.order_by(Reminder.due_datetime.asc()).all()
            return {
                "success": True,
                "count": len(reminders),
                "reminders": [
                    {
                        "id": r.id,
                        "title": r.title,
                        "description": r.description,
                        "due": r.due_datetime.strftime("%Y-%m-%d %I:%M %p"),
                        "is_completed": r.is_completed
                    }
                    for r in reminders
                ]
            }
        finally:
            db.close()

class DeleteReminderTool(BaseTool):
    name = "delete_reminder"
    description = "Delete or dismiss a reminder by ID or title."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "reminder_id": {
                "type": "string",
                "description": "ID or title of the reminder to delete"
            }
        },
        "required": ["reminder_id"]
    }

    def execute(self, reminder_id: str, **kwargs) -> dict[str, Any]:
        db = SessionLocal()
        try:
            rem = db.query(Reminder).filter(Reminder.id == reminder_id).first()
            if not rem:
                rem = db.query(Reminder).filter(Reminder.title.ilike(f"%{reminder_id}%")).first()

            if not rem:
                return {
                    "success": False,
                    "message": f"Reminder '{reminder_id}' not found."
                }

            title = rem.title
            db.delete(rem)
            db.commit()
            return {
                "success": True,
                "message": f"Reminder '{title}' has been removed."
            }
        finally:
            db.close()
