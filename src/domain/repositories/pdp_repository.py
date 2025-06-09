from abc import ABC, abstractmethod
from datetime import date
from typing import List

from src.domain.entities.pdp_record import PDPRecord


class PDPRepository(ABC):
    """Repository interface for PDP records"""

    @abstractmethod
    async def get_by_filters(
        self, dates: List[date], agent_emails: List[str]
    ) -> List[PDPRecord]:
        """Get PDP records filtered by specific dates and emails"""
        pass
