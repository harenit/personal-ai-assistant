from pathlib import Path
from backend.tools.system_tools import OpenApplicationTool, OpenUrlTool
from backend.tools.lms_tools import GetCoursesTool, GetUpcomingAssignmentsTool, GetExamsTool
from backend.tools.email_tools import ListEmailsTool, SearchEmailsTool, DraftReplyTool
from backend.tools.calendar_tools import ListEventsTool, GetUpcomingEventsTool
from backend.tools.reminder_tools import CreateReminderTool, ListRemindersTool
from backend.tools.ppt_tools import GeneratePresentationTool
from backend.tools.search_tools import SearchWebTool, SearchYouTubeTool

def test_system_tools_allowlist():
    tool = OpenApplicationTool()
    # Test disallowed app
    res = tool.execute(application_name="malicious_cmd.exe")
    assert res["success"] is False
    assert "allowlist" in res["message"].lower()

def test_lms_tools():
    courses_tool = GetCoursesTool()
    c_res = courses_tool.execute()
    assert c_res["success"] is True
    assert c_res["count"] >= 4

    assign_tool = GetUpcomingAssignmentsTool()
    a_res = assign_tool.execute(days_ahead=7)
    assert a_res["success"] is True
    assert isinstance(a_res["assignments"], list)

    exams_tool = GetExamsTool()
    e_res = exams_tool.execute()
    assert e_res["success"] is True
    assert e_res["count"] >= 2

def test_email_tools():
    list_tool = ListEmailsTool()
    l_res = list_tool.execute(limit=5)
    assert l_res["success"] is True
    assert len(l_res["emails"]) > 0

    search_tool = SearchEmailsTool()
    s_res = search_tool.execute(query="Midterm")
    assert s_res["success"] is True
    assert len(s_res["emails"]) > 0

    draft_tool = DraftReplyTool()
    d_res = draft_tool.execute(email_id=s_res["emails"][0]["id"], reply_text="I will review the study materials.")
    assert d_res["success"] is True

def test_calendar_tools():
    cal_tool = ListEventsTool()
    res = cal_tool.execute()
    assert res["success"] is True
    assert res["count"] >= 4

def test_reminder_tools():
    create_tool = CreateReminderTool()
    res = create_tool.execute(title="Automated Test Reminder", due_datetime="tomorrow at 5 PM")
    assert res["success"] is True

    list_tool = ListRemindersTool()
    l_res = list_tool.execute()
    assert l_res["success"] is True
    titles = [r["title"] for r in l_res["reminders"]]
    assert "Automated Test Reminder" in titles

def test_presentation_generation():
    ppt_tool = GeneratePresentationTool()
    res = ppt_tool.execute(topic="Artificial Intelligence Test", slide_count=4)
    assert res["success"] is True
    file_path = Path(res["file_path"])
    assert file_path.exists()
    assert file_path.suffix == ".pptx"
    assert file_path.stat().st_size > 1000

def test_search_tools():
    search_tool = SearchWebTool()
    res = search_tool.execute(query="binary search trees tutorial", max_results=2)
    assert res["success"] is True
    assert len(res["results"]) > 0

    yt_tool = SearchYouTubeTool()
    yt_res = yt_tool.execute(query="machine learning tutorial", max_results=2)
    assert yt_res["success"] is True
    assert len(yt_res["videos"]) > 0
