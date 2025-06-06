from abc import ABC, abstractmethod
from datetime import date
from typing import List

from src.domain.entities.pdp_record import PDPRecord


class PDPRepository(ABC):
    """Repository interface for PDP records"""

    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> List[PDPRecord]:
        """Get PDP records within a date range"""
        pass
