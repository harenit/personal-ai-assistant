from backend.permissions.manager import PermissionManager
from backend.permissions.models import RiskLevel, PermissionStatus

def test_risk_classification():
    # Sensitive
    assert PermissionManager.requires_permission("send_email") is True
    assert PermissionManager.requires_permission("submit_assignment") is True
    assert PermissionManager.requires_permission("create_calendar_event") is True

    # Low risk
    assert PermissionManager.requires_permission("get_assignments") is False
    assert PermissionManager.requires_permission("open_application") is False
    assert PermissionManager.requires_permission("generate_presentation") is False
    assert PermissionManager.requires_permission("create_reminder") is False

def test_permission_request_workflow():
    req = PermissionManager.create_request(
        tool_name="send_email",
        parameters={"recipient": "prof@univ.edu", "subject": "Test", "body": "Hello"},
        description="Send email to Professor",
        reason="Testing permission workflow"
    )
    assert req.id is not None
    assert req.status == PermissionStatus.PENDING.value

    # Approve
    approved = PermissionManager.approve_request(req.id)
    assert approved.status == PermissionStatus.APPROVED.value

    # Create another to test Deny
    req2 = PermissionManager.create_request(
        tool_name="submit_assignment",
        parameters={"assignment_id": "test_1", "submission_text": "Code"},
        description="Submit assignment",
        reason="Testing denial"
    )
    denied = PermissionManager.deny_request(req2.id)
    assert denied.status == PermissionStatus.DENIED.value
