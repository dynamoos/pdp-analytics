from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from typing import Optional

from src.domain.value_objects.email import Email
from src.domain.value_objects.period import Period


@dataclass(frozen=True)
class PDPRecord:
    """Entity representing a PDP (Payment Promise) record"""

    # Agent identification
    dni: str
    agent_full_name: str
    agent_email: Email

    # Temporal information
    record_date: date
    period: Period
    month_name: str

    # Classification
    service_type: str
    portfolio: str
    due_day: int

    # Metrics from BigQuery
    pdp_count: int
    total_pdp_operations: int
    total_managed_amount: Decimal
    days_with_pdp: int
    documents_with_debt: int
    average_amount_per_document: Decimal

    total_connected_seconds: Optional[int] = None

    def __post_init__(self):
        """Entity validations"""
        if self.pdp_count < 0:
            raise ValueError("PDP count cannot be negative")

        if self.total_managed_amount < 0:
            raise ValueError("Total managed amount cannot be negative")

        if self.due_day < 0 or self.due_day > 31:
            raise ValueError("Due day must be between 0 and 31")

        if self.service_type not in ["MOVIL", "FIJA", "Sin Servicio"]:
            raise ValueError(f"Invalid service type: {self.service_type}")

    @property
    def connected_hours(self) -> str:
        hours = self.total_connected_seconds // 3600
        minutes = (self.total_connected_seconds % 3600) // 60
        seconds = self.total_connected_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def pdp_per_hour(self) -> Decimal:
        if self.total_connected_seconds and self.total_connected_seconds > 0:
            hours = Decimal(str(self.total_connected_seconds)) / Decimal("3600")
            return Decimal(str(self.pdp_count)) / hours
        return Decimal("0")

    def with_connected_time(self, seconds: Optional[int]) -> "PDPRecord":
        return replace(self, total_connected_seconds=seconds)
