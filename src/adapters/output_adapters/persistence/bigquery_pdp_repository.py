from datetime import date
from decimal import Decimal
from typing import Any, Dict, List

from google.cloud.bigquery.query import ArrayQueryParameter
from loguru import logger

from src.domain.entities.pdp_record import PDPRecord
from src.domain.repositories.pdp_repository import PDPRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.period import Period
from src.infrastructure.database.bigquery_client import BigQueryClient
from src.infrastructure.database.queries.pdp_queries import PDPQueries
from src.shared.exceptions import RepositoryException


class BigQueryPDPRepository(PDPRepository):
    """BigQuery implementation of PDPRepository"""

    def __init__(self, client: BigQueryClient):
        self._client = client
        self._queries = PDPQueries()

    async def get_by_filters(
        self, dates: List[date], agent_emails: List[str]
    ) -> List[PDPRecord]:
        logger.info(
            f"Fetching PDP records for {len(dates)} dates "
            f"and {len(agent_emails)} agents"
        )
        try:
            query = self._queries.get_pdps_by_filters(dates, agent_emails)

            parameters = [
                ArrayQueryParameter("dates", "DATE", dates),
                ArrayQueryParameter("emails", "STRING", agent_emails),
            ]

            rows = await self._client.execute_query(query, parameters)
            logger.info(f"Fetched {len(rows)} call data records")
            return [self._map_row_to_entity(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to fetch PDP records: {str(e)}")
            raise RepositoryException(f"Failed to fetch PDP records: {str(e)}") from e

    @staticmethod
    def _map_row_to_entity(row: Dict[str, Any]) -> PDPRecord:
        return PDPRecord(
            dni=str(row["dni"]),
            agent_full_name=row["nombre_apellidos"],
            agent_email=Email(row["usuario"]),
            record_date=row["fecha"],
            period=Period(year=row["anio"], month=row["mes"]),
            month_name=row["nombre_mes"],
            service_type=row["servicio"],
            portfolio=row["cartera"],
            due_day=row["vencimiento"],
            pdp_count=row["cant_pdp"],
            total_pdp_operations=row["total_gestiones_pdp"],
            total_managed_amount=Decimal(str(row["monto_total_gestionado"])),
            days_with_pdp=row["dias_con_pdp"],
            documents_with_debt=row["documentos_con_deuda"],
            average_amount_per_document=Decimal(
                str(row["monto_promedio_por_documento"])
            ),
            total_connected_seconds=None,
        )
