from datetime import datetime
from typing import Any, Optional
from backend.tools.base import BaseTool
from backend.permissions.models import RiskLevel
from backend.integrations.calendar.mock_calendar import MockCalendarProvider

calendar_provider = MockCalendarProvider()

class ListEventsTool(BaseTool):
    name = "list_events"
    description = "List all calendar events, lectures, study sessions, and exams."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {}
    }

    def execute(self, **kwargs) -> dict[str, Any]:
        events = calendar_provider.list_events()
        return {
            "success": True,
            "count": len(events),
            "events": events
        }

class GetUpcomingEventsTool(BaseTool):
    name = "get_upcoming_events"
    description = "Get upcoming events and commitments scheduled for the next specified number of hours (e.g. 24 or 48 hours)."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "hours_ahead": {
                "type": "integer",
                "description": "Hours ahead to inspect (default 48)",
                "default": 48
            }
        }
    }

    def execute(self, hours_ahead: int = 48, **kwargs) -> dict[str, Any]:
        try:
            hours_ahead = int(hours_ahead)
        except (ValueError, TypeError):
            hours_ahead = 48
        events = calendar_provider.get_upcoming_events(hours_ahead=hours_ahead)
        return {
            "success": True,
            "count": len(events),
            "events": events,
            "message": f"Found {len(events)} upcoming event(s) in the next {hours_ahead} hours."
        }

class CreateCalendarEventTool(BaseTool):
    name = "create_calendar_event"
    description = "Create and schedule a new event on the student's calendar. (SENSITIVE ACTION: Requires student confirmation)."
    risk_level = RiskLevel.SENSITIVE
    parameters = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Title of the calendar event (e.g. 'Study Group for AI')"
            },
            "start_time": {
                "type": "string",
                "description": "Start datetime in format 'YYYY-MM-DD HH:MM' or ISO format"
            },
            "end_time": {
                "type": "string",
                "description": "End datetime in format 'YYYY-MM-DD HH:MM' or ISO format"
            },
            "location": {
                "type": "string",
                "description": "Location of event (default 'Campus')",
                "default": "Campus"
            },
            "event_type": {
                "type": "string",
                "description": "Type of event: 'study', 'class', 'personal', 'exam'",
                "default": "study"
            },
            "description": {
                "type": "string",
                "description": "Optional notes or details",
                "default": ""
            }
        },
        "required": ["title", "start_time", "end_time"]
    }

    def execute(self, title: str, start_time: str, end_time: str, location: str = "Campus", event_type: str = "study", description: str = "", **kwargs) -> dict[str, Any]:
        try:
            try:
                dt_start = datetime.fromisoformat(start_time)
            except ValueError:
                dt_start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            try:
                dt_end = datetime.fromisoformat(end_time)
            except ValueError:
                dt_end = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

            return calendar_provider.create_event(
                title=title,
                start_datetime=dt_start,
                end_datetime=dt_end,
                location=location,
                event_type=event_type,
                description=description
            )
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to parse datetime or create calendar event: {str(e)}"
            }

class CancelCalendarEventTool(BaseTool):
    name = "cancel_calendar_event"
    description = "Cancel or remove a scheduled event from the student calendar. (SENSITIVE ACTION: Requires student confirmation)."
    risk_level = RiskLevel.SENSITIVE
    parameters = {
        "type": "object",
        "properties": {
            "event_id": {
                "type": "string",
                "description": "ID or exact title of the calendar event to cancel"
            }
        },
        "required": ["event_id"]
    }

    def execute(self, event_id: str, **kwargs) -> dict[str, Any]:
        return calendar_provider.cancel_event(event_id)
