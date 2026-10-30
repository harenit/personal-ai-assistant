from typing import Any, Optional
from backend.tools.base import BaseTool
from backend.permissions.models import RiskLevel
from backend.integrations.lms.mock_lms import MockLMSProvider

lms_provider = MockLMSProvider()

class GetCoursesTool(BaseTool):
    name = "get_courses"
    description = "Retrieve the list of enrolled university courses, professors, schedules, and classrooms from the LMS."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {}
    }

    def execute(self, **kwargs) -> dict[str, Any]:
        courses = lms_provider.get_courses()
        return {
            "success": True,
            "count": len(courses),
            "courses": courses
        }

class GetAssignmentsTool(BaseTool):
    name = "get_assignments"
    description = "Retrieve all academic assignments from the LMS, including title, course, points, due date, and submission status."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "course_id": {
                "type": "string",
                "description": "Optional course ID or code to filter assignments"
            }
        }
    }

    def execute(self, course_id: Optional[str] = None, **kwargs) -> dict[str, Any]:
        assignments = lms_provider.get_assignments(course_id=course_id)
        return {
            "success": True,
            "count": len(assignments),
            "assignments": assignments
        }

class GetUpcomingAssignmentsTool(BaseTool):
    name = "get_upcoming_assignments"
    description = "Retrieve pending assignments due soon (within the next specified number of days, e.g. 7 days)."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "days_ahead": {
                "type": "integer",
                "description": "Number of days ahead to look for due assignments (default 7)",
                "default": 7
            }
        }
    }

    def execute(self, days_ahead: int = 7, **kwargs) -> dict[str, Any]:
        try:
            days_ahead = int(days_ahead)
        except (ValueError, TypeError):
            days_ahead = 7
        assignments = lms_provider.get_upcoming_assignments(days_ahead=days_ahead)
        return {
            "success": True,
            "count": len(assignments),
            "assignments": assignments,
            "message": f"Found {len(assignments)} pending assignment(s) due within {days_ahead} days."
        }

class GetOverdueAssignmentsTool(BaseTool):
    name = "get_overdue_assignments"
    description = "Retrieve assignments whose deadline has passed and have not yet been submitted."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {}
    }

    def execute(self, **kwargs) -> dict[str, Any]:
        assignments = lms_provider.get_overdue_assignments()
        return {
            "success": True,
            "count": len(assignments),
            "overdue_assignments": assignments
        }

class GetExamsTool(BaseTool):
    name = "get_exams"
    description = "Retrieve the exam schedule from the LMS, including upcoming midterms, quizzes, and finals with date, time, room, and syllabus topics."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {}
    }

    def execute(self, **kwargs) -> dict[str, Any]:
        exams = lms_provider.get_exams()
        return {
            "success": True,
            "count": len(exams),
            "exams": exams
        }

class GetAnnouncementsTool(BaseTool):
    name = "get_announcements"
    description = "Retrieve course announcements, university bulletins, and notices posted by professors."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {}
    }

    def execute(self, **kwargs) -> dict[str, Any]:
        announcements = lms_provider.get_announcements()
        return {
            "success": True,
            "count": len(announcements),
            "announcements": announcements
        }

class SubmitAssignmentTool(BaseTool):
    name = "submit_assignment"
    description = "Submit student work or assignment solutions to the official university LMS. (SENSITIVE ACTION: Requires student confirmation)."
    risk_level = RiskLevel.SENSITIVE
    parameters = {
        "type": "object",
        "properties": {
            "assignment_id": {
                "type": "string",
                "description": "ID or title of the assignment to submit"
            },
            "submission_text": {
                "type": "string",
                "description": "Content, repository URL, or textual solution for submission"
            }
        },
        "required": ["assignment_id", "submission_text"]
    }

    def execute(self, assignment_id: str, submission_text: str, **kwargs) -> dict[str, Any]:
        return lms_provider.submit_assignment(assignment_id, submission_text)
