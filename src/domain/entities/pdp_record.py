from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class PDPRecord:
    """Entity representing a PDP (Payment Promise) record"""

    record_date: date
    hour: int
    dni: str
    agent_name: str
    total_operations: int
    effective_contacts: int
    no_contacts: int
    non_effective_contacts: int
    pdp_count: int

    def __post_init__(self):
        """Entity validations"""
        if not self.agent_name:
            raise ValueError("Agent name cannot be empty")

        if self.hour < 0 or self.hour > 23:
            raise ValueError("Hour must be between 0 and 23")

        if self.pdp_count < 0:
            raise ValueError("PDP count cannot be negative")

        if self.total_operations < 0:
            raise ValueError("Total operations cannot be negative")

    @property
    def agent_identifier(self) -> str:
        """Get agent unique identifier"""
        return self.dni

    @property
    def pdp_per_hour(self) -> Decimal:
        """Calculate PDP per hour - assuming each record represents one hour of work"""
        return Decimal(str(self.pdp_count))
