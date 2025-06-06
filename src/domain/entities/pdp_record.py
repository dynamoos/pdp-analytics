from dataclasses import dataclass
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

    # From API calls (optional)
    total_connected_seconds: Optional[int] = None
    total_time_hms: Optional[str] = None

    # Calculated metric for heatmap
    pdp_per_hour: Optional[Decimal] = None

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
    def average_pdp_per_day(self) -> float:
        """Calculate average PDPs per day"""
        if self.days_with_pdp == 0:
            return 0.0
        return self.pdp_count / self.days_with_pdp

    @property
    def effectiveness_rate(self) -> float:
        """Calculate effectiveness (documents with debt / total operations)"""
        if self.total_pdp_operations == 0:
            return 0.0
        return self.documents_with_debt / self.total_pdp_operations

    @property
    def connected_hours(self) -> Optional[float]:
        """Convert seconds to hours if available"""
        if self.total_connected_seconds is None:
            return None
        return self.total_connected_seconds / 3600
