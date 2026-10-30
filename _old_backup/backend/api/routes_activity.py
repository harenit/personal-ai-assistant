from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.database.models import AuditLog

router = APIRouter(prefix="/activity", tags=["Activity Audit Trail"])

@router.get("")
def list_activity_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "event_type": l.event_type,
            "tool_name": l.tool_name,
            "details": l.details,
            "status": l.status,
            "timestamp": l.timestamp.strftime("%Y-%m-%d %I:%M:%S %p")
        }
        for l in logs
    ]
