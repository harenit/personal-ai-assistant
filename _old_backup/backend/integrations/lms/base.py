from abc import ABC, abstractmethod
from typing import Any, Optional

class LMSProvider(ABC):
    @abstractmethod
    def get_courses(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_assignments(self, course_id: Optional[str] = None) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_upcoming_assignments(self, days_ahead: int = 7) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_overdue_assignments(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_exams(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_announcements(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def submit_assignment(self, assignment_id: str, submission_text: str) -> dict[str, Any]:
        pass
