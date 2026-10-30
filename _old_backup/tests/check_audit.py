from backend.database.connection import SessionLocal
from backend.database.models import AuditLog, PermissionRequest

s = SessionLocal()
print("=== RECENT AUDIT LOGS ===")
logs = s.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(15).all()
for l in reversed(logs):
    print(f"[{l.timestamp.strftime('%H:%M:%S')}] {l.event_type} | Tool: {l.tool_name} | {l.details}")

print("\n=== RECENT PERMISSION REQUESTS ===")
perms = s.query(PermissionRequest).order_by(PermissionRequest.created_at.desc()).limit(5).all()
for p in perms:
    print(f"ID: {p.id} | Tool: {p.tool_name} | Status: {p.status} | Details: {p.description}")
