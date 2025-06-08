import time
from decimal import Decimal
from typing import List

from loguru import logger

from src.application.dto.pdp_dto import PDPRequestDTO, PDPResponseDTO
from src.domain.entities.call_data import AgentCallData
from src.domain.entities.pdp_record import PDPRecord
from src.domain.repositories.call_repository import CallRepository
from src.domain.repositories.pdp_repository import PDPRepository


class ProcessPDPDataUseCase:
    """Use case for processing PDP data with call enrichment"""

    def __init__(
        self,
        pdp_repository: PDPRepository,
        call_repository: CallRepository,
        # excel_service: ExcelService,
    ):
        self._pdp_repository = pdp_repository
        self._call_repository = call_repository
        # self._excel_service = excel_service

    async def execute(self, request: PDPRequestDTO) -> PDPResponseDTO:
        """Execute the use case"""
        start_time = time.time()
        errors = []

        try:
            call_data = await self._call_repository.get_by_date_range(
                request.start_date, request.end_date
            )
            if not call_data:
                logger.warning("No call data found")
                processing_time = time.time() - start_time
                return PDPResponseDTO.empty(
                    processing_time=processing_time,
                    errors=["No call data found for the specified period"],
                )

            available_dates = set(record.call_date for record in call_data)
            available_emails = set(record.agent_email.value for record in call_data)

            logger.info(
                f"Found {len(available_dates)} dates and "
                f"{len(available_emails)} unique agents with call data"
            )

            pdp_records = await self._pdp_repository.get_by_filters(
                dates=list(available_dates), agent_emails=list(available_emails)
            )

            logger.info(f"Found {len(pdp_records)} PDP records")

            enriched_records = await self._enrich_with_call_data(pdp_records, call_data)

            csv_path = await self._save_to_csv(enriched_records)

            total_pdps = sum(record.pdp_count for record in enriched_records)
            total_amount = sum(
                record.total_managed_amount for record in enriched_records
            )
            processing_time = time.time() - start_time

            return PDPResponseDTO(
                total_records=len(enriched_records),
                total_pdps=total_pdps,
                total_amount=Decimal(total_amount),
                excel_file_path=csv_path,
                processing_time_seconds=processing_time,
                errors=errors if errors else None,
            )

        except Exception as e:
            logger.error(f"Error processing PDP data: {str(e)}")

            processing_time = time.time() - start_time

            return PDPResponseDTO.with_error(
                error_message=f"Failed to process PDP data: {str(e)}",
                processing_time=processing_time,
            )

    @staticmethod
    async def _enrich_with_call_data(
        pdp_records: List[PDPRecord], call_data: List[AgentCallData]
    ) -> List[PDPRecord]:
        call_lookup = {
            (call.agent_email.value.lower(), call.call_date): call for call in call_data
        }

        from collections import defaultdict

        pdp_groups = defaultdict(list)
        for pdp in pdp_records:
            pdp_groups[(pdp.agent_email.value.lower(), pdp.record_date)].append(pdp)

        enriched_records = []

        for (email, date), pdp_list in pdp_groups.items():
            call = call_lookup.get((email, date))

            if call:
                total_seconds = call.total_connected_seconds
                total_pdps = sum(p.pdp_count for p in pdp_list)

                for pdp in pdp_list:
                    weight = pdp.pdp_count / total_pdps if total_pdps > 0 else 0
                    weighted_seconds = int(total_seconds * weight)
                    enriched_records.append(pdp.with_connected_time(weighted_seconds))
            else:
                enriched_records.extend(pdp_list)

        return enriched_records

    @staticmethod
    async def _save_to_csv(records: List[PDPRecord]) -> str:
        """Save enriched PDP records to CSV for testing"""
        import csv
        from datetime import datetime
        from pathlib import Path

        output_dir = Path("output/csv")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"enriched_pdp_data_{timestamp}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "fecha",
                "dni",
                "nombre_agente",
                "email",
                "servicio",
                "cartera",
                "vencimiento",
                "periodo",
                "mes",
                "pdp_count",
                "total_operaciones",
                "monto_gestionado",
                "dias_con_pdp",
                "documentos_con_deuda",
                "monto_promedio",
                "segundos_conectado",
                "tiempo_conectado_hms",
                "pdp_por_hora",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for record in records:
                writer.writerow(
                    {
                        "fecha": record.record_date.isoformat(),
                        "dni": record.dni,
                        "nombre_agente": record.agent_full_name,
                        "email": record.agent_email.value,
                        "servicio": record.service_type,
                        "cartera": record.portfolio,
                        "vencimiento": record.due_day,
                        "periodo": f"{record.period.year}-{record.period.month:02d}",
                        "mes": record.month_name,
                        "pdp_count": record.pdp_count,
                        "total_operaciones": record.total_pdp_operations,
                        "monto_gestionado": float(record.total_managed_amount),
                        "dias_con_pdp": record.days_with_pdp,
                        "documentos_con_deuda": record.documents_with_debt,
                        "monto_promedio": float(record.average_amount_per_document),
                        "segundos_conectado": record.total_connected_seconds or 0,
                        "tiempo_conectado_hms": (
                            record.connected_hours
                            if record.total_connected_seconds
                            else ""
                        ),
                        "pdp_por_hora": (
                            float(record.pdp_per_hour)
                            if record.total_connected_seconds
                            else 0
                        ),
                    }
                )

        logger.info(f"✅ Saved {len(records)} records to {filename}")
        return str(filename)
