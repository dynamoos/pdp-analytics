from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class PDPRecord:
    """Entity representing a PDP (Payment Promise) record"""

    record_date: date
    dni: str
    agent_name: str
    promises_per_hour: Decimal

    def __post_init__(self):
        """Entity validations"""
        if not self.agent_name:
            raise ValueError("Agent name cannot be empty")

        if not self.dni:
            raise ValueError("DNI cannot be empty")

        if self.promises_per_hour < 0:
            raise ValueError("Promises per hour cannot be negative")

    @property
    def agent_identifier(self) -> str:
        """Get agent unique identifier"""
        return self.dni.value
