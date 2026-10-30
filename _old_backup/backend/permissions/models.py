from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime

class RiskLevel(str, Enum):
    LOW_RISK = "LOW_RISK"
    SENSITIVE = "SENSITIVE"

class PermissionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"

class PermissionRequestInfo(BaseModel):
    id: str
    tool_name: str
    risk_level: RiskLevel
    parameters: dict[str, Any]
    description: str
    reason: str
    status: PermissionStatus
    created_at: datetime
