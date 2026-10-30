from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.connection import get_db
from backend.database.models import Reminder
from backend.tools.reminder_tools import CreateReminderTool, DeleteReminderTool

router = APIRouter(prefix="/reminders", tags=["Reminders"])

class ReminderCreateRequest(BaseModel):
    title: str
    due_datetime: str
    description: str = ""

@router.get("")
def list_reminders(include_completed: bool = False, db: Session = Depends(get_db)):
    query = db.query(Reminder)
    if not include_completed:
        query = query.filter(Reminder.is_completed == False)
    reminders = query.order_by(Reminder.due_datetime.asc()).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "due": r.due_datetime.strftime("%Y-%m-%d %I:%M %p"),
            "is_completed": r.is_completed
        }
        for r in reminders
    ]

@router.post("")
def create_reminder(req: ReminderCreateRequest):
    tool = CreateReminderTool()
    res = tool.execute(title=req.title, due_datetime=req.due_datetime, description=req.description)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: str):
    tool = DeleteReminderTool()
    res = tool.execute(reminder_id=reminder_id)
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res
