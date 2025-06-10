from datetime import date
from typing import Any, Dict, List

from google.cloud.bigquery.query import ScalarQueryParameter
from loguru import logger

from src.domain.entities.pdp_record import PDPRecord
from src.domain.repositories.productivity_repository import ProductivityRepository
from src.infrastructure.database.bigquery_client import BigQueryClient
from src.infrastructure.database.queries.pdp_queries import PDPQueries
from src.shared.exceptions import RepositoryException


class BigQueryProductivityRepository(ProductivityRepository):
    """BigQuery implementation of ProductivityRepository"""

    def __init__(self, client: BigQueryClient):
        self._client = client
        self._queries = PDPQueries()

    async def get_by_filters(self, start_date: date, end_date: date) -> List[PDPRecord]:
        logger.info(f"Fetching productivity data from {start_date} to {end_date}")
        try:
            query = self._queries.get_pdps_by_filters(start_date, end_date)

            parameters = [
                ScalarQueryParameter("start_date", "DATE", start_date),
                ScalarQueryParameter("end_date", "DATE", end_date),
            ]

            rows = await self._client.execute_query(query, parameters)
            logger.info(f"Fetched {len(rows)} productivity records")
            return [self._map_row_to_entity(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to fetch PDP records: {str(e)}")
            raise RepositoryException(f"Failed to fetch PDP records: {str(e)}") from e

    @staticmethod
    def _map_row_to_entity(row: Dict[str, Any]) -> PDPRecord:
        dni = (
            str(row["dni_ejecutivo"]) if row["dni_ejecutivo"] is not None else "SIN DNI"
        )
        return PDPRecord(
            record_date=row["fecha"],
            hour=row["hora"],
            dni=dni,
            agent_name=row["ejecutivo"],
            total_operations=row["total_gestiones"],
            effective_contacts=row["contactos_efectivos"],
            no_contacts=row["no_contactos"],
            non_effective_contacts=row["contactos_no_efectivos"],
            pdp_count=row["gestiones_pdp"],
        )
