from dataclasses import dataclass
from datetime import date


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
        if not self.agent_name:
            raise ValueError("Agent name cannot be empty")

        if not self.dni:
            raise ValueError("DNI cannot be empty")

        if self.hour < 0 or self.hour > 23:
            raise ValueError("Hour must be between 0 and 23")

        if self.pdp_count < 0:
            raise ValueError("PDP count cannot be negative")

        if self.total_operations < 0:
            raise ValueError("Total operations cannot be negative")
