from dataclasses import dataclass
from datetime import date
from typing import Optional, List
from decimal import Decimal


@dataclass
class PDPRequestDTO:
    """DTO for PDP processing request"""

    start_date: date
    end_date: date
    service_type: Optional[str] = None
    portfolio: Optional[str] = None
    include_call_data: bool = True
    generate_heatmap: bool = True


@dataclass
class PDPResponseDTO:
    """DTO for PDP processing response"""

    total_records: int
    total_pdps: int
    total_amount: Decimal
    excel_file_path: str
    processing_time_seconds: float
    errors: List[str] = None


@dataclass
class AgentMetricsDTO:
    """DTO for agent metrics in heatmap"""

    dni: str
    agent_name: str
    date: date
    pdp_count: int
    connected_hours: float
    pdp_per_hour: float
    total_amount: Decimal
