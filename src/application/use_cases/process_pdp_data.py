import time
from datetime import date
from decimal import Decimal
from typing import Dict, List

from loguru import logger

from src.application.dto.pdp_dto import PDPRequestDTO, PDPResponseDTO
from src.application.services.excel_service import ExcelService
from src.domain.entities.pdp_record import PDPRecord
from src.domain.repositories.call_api_repository import CallApiRepository
from src.domain.repositories.pdp_repository import PDPRepository
from src.shared.exceptions import UseCaseException


class ProcessPDPDataUseCase:
    """Use case for processing PDP data with call enrichment"""

    def __init__(
        self,
        pdp_repository: PDPRepository,
        call_api_repository: CallApiRepository,
        excel_service: ExcelService,
    ):
        self._pdp_repository = pdp_repository
        self._call_api_repository = call_api_repository
        self._excel_service = excel_service

    async def execute(self, request: PDPRequestDTO) -> PDPResponseDTO:
        """Execute the use case"""
        start_time = time.time()
        errors = []

        try:
            # Step 1: Get PDP records from BigQuery
            logger.info(
                f"Fetching PDP records from {request.start_date} to {request.end_date}"
            )
            pdp_records = await self._pdp_repository.get_by_date_range(
                start_date=request.start_date,
                end_date=request.end_date,
            )

            if not pdp_records:
                raise UseCaseException(
                    "No PDP records found for the specified criteria"
                )

            logger.info(f"Found {len(pdp_records)} PDP records")

            # Step 2: Enrich with call data if requested
            if request.include_call_data:
                pdp_records = await self._enrich_with_call_data(pdp_records, errors)

            # Step 3: Calculate productivity metrics
            pdp_records = self._calculate_productivity_metrics(pdp_records)

            # Step 4: Generate Excel report
            excel_path = await self._excel_service.generate_pdp_report(
                pdp_records=pdp_records, include_heatmap=request.generate_heatmap
            )

            # Step 5: Calculate summary metrics
            total_pdps = sum(record.pdp_count for record in pdp_records)
            total_amount = sum(record.total_managed_amount for record in pdp_records)

            processing_time = time.time() - start_time

            return PDPResponseDTO(
                total_records=len(pdp_records),
                total_pdps=total_pdps,
                total_amount=total_amount,
                excel_file_path=excel_path,
                processing_time_seconds=processing_time,
                errors=errors if errors else None,
            )

        except Exception as e:
            logger.error(f"Error processing PDP data: {str(e)}")
            raise UseCaseException(f"Failed to process PDP data: {str(e)}")

    async def _enrich_with_call_data(
        self, pdp_records: List[PDPRecord], errors: List[str]
    ) -> List[PDPRecord]:
        """Enrich PDP records with call data from external API"""
        logger.info("Enriching PDP records with call data")

        # Group records by date for batch processing
        records_by_date: Dict[date, List[PDPRecord]] = {}
        for record in pdp_records:
            if record.record_date not in records_by_date:
                records_by_date[record.record_date] = []
            records_by_date[record.record_date].append(record)

        enriched_records = []

        # Process each date
        for query_date, date_records in records_by_date.items():
            # Prepare batch request
            agents_data = [
                {"email": record.agent_email, "dni": record.dni}
                for record in date_records
            ]

            # Get call data for all agents on this date
            try:
                call_responses = (
                    await self._call_api_repository.get_multiple_agents_calls(
                        agents_data=agents_data, query_date=query_date
                    )
                )

                # Match call data with PDP records
                for record in date_records:
                    api_email = record.agent_email.api_format

                    if (
                        api_email in call_responses
                        and call_responses[api_email].success
                    ):
                        call_data = (
                            call_responses[api_email].data[0]
                            if call_responses[api_email].data
                            else None
                        )

                        if call_data:
                            # Create new record with call data
                            enriched_record = PDPRecord(
                                **{
                                    field: getattr(record, field)
                                    for field in record.__dataclass_fields__
                                    if field
                                    not in ["total_connected_seconds", "total_time_hms"]
                                },
                                total_connected_seconds=call_data.total_connected_seconds,
                                total_time_hms=call_data.total_time_hms,
                            )
                            enriched_records.append(enriched_record)
                        else:
                            enriched_records.append(record)
                    else:
                        errors.append(
                            f"Failed to get call data for {record.agent_email.value} on {query_date}"
                        )
                        enriched_records.append(record)

            except Exception as e:
                logger.error(f"Error fetching call data for {query_date}: {str(e)}")
                errors.append(f"API error for date {query_date}: {str(e)}")
                enriched_records.extend(date_records)

        logger.info(f"Enriched {len(enriched_records)} records with call data")
        return enriched_records

    def _calculate_productivity_metrics(
        self, pdp_records: List[PDPRecord]
    ) -> List[PDPRecord]:
        """Calculate productivity metrics (PDPs per hour)"""
        calculated_records = []

        for record in pdp_records:
            if record.total_connected_seconds and record.total_connected_seconds > 0:
                hours_connected = record.total_connected_seconds / 3600
                pdp_per_hour = Decimal(str(record.pdp_count / hours_connected))
            else:
                pdp_per_hour = Decimal("0")

            # Create new record with calculated metric
            calculated_record = PDPRecord(
                **{
                    field: getattr(record, field)
                    for field in record.__dataclass_fields__
                    if field != "pdp_per_hour"
                },
                pdp_per_hour=pdp_per_hour,
            )
            calculated_records.append(calculated_record)

        return calculated_records
