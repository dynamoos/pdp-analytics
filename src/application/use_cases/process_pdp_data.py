import time

from loguru import logger

from src.application.dto.pdp_dto import PDPRequestDTO, PDPResponseDTO
from src.application.services.excel_service import ExcelService
from src.domain.repositories.productivity_repository import ProductivityRepository
from src.domain.value_objects.period import Period


class ProcessPDPDataUseCase:
    """Use case for processing PDP data"""

    def __init__(
        self,
        productivity_repository: ProductivityRepository,
        excel_service: ExcelService,
    ):
        self._productivity_repository = productivity_repository
        self._excel_service = excel_service

    async def execute(self, request: PDPRequestDTO) -> PDPResponseDTO:
        """Execute the use case"""
        start_time = time.time()
        errors = []

        try:
            # Calculate month range based on provided date
            period = Period.from_date(request.reference_date)
            start_date, end_date = period.get_date_range()

            logger.info(
                f"Processing productivity data for period {period.formatted} "
                f"({start_date} to {end_date})"
            )

            # Get productivity data
            records = await self._productivity_repository.get_by_filters(
                start_date, end_date
            )

            if not records:
                logger.warning("No productivity data found")
                processing_time = time.time() - start_time
                return PDPResponseDTO.empty(
                    processing_time=processing_time,
                    errors=[
                        f"No productivity data found for period {period.formatted}"
                    ],
                )
            logger.info(f"Found {len(records)} productivity records")

            # Generate Excel report
            excel_path = await self._excel_service.generate_pdp_report(records)

            # Calculate statistics
            unique_agents = len(set(record.agent_name for record in records))

            processing_time = time.time() - start_time

            return PDPResponseDTO(
                total_records=len(records),
                unique_agents=unique_agents,
                excel_file_path=excel_path.split("/")[-1],
                processing_time_seconds=processing_time,
                period=period.formatted,
                errors=errors if errors else None,
            )

        except Exception as e:
            logger.error(f"Error processing productivity data: {str(e)}")
            processing_time = time.time() - start_time
            return PDPResponseDTO.with_error(
                error_message=f"Failed to process productivity data: {str(e)}",
                processing_time=processing_time,
            )
