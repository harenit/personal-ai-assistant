import uuid
from backend.agent.engine import agent_engine

def test_agent_assignments_query():
    state = agent_engine.run_task(
        task="Do I have any assignments due this week?",
        conversation_id=str(uuid.uuid4())
    )
    assert state.status in ["completed", "waiting_for_permission"]
    # Check that tool steps were generated
    assert len(state.steps) >= 1
    # Check that final response is populated
    assert state.final_response is not None
    assert len(state.final_response) > 10

def test_agent_sensitive_action_interception():
    # User asks to send email directly
    state = agent_engine.run_task(
        task="Send an email to prof@university.edu saying I need an extension on my project.",
        conversation_id=str(uuid.uuid4())
    )
    # The agent should either draft the email or attempt to send it and get intercepted for permission
    if state.status == "waiting_for_permission":
        assert state.permission_request is not None
        assert state.permission_request["tool_name"] == "send_email"
        # Test approval resumption
        approved_state = agent_engine.resume_permission(state.permission_request["id"], approved=True)
        assert approved_state.status == "completed"
        assert approved_state.final_response is not None
