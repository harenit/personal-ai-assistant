from abc import ABC, abstractmethod
from typing import Any, Optional

class EmailProvider(ABC):
    @abstractmethod
    def list_emails(self, limit: int = 10, unread_only: bool = False) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def search_emails(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def read_email(self, email_id: str) -> Optional[dict[str, Any]]:
        pass

    @abstractmethod
    def draft_reply(self, email_id: str, reply_text: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def send_email(self, recipient: str, subject: str, body: str) -> dict[str, Any]:
        pass
