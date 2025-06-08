from dataclasses import dataclass
from datetime import date

from src.domain.value_objects.email import Email


@dataclass(frozen=True)
class AgentCallData:
    """Agent call data for a specific date"""

    agent_email: Email
    call_date: date
    total_connected_seconds: int

    def __post_init__(self):
        if self.total_connected_seconds < 0:
            raise ValueError("Connected time cannot be negative")
