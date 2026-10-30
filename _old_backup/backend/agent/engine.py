import json
import logging
import uuid
from datetime import datetime
from typing import Any, Optional
from backend.agent.state import AgentState, AgentStep
from backend.tools.registry import tool_registry
from backend.permissions.manager import PermissionManager
from backend.permissions.models import PermissionStatus
from backend.llm.client import llm_client
from backend.database.connection import SessionLocal
from backend.database.models import Conversation, Message, AuditLog

logger = logging.getLogger(__name__)

class AgentEngine:
    def __init__(self):
        # In-memory dictionary holding paused states waiting for approval: request_id -> (state, pending_call)
        self.pending_tasks: dict[str, tuple[AgentState, dict[str, Any]]] = {}

    def run_task(self, task: str, conversation_id: Optional[str] = None, max_turns: int = 6) -> AgentState:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        # Load recent conversation history from DB if available
        messages = self._load_conversation_history(conversation_id)
        messages.append({"role": "user", "content": task})

        state = AgentState(
            conversation_id=conversation_id,
            task=task,
            messages=messages,
            steps=[],
            status="planning"
        )

        step_counter = 1

        # Audit task start
        PermissionManager.log_audit("TASK_START", None, f"Student task started: '{task}'")

        state.steps.append(AgentStep(
            step_number=step_counter,
            action_type="plan",
            status_message=f"Understanding request: '{task[:60]}...'"
        ))
        step_counter += 1

        tools_schema = tool_registry.get_relevant_tools(task)

        for turn in range(max_turns):
            # Query LLM
            llm_result = llm_client.chat(messages=state.messages, tools=tools_schema)
            content = llm_result.get("content")
            tool_calls = llm_result.get("tool_calls", [])

            if tool_calls:
                # Append assistant message with tool_calls for API consistency
                state.messages.append({
                    "role": "assistant",
                    "content": content or "",
                    "tool_calls": [
                        {
                            "id": tc.get("id", f"call_{i}"),
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": tc.get("arguments", {})
                            }
                        }
                        for i, tc in enumerate(tool_calls)
                    ]
                })

                # LLM wants to run one or more tools
                for tc in tool_calls:
                    tool_name = tc["name"]
                    arguments = tc.get("arguments", {})

                    # Check permission
                    if PermissionManager.requires_permission(tool_name):
                        # Create permission request in database
                        req = PermissionManager.create_request(
                            tool_name=tool_name,
                            parameters=arguments,
                            description=f"Action: {tool_name} with {json.dumps(arguments)}",
                            reason=f"Authorizing execution of {tool_name}"
                        )

                        state.steps.append(AgentStep(
                            step_number=step_counter,
                            action_type="permission_request",
                            tool_name=tool_name,
                            arguments=arguments,
                            status_message=f"Waiting for student authorization to execute {tool_name}..."
                        ))
                        step_counter += 1

                        state.status = "waiting_for_permission"
                        state.permission_request = {
                            "id": req.id,
                            "tool_name": tool_name,
                            "parameters": arguments,
                            "description": req.description,
                            "reason": req.reason
                        }

                        # Store state to resume once approved/denied
                        self.pending_tasks[req.id] = (state, tc)
                        self._persist_conversation(state)
                        return state

                    # LOW RISK tool - execute immediately
                    state.steps.append(AgentStep(
                        step_number=step_counter,
                        action_type="tool_select",
                        tool_name=tool_name,
                        arguments=arguments,
                        status_message=f"Executing {tool_name}..."
                    ))
                    step_counter += 1

                    # Real tool execution
                    result = tool_registry.execute(tool_name, arguments)
                    
                    # Log in audit
                    PermissionManager.log_audit(
                        "TOOL_EXECUTE",
                        tool_name,
                        f"Executed {tool_name}: success={result.get('success', True)}"
                    )

                    state.steps.append(AgentStep(
                        step_number=step_counter,
                        action_type="tool_result",
                        tool_name=tool_name,
                        result=result,
                        status_message=f"Completed {tool_name}"
                    ))
                    step_counter += 1

                    # Check if file was generated
                    if result.get("file_path"):
                        state.referenced_files.append({
                            "name": result.get("file_name", "Generated File"),
                            "path": result.get("file_path"),
                            "url": result.get("download_url")
                        })

                    # Append tool message back to conversation for observation
                    state.messages.append({
                        "role": "tool",
                        "content": json.dumps(result)
                    })

                # Loop continues so LLM observes tool outputs
                continue

            # No tool calls - LLM produced final response
            final_text = content or "Task completed successfully."
            state.final_response = final_text
            state.status = "completed"

            state.steps.append(AgentStep(
                step_number=step_counter,
                action_type="final_response",
                status_message="Response generated."
            ))

            PermissionManager.log_audit("TASK_COMPLETE", None, f"Task finished: '{task[:60]}...'")
            self._persist_conversation(state)
            return state

        # If loop reached max_turns without final text, synthesize
        state.final_response = "I have performed the required actions for your task."
        state.status = "completed"
        self._persist_conversation(state)
        return state

    def resume_permission(self, request_id: str, approved: bool) -> AgentState:
        """Resumes a paused agent execution after approval or denial."""
        pending = self.pending_tasks.pop(request_id, None)
        if not pending:
            # Fallback reconstruct
            raise ValueError(f"No active pending agent task for permission request {request_id}")

        state, tool_call = pending
        tool_name = tool_call["name"]
        arguments = tool_call.get("arguments", {})
        step_counter = len(state.steps) + 1

        if approved:
            # Update DB permission record
            PermissionManager.approve_request(request_id)

            state.steps.append(AgentStep(
                step_number=step_counter,
                action_type="tool_select",
                tool_name=tool_name,
                arguments=arguments,
                status_message=f"Permission granted. Executing {tool_name}..."
            ))
            step_counter += 1

            # Execute authorized sensitive tool
            result = tool_registry.execute(tool_name, arguments)
            PermissionManager.log_audit(
                "TOOL_EXECUTE",
                tool_name,
                f"Authorized execution of {tool_name}: success={result.get('success', True)}"
            )

            state.steps.append(AgentStep(
                step_number=step_counter,
                action_type="tool_result",
                tool_name=tool_name,
                result=result,
                status_message=f"Completed {tool_name}"
            ))
            step_counter += 1

            state.messages.append({
                "role": "tool",
                "content": json.dumps(result)
            })

        else:
            # Denied
            PermissionManager.deny_request(request_id)
            state.steps.append(AgentStep(
                step_number=step_counter,
                action_type="tool_result",
                tool_name=tool_name,
                result={"success": False, "status": "permission_denied"},
                status_message=f"Permission denied for {tool_name}. Operation canceled."
            ))
            step_counter += 1

            state.messages.append({
                "role": "tool",
                "content": json.dumps({
                    "success": False,
                    "status": "permission_denied",
                    "message": f"User explicitly clicked DENY for {tool_name}. Do NOT execute this action. Acknowledge the cancellation."
                })
            })

        # Clear permission request object on state
        state.permission_request = None
        state.status = "executing"

        # Resume LLM to formulate completion response
        tools_schema = tool_registry.get_relevant_tools(state.task)
        llm_result = llm_client.chat(messages=state.messages, tools=tools_schema)
        final_text = llm_result.get("content") or f"Action {tool_name} {'completed' if approved else 'was canceled by your decision'}."

        state.final_response = final_text
        state.status = "completed"

        state.steps.append(AgentStep(
            step_number=step_counter,
            action_type="final_response",
            status_message="Response generated."
        ))

        self._persist_conversation(state)
        return state

    def _load_conversation_history(self, conversation_id: str) -> list[dict[str, Any]]:
        db = SessionLocal()
        try:
            msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc()).all()
            history = []
            for m in msgs[-10:]:  # last 10 messages for context
                role = "assistant" if m.sender == "assistant" else "user"
                history.append({"role": role, "content": m.content})
            return history
        finally:
            db.close()

    def _persist_conversation(self, state: AgentState):
        db = SessionLocal()
        try:
            conv = db.query(Conversation).filter(Conversation.id == state.conversation_id).first()
            if not conv:
                conv = Conversation(
                    id=state.conversation_id,
                    title=state.task[:60] if state.task else "Study Session"
                )
                db.add(conv)

            # Record assistant message if completed
            if state.final_response:
                steps_json = json.dumps([s.model_dump() for s in state.steps])
                files_json = json.dumps(state.referenced_files)
                msg = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=state.conversation_id,
                    sender="assistant",
                    content=state.final_response,
                    steps_json=steps_json,
                    files_json=files_json,
                    timestamp=datetime.utcnow()
                )
                db.add(msg)
            db.commit()
        finally:
            db.close()

agent_engine = AgentEngine()
