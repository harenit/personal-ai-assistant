import json
import uuid
from datetime import datetime
from typing import Any, Optional
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import PermissionRequest, AuditLog
from backend.permissions.models import RiskLevel, PermissionStatus

# Allowlisted tools and their risk classifications
SENSITIVE_TOOLS = {
    "send_email": "Sending an email communicates externally on the student's behalf.",
    "submit_assignment": "Submitting an assignment officially alters course academic records.",
    "create_calendar_event": "Creating an event modifies external calendar commitments.",
    "cancel_calendar_event": "Canceling an event removes a scheduled commitment.",
    "delete_document": "Deleting an uploaded document removes permanent student records."
}

class PermissionManager:
    @staticmethod
    def get_risk_level(tool_name: str) -> RiskLevel:
        if tool_name in SENSITIVE_TOOLS:
            return RiskLevel.SENSITIVE
        return RiskLevel.LOW_RISK

    @staticmethod
    def requires_permission(tool_name: str) -> bool:
        return tool_name in SENSITIVE_TOOLS

    @staticmethod
    def create_request(
        tool_name: str,
        parameters: dict[str, Any],
        description: str = "",
        reason: str = "",
        db: Optional[Session] = None
    ) -> PermissionRequest:
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            req_id = str(uuid.uuid4())
            if not reason:
                reason = SENSITIVE_TOOLS.get(tool_name, "This action requires authorization.")
            
            if not description:
                description = f"JARVIS wants permission to execute {tool_name} with: {json.dumps(parameters)}"

            req = PermissionRequest(
                id=req_id,
                tool_name=tool_name,
                risk_level=RiskLevel.SENSITIVE.value,
                parameters_json=json.dumps(parameters),
                description=description,
                reason=reason,
                status=PermissionStatus.PENDING.value,
                created_at=datetime.utcnow()
            )
            db.add(req)

            # Audit log
            audit = AuditLog(
                event_type="PERMISSION_REQUEST",
                tool_name=tool_name,
                details=f"Permission requested for {tool_name}: {description}",
                status="PENDING",
                timestamp=datetime.utcnow()
            )
            db.add(audit)
            db.commit()
            db.refresh(req)
            return req
        finally:
            if close_db:
                db.close()

    @staticmethod
    def approve_request(request_id: str, db: Optional[Session] = None) -> Optional[PermissionRequest]:
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            req = db.query(PermissionRequest).filter(PermissionRequest.id == request_id).first()
            if not req:
                return None
            req.status = PermissionStatus.APPROVED.value
            req.resolved_at = datetime.utcnow()

            audit = AuditLog(
                event_type="PERMISSION_DECISION",
                tool_name=req.tool_name,
                details=f"Permission APPROVED for {req.tool_name} (ID: {req.id})",
                status="APPROVED",
                timestamp=datetime.utcnow()
            )
            db.add(audit)
            db.commit()
            db.refresh(req)
            return req
        finally:
            if close_db:
                db.close()

    @staticmethod
    def deny_request(request_id: str, db: Optional[Session] = None) -> Optional[PermissionRequest]:
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            req = db.query(PermissionRequest).filter(PermissionRequest.id == request_id).first()
            if not req:
                return None
            req.status = PermissionStatus.DENIED.value
            req.resolved_at = datetime.utcnow()

            audit = AuditLog(
                event_type="PERMISSION_DECISION",
                tool_name=req.tool_name,
                details=f"Permission DENIED for {req.tool_name} (ID: {req.id})",
                status="DENIED",
                timestamp=datetime.utcnow()
            )
            db.add(audit)
            db.commit()
            db.refresh(req)
            return req
        finally:
            if close_db:
                db.close()

    @staticmethod
    def log_audit(event_type: str, tool_name: Optional[str], details: str, status: str = "SUCCESS", db: Optional[Session] = None):
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            audit = AuditLog(
                event_type=event_type,
                tool_name=tool_name,
                details=details,
                status=status,
                timestamp=datetime.utcnow()
            )
            db.add(audit)
            db.commit()
        finally:
            if close_db:
                db.close()

    @staticmethod
    def get_pending_requests(db: Optional[Session] = None) -> list[PermissionRequest]:
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            return db.query(PermissionRequest).filter(
                PermissionRequest.status == PermissionStatus.PENDING.value
            ).order_by(PermissionRequest.created_at.desc()).all()
        finally:
            if close_db:
                db.close()
