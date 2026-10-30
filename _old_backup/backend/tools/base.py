from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel
from backend.permissions.models import RiskLevel

class BaseTool(ABC):
    name: str
    description: str
    risk_level: RiskLevel = RiskLevel.LOW_RISK
    parameters: dict[str, Any]  # JSON Schema definition for tool inputs

    @abstractmethod
    def execute(self, **kwargs) -> dict[str, Any]:
        """Execute the tool safely and return a structured JSON response."""
        pass

    def to_openai_tool(self) -> dict[str, Any]:
        """Format the tool schema for LLM tool/function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
