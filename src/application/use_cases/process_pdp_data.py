import time
from decimal import Decimal
from typing import List

from loguru import logger

from src.application.dto.pdp_dto import PDPRequestDTO, PDPResponseDTO
from src.application.services.excel_service import ExcelService
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
        excel_service: ExcelService,
    ):
        self._pdp_repository = pdp_repository
        self._call_repository = call_repository
        self._excel_service = excel_service

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

            excel_path = await self._excel_service.generate_pdp_report(
                pdp_records=enriched_records
            )

            total_pdps = sum(record.pdp_count for record in enriched_records)
            total_amount = sum(
                record.total_managed_amount for record in enriched_records
            )
            processing_time = time.time() - start_time

            return PDPResponseDTO(
                total_records=len(enriched_records),
                total_pdps=total_pdps,
                total_amount=Decimal(total_amount),
                excel_file_path=excel_path,
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
                enriched_records.extend(
                    [pdp.with_connected_time(None) for pdp in pdp_list]
                )

        return enriched_records
