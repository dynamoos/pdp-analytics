from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from src.domain.entities.pdp_record import PDPRecord
from src.domain.value_objects.period import Period


class PDPRepository(ABC):
    """Repository interface for PDP records"""

    @abstractmethod
    async def get_by_period(
        self,
        period: Period,
        service_type: Optional[str] = None,
        portfolio: Optional[str] = None,
    ) -> List[PDPRecord]:
        """Get PDP records for a specific period with optional filters"""
        pass

    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        service_type: Optional[str] = None,
        portfolio: Optional[str] = None,
    ) -> List[PDPRecord]:
        """Get PDP records within a date range"""
        pass

    @abstractmethod
    async def get_by_agent_dni(
        self, dni: str, period: Optional[Period] = None
    ) -> List[PDPRecord]:
        """Get PDP records for a specific agent"""
        pass
