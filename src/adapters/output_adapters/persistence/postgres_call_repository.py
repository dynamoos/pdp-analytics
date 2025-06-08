from datetime import date
from typing import Any, Dict, List

from loguru import logger

from src.domain.entities.call_data import AgentCallData
from src.domain.repositories.call_repository import CallRepository
from src.domain.value_objects.email import Email
from src.infrastructure.database.postgres_manager import PostgresManager
from src.shared.exceptions import RepositoryException


class PostgresCallRepository(CallRepository):
    """Postgres implementation of PDPRepository"""

    def __init__(self, postgres_manager: PostgresManager):
        self._session_manager = postgres_manager

    async def get_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[AgentCallData]:
        logger.info(f"Fetching call data from {start_date} to {end_date}")

        query = """
            SELECT date, email, total_seconds 
            FROM agent_connected_times
            WHERE date >= $1 AND date <= $2
            ORDER BY date, email
        """

        try:
            rows = await self._session_manager.fetch_all(query, start_date, end_date)
            logger.info(f"Fetched {len(rows)} call data records")
            return [self._map_row_to_entity(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch call data: {str(e)}")
            raise RepositoryException(f"Failed to fetch call data: {str(e)}") from e

    @staticmethod
    def _map_row_to_entity(row: Dict[str, Any]) -> AgentCallData:
        return AgentCallData(
            agent_email=Email(row["email"]),
            call_date=row["date"],
            total_connected_seconds=row["total_seconds"],
        )
