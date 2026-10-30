import logging
from typing import Any, Optional
from backend.tools.base import BaseTool
from backend.tools.system_tools import (
    OpenApplicationTool, CloseApplicationTool, OpenUrlTool,
    OpenGeneratedFileTool, OpenFolderTool
)
from backend.tools.lms_tools import (
    GetCoursesTool, GetAssignmentsTool, GetUpcomingAssignmentsTool,
    GetOverdueAssignmentsTool, GetExamsTool, GetAnnouncementsTool,
    SubmitAssignmentTool
)
from backend.tools.email_tools import (
    ListEmailsTool, SearchEmailsTool, ReadEmailTool, DraftReplyTool, SendEmailTool
)
from backend.tools.calendar_tools import (
    ListEventsTool, GetUpcomingEventsTool, CreateCalendarEventTool, CancelCalendarEventTool
)
from backend.tools.reminder_tools import (
    CreateReminderTool, ListRemindersTool, DeleteReminderTool
)
from backend.tools.study_tools import (
    SummarizeDocumentTool, AskDocumentQuestionTool, GenerateQuizTool,
    GenerateFlashcardsTool, GenerateStudyPlanTool
)
from backend.tools.ppt_tools import GeneratePresentationTool
from backend.tools.search_tools import SearchWebTool, SearchYouTubeTool
from backend.tools.drive_tools import (
    SearchFilesTool, ReadFileContentTool, OpenDriveFolderTool, GetSystemTelemetryTool
)

logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._register_default_tools()

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_openai_tools(self) -> list[dict[str, Any]]:
        return [tool.to_openai_tool() for tool in self._tools.values()]

    def get_relevant_tools(self, query: str) -> list[dict[str, Any]]:
        """Dynamically filters tools based on task context to optimize local LLM latency."""
        q = (query or "").lower()
        selected_tool_names: set[str] = set()

        categories = {
            "lms": [
                "assignment", "assignments", "homework", "due", "deadline", "course", 
                "courses", "exam", "exams", "announcement", "announcements", "lms", "grade",
                "cs401", "cs350", "cs480", "math310", "canvas", "blackboard", "moodle"
            ],
            "email": [
                "email", "emails", "mail", "inbox", "professor", "prof", "reply", "draft", "send"
            ],
            "calendar": [
                "calendar", "event", "events", "schedule", "meeting", "tomorrow", "session"
            ],
            "reminders": [
                "reminder", "reminders", "remind", "alarm", "break"
            ],
            "presentation": [
                "presentation", "presentations", "slide", "slides", "powerpoint", "pptx", "deck"
            ],
            "study": [
                "quiz", "quizzes", "flashcard", "flashcards", "summarize", "summary", 
                "study", "plan", "document", "notes", "pdf", "docx"
            ],
            "search": [
                "youtube", "video", "tutorial", "tutorials", "search", "web", "google", "find"
            ],
            "system": [
                "open", "launch", "calculator", "calc", "notepad", "browser", "folder", "app", "application", "close"
            ],
            "drive": [
                "drive", "google drive", "onedrive", "file", "files", "document", "documents", "search file", "find file", "downloads", "desktop", "storage"
            ],
            "telemetry": [
                "telemetry", "cpu", "ram", "battery", "system load", "performance", "specs", "hardware"
            ]
        }

        tool_category_map = {
            "lms": ["get_upcoming_assignments", "get_assignments", "get_overdue_assignments", "get_exams", "get_announcements", "get_courses", "submit_assignment"],
            "email": ["list_emails", "search_emails", "read_email", "draft_reply", "send_email"],
            "calendar": ["get_upcoming_events", "list_events", "create_calendar_event", "cancel_calendar_event"],
            "reminders": ["create_reminder", "list_reminders", "delete_reminder"],
            "presentation": ["generate_presentation", "open_generated_file"],
            "study": ["summarize_document", "ask_document_question", "generate_quiz", "generate_flashcards", "generate_study_plan"],
            "search": ["search_youtube", "search_web", "open_url"],
            "system": ["open_application", "close_application", "open_url", "open_folder", "open_generated_file"],
            "drive": ["search_files", "read_file_content", "open_drive_folder", "open_folder", "open_generated_file"],
            "telemetry": ["get_system_telemetry"]
        }

        matched_categories = []
        for cat, keywords in categories.items():
            if any(k in q for k in keywords):
                matched_categories.append(cat)

        # Broad student questions: "what should I work on first?", "what do I need to finish today?"
        if any(phrase in q for phrase in ["work on", "finish today", "today", "priorit", "overview", "what should i"]):
            if "lms" not in matched_categories:
                matched_categories.append("lms")
            if "calendar" not in matched_categories:
                matched_categories.append("calendar")
            if "email" not in matched_categories:
                matched_categories.append("email")

        # If no specific categories matched, default to general university & system tools
        if not matched_categories:
            matched_categories = ["lms", "system", "email", "calendar"]

        for cat in matched_categories:
            for t_name in tool_category_map.get(cat, []):
                selected_tool_names.add(t_name)

        if "open" in q or "launch" in q:
            selected_tool_names.add("open_application")
            selected_tool_names.add("open_url")
            selected_tool_names.add("open_generated_file")

        # Score tools based on query relevance and cap at 5 for maximum local LLM speed
        def score_tool(name: str) -> int:
            score = 0
            for word in q.split():
                if len(word) > 2 and word in name.lower():
                    score += 4
            if ("search" in q or "find" in q) and ("file" in q or "drive" in q) and name in ["search_files", "open_drive_folder"]:
                score += 12
            if ("calc" in q or "notepad" in q or "open" in q) and name == "open_application":
                score += 10
            if "assign" in q and "assignment" in name:
                score += 8
            if "exam" in q and "exam" in name:
                score += 8
            if ("email" in q or "mail" in q or "prof" in q) and "email" in name:
                score += 8
            if ("slide" in q or "presentation" in q) and "presentation" in name:
                score += 10
            return score

        sorted_names = sorted(list(selected_tool_names), key=score_tool, reverse=True)[:5]

        selected_tools = [
            self._tools[t_name].to_openai_tool() 
            for t_name in sorted_names 
            if t_name in self._tools
        ]

        if len(selected_tools) < 2:
            return self.get_openai_tools()[:5]

        return selected_tools

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self.get(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' is not registered in the system."
            }

        try:
            logger.info(f"Executing tool {tool_name} with arguments: {arguments}")
            return tool.execute(**arguments)
        except TypeError as e:
            return {
                "success": False,
                "error": f"Invalid arguments supplied to {tool_name}: {str(e)}"
            }
        except Exception as e:
            logger.exception(f"Tool {tool_name} raised unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing {tool_name}: {str(e)}"
            }

    def _register_default_tools(self):
        # System control tools
        self.register(OpenApplicationTool())
        self.register(CloseApplicationTool())
        self.register(OpenUrlTool())
        self.register(OpenGeneratedFileTool())
        self.register(OpenFolderTool())

        # LMS tools
        self.register(GetCoursesTool())
        self.register(GetAssignmentsTool())
        self.register(GetUpcomingAssignmentsTool())
        self.register(GetOverdueAssignmentsTool())
        self.register(GetExamsTool())
        self.register(GetAnnouncementsTool())
        self.register(SubmitAssignmentTool())

        # Email tools
        self.register(ListEmailsTool())
        self.register(SearchEmailsTool())
        self.register(ReadEmailTool())
        self.register(DraftReplyTool())
        self.register(SendEmailTool())

        # Calendar tools
        self.register(ListEventsTool())
        self.register(GetUpcomingEventsTool())
        self.register(CreateCalendarEventTool())
        self.register(CancelCalendarEventTool())

        # Reminder tools
        self.register(CreateReminderTool())
        self.register(ListRemindersTool())
        self.register(DeleteReminderTool())

        # Study & RAG tools
        self.register(SummarizeDocumentTool())
        self.register(AskDocumentQuestionTool())
        self.register(GenerateQuizTool())
        self.register(GenerateFlashcardsTool())
        self.register(GenerateStudyPlanTool())

        # Presentation tool
        self.register(GeneratePresentationTool())

        # Search tools
        self.register(SearchWebTool())
        self.register(SearchYouTubeTool())

        # Drive & Telemetry tools
        self.register(SearchFilesTool())
        self.register(ReadFileContentTool())
        self.register(OpenDriveFolderTool())
        self.register(GetSystemTelemetryTool())

tool_registry = ToolRegistry()
