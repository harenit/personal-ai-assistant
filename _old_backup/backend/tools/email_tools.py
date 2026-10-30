from typing import Any, Optional
from backend.tools.base import BaseTool
from backend.permissions.models import RiskLevel
from backend.integrations.email.mock_email import MockEmailProvider

email_provider = MockEmailProvider()

class ListEmailsTool(BaseTool):
    name = "list_emails"
    description = "List recent academic emails from professors, departments, and university advisors."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of emails to retrieve (default 10)",
                "default": 10
            },
            "unread_only": {
                "type": "boolean",
                "description": "Whether to only fetch unread emails",
                "default": False
            }
        }
    }

    def execute(self, limit: int = 10, unread_only: bool = False, **kwargs) -> dict[str, Any]:
        emails = email_provider.list_emails(limit=limit, unread_only=unread_only)
        return {
            "success": True,
            "count": len(emails),
            "emails": emails
        }

class SearchEmailsTool(BaseTool):
    name = "search_emails"
    description = "Search emails by keyword, professor name, subject, or academic topic (e.g. 'assignment', 'midterm', 'extension', 'office hours')."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search keyword or sender to look up in emails"
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return (default 5)",
                "default": 5
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, limit: int = 5, **kwargs) -> dict[str, Any]:
        emails = email_provider.search_emails(query=query, limit=limit)
        return {
            "success": True,
            "query": query,
            "count": len(emails),
            "emails": emails,
            "message": f"Found {len(emails)} matching email(s) for query '{query}'."
        }

class ReadEmailTool(BaseTool):
    name = "read_email"
    description = "Read the full text content of a specific email by its ID or subject keyword."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "email_id": {
                "type": "string",
                "description": "ID or subject of the email to read"
            }
        },
        "required": ["email_id"]
    }

    def execute(self, email_id: str, **kwargs) -> dict[str, Any]:
        email = email_provider.read_email(email_id=email_id)
        if not email:
            return {
                "success": False,
                "message": f"No email found matching ID or title '{email_id}'."
            }
        return {
            "success": True,
            "email": email
        }

class DraftReplyTool(BaseTool):
    name = "draft_reply"
    description = "Prepare a polite, professional email draft reply to a professor or advisor for student review."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "email_id": {
                "type": "string",
                "description": "ID or subject of the email being replied to"
            },
            "reply_text": {
                "type": "string",
                "description": "The message body drafted for the reply"
            }
        },
        "required": ["email_id", "reply_text"]
    }

    def execute(self, email_id: str, reply_text: str, **kwargs) -> dict[str, Any]:
        return email_provider.draft_reply(email_id=email_id, reply_text=reply_text)

class SendEmailTool(BaseTool):
    name = "send_email"
    description = "Send an email to a professor, advisor, or classmate. (SENSITIVE ACTION: Requires explicit student permission before transmission)."
    risk_level = RiskLevel.SENSITIVE
    parameters = {
        "type": "object",
        "properties": {
            "recipient": {
                "type": "string",
                "description": "Recipient email address (e.g. professor@university.edu)"
            },
            "subject": {
                "type": "string",
                "description": "Email subject line"
            },
            "body": {
                "type": "string",
                "description": "Email message body"
            }
        },
        "required": ["recipient", "subject", "body"]
    }

    def execute(self, recipient: str, subject: str, body: str, **kwargs) -> dict[str, Any]:
        return email_provider.send_email(recipient=recipient, subject=subject, body=body)
