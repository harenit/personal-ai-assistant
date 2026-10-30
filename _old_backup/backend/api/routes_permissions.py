from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.permissions.manager import PermissionManager
from backend.agent.engine import agent_engine

router = APIRouter(prefix="/permissions", tags=["Permissions"])

@router.get("")
def list_pending_permissions(db: Session = Depends(get_db)):
    reqs = PermissionManager.get_pending_requests(db=db)
    return [
        {
            "id": r.id,
            "tool_name": r.tool_name,
            "risk_level": r.risk_level,
            "parameters": r.parameters_json,
            "description": r.description,
            "reason": r.reason,
            "status": r.status,
            "created_at": r.created_at.strftime("%Y-%m-%d %I:%M %p")
        }
        for r in reqs
    ]

@router.post("/{permission_id}/approve")
def approve_permission(permission_id: str):
    try:
        updated_state = agent_engine.resume_permission(permission_id, approved=True)
        return {
            "success": True,
            "permission_id": permission_id,
            "status": updated_state.status,
            "final_response": updated_state.final_response,
            "steps": [s.model_dump() for s in updated_state.steps],
            "referenced_files": updated_state.referenced_files
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume execution: {str(e)}")

@router.post("/{permission_id}/deny")
def deny_permission(permission_id: str):
    try:
        updated_state = agent_engine.resume_permission(permission_id, approved=False)
        return {
            "success": True,
            "permission_id": permission_id,
            "status": updated_state.status,
            "final_response": updated_state.final_response,
            "steps": [s.model_dump() for s in updated_state.steps],
            "referenced_files": updated_state.referenced_files
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process denial: {str(e)}")
