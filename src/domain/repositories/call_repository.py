from abc import ABC, abstractmethod
from datetime import date
from typing import List

from src.domain.entities.call_data import AgentCallData


class CallRepository(ABC):
    """Repository interface for external call"""

    @abstractmethod
    async def get_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[AgentCallData]:
        """
        Get all agents call data for a date range
        """
        pass
