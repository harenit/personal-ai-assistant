from abc import ABC, abstractmethod
from typing import Any

class SearchProvider(ABC):
    @abstractmethod
    def search_web(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def search_youtube(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        pass
