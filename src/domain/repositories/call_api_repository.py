from abc import ABC, abstractmethod
from datetime import date
from typing import List, Dict

from src.domain.entities.call_data import CallApiResponse
from src.domain.value_objects.email import Email


class CallApiRepository(ABC):
    """Repository interface for external call API"""

    @abstractmethod
    async def get_agent_calls(
        self, agent_email: Email, query_date: date
    ) -> CallApiResponse:
        """Get call data for a specific agent on a specific date"""
        pass

    @abstractmethod
    async def get_multiple_agents_calls(
        self, agents_data: List[Dict[str, any]], query_date: date
    ) -> Dict[str, CallApiResponse]:
        """Get call data for multiple agents (batch operation)"""
        pass
