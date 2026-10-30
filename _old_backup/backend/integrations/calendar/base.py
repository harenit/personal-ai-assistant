from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime

class CalendarProvider(ABC):
    @abstractmethod
    def list_events(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_upcoming_events(self, hours_ahead: int = 48) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def create_event(
        self,
        title: str,
        start_datetime: datetime,
        end_datetime: datetime,
        location: str = "Campus",
        event_type: str = "study",
        description: str = ""
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def cancel_event(self, event_id: str) -> dict[str, Any]:
        pass
