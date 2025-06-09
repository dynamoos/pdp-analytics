from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional


@dataclass
class PDPRequestDTO:
    """DTO for PDP processing request"""

    reference_date: date


@dataclass
class PDPResponseDTO:
    """DTO for PDP processing response"""

    total_records: int
    unique_agents: int
    average_productivity: Decimal
    excel_file_path: str
    processing_time_seconds: float
    period: str
    errors: Optional[List[str]] = None

    def __post_init__(self):
        if self.average_productivity is not None:
            self.average_productivity = Decimal(
                str(self.average_productivity)
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if self.processing_time_seconds is not None:
            self.processing_time_seconds = round(self.processing_time_seconds, 2)

        if self.errors is None:
            self.errors = []

    @classmethod
    def empty(
        cls, processing_time: float = 0.0, errors: List[str] = None
    ) -> "PDPResponseDTO":
        """Create an empty response when no data is found"""
        return cls(
            total_records=0,
            unique_agents=0,
            average_productivity=Decimal("0"),
            excel_file_path="",
            processing_time_seconds=processing_time,
            period="",
            errors=errors or [],
        )

    @classmethod
    def with_error(
        cls, error_message: str, processing_time: float = 0.0
    ) -> "PDPResponseDTO":
        """Create a response with error"""
        return cls(
            total_records=0,
            unique_agents=0,
            average_productivity=Decimal("0"),
            excel_file_path="",
            processing_time_seconds=processing_time,
            period="",
            errors=[error_message],
        )
