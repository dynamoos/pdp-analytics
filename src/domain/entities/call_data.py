from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from src.domain.value_objects.email import Email


@dataclass(frozen=True)
class AgentCallData:
    """Agent call data for a specific date"""

    agent_email: Email
    call_date: date
    total_connected_seconds: int
    total_time_hms: str

    def __post_init__(self):
        """Validations"""
        if self.total_connected_seconds < 0:
            raise ValueError("Connected time cannot be negative")

    @property
    def connected_hours(self) -> float:
        """Convert seconds to hours"""
        return self.total_connected_seconds / 3600


@dataclass(frozen=True)
class CallApiResponse:
    """Call API response wrapper"""

    success: bool
    data: List[AgentCallData]
    error_message: Optional[str] = None

    @classmethod
    def from_error(cls, error_message: str) -> "CallApiResponse":
        """Factory method to create error response"""
        return cls(success=False, data=[], error_message=error_message)
