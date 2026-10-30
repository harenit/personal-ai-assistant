from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

class AgentStep(BaseModel):
    step_number: int
    action_type: str  # "plan", "tool_select", "tool_result", "permission_request", "final_response"
    tool_name: Optional[str] = None
    arguments: Optional[dict[str, Any]] = None
    result: Optional[dict[str, Any]] = None
    status_message: str  # Safe, clean UI indicator (NEVER private chain-of-thought)
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%I:%M:%S %p"))

class AgentState(BaseModel):
    conversation_id: str
    task: str
    messages: list[dict[str, Any]] = Field(default_factory=list)
    steps: list[AgentStep] = Field(default_factory=list)
    status: str = "idle"  # "planning", "executing", "waiting_for_permission", "completed", "error"
    permission_request: Optional[dict[str, Any]] = None
    final_response: Optional[str] = None
    referenced_files: list[dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
