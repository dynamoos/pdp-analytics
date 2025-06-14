import time

from loguru import logger

from src.application.dto import SheetConfig
from src.application.dto.pdp_dto import PDPRequestDTO, PDPResponseDTO
from src.application.ports.repositories import ProductivityRepository
from src.application.ports.services import DataTransformationService
from src.application.services.excel_service import ExcelService
from src.domain.entities import PDPRecord
from src.domain.value_objects.period import Period


class ProcessPDPDataUseCase:
    """Use case for processing PDP data"""

    def __init__(
        self,
        productivity_repository: ProductivityRepository,
        excel_service: ExcelService,
        data_transformation_service: DataTransformationService,
    ):
        self._productivity_repository = productivity_repository
        self._excel_service = excel_service
        self._data_transformation_service = data_transformation_service

    HEATMAP_METRICS = [
        {
            "field": "pdp_count",
            "sheet_name": "PDP por Hora",
            "heatmap_ranges": {"high": 3.0, "medium": 2.0},
        },
        {
            "field": "total_operations",
            "sheet_name": "Operaciones por Hora",
            "heatmap_ranges": {"high": 29, "medium": 19.33},
        },
    ]

    async def execute(self, request: PDPRequestDTO) -> PDPResponseDTO:
        """Execute the use case"""
        start_time = time.time()

        try:
            period = Period.from_date(request.reference_date)
            records = await self._fetch_productivity_records(period)

            if not records:
                return self._create_empty_response(period, start_time)

            sheet_configs = self._create_sheet_configurations(records)
            excel_path = await self._excel_service.generate_from_sheet_configs(
                sheet_configs, filename_prefix="pdp_report"
            )

            return PDPResponseDTO(
                total_records=len(records),
                unique_agents=len({record.agent_name for record in records}),
                excel_file_path=excel_path.split("/")[-1],
                processing_time_seconds=time.time() - start_time,
                period=f"{period.year}-{period.month}",
            )

        except Exception as e:
            logger.error(f"Error processing productivity data: {str(e)}")
            return self._create_error_response(str(e), start_time)

    async def _fetch_productivity_records(self, period: Period) -> list[PDPRecord]:
        """Fetch productivity records for the given period."""
        start_date, end_date = period.get_date_range()

        logger.info(
            f"Processing productivity data for period {period.year}-{period.month} "
            f"({start_date} to {end_date})"
        )

        records = await self._productivity_repository.get_by_filters(
            start_date, end_date
        )

        if records:
            logger.info(f"Found {len(records)} productivity records")
        else:
            logger.warning("No productivity data found")

        return records

    def _create_sheet_configurations(
        self, records: list[PDPRecord]
    ) -> list[SheetConfig]:
        sheet_configs = [self._create_detail_sheet_config(records, "DETALLE")]

        sheet_configs.extend(
            self._create_heatmap_sheet_config(
                records,
                metric_field=metric_config["field"],
                sheet_name=metric_config["sheet_name"],
                heatmap_ranges=metric_config["heatmap_ranges"],
            )
            for metric_config in self.HEATMAP_METRICS
        )

        return sheet_configs

    def _create_detail_sheet_config(
        self, records: list[PDPRecord], sheet_name: str = None
    ) -> SheetConfig:
        """Create configuration for detailed data sheet."""
        detailed_data = self._data_transformation_service.transform_to_tabular_format(
            records
        )

        return SheetConfig(
            sheet_name=sheet_name,
            data=detailed_data,
            apply_filters=True,
            heatmap_ranges=None,
        )

    def _create_heatmap_sheet_config(
        self,
        records: list[PDPRecord],
        metric_field: str,
        heatmap_ranges: dict,
        sheet_name: str,
    ) -> SheetConfig:
        """Create configuration for heatmap sheet."""
        heatmap_data = self._data_transformation_service.create_productivity_heatmap(
            records, metric_field=metric_field
        )
        return SheetConfig(
            sheet_name=sheet_name,
            data=heatmap_data,
            apply_filters=False,
            heatmap_ranges=heatmap_ranges,
        )

    @staticmethod
    def _create_empty_response(period: Period, start_time: float) -> PDPResponseDTO:
        """Create response when no data is found."""
        processing_time = time.time() - start_time
        return PDPResponseDTO.empty(
            processing_time=processing_time,
            errors=[
                f"No productivity data found for period {period.year}-{period.month}"
            ],
        )

    @staticmethod
    def _create_error_response(error_message: str, start_time: float) -> PDPResponseDTO:
        """Create error response DTO."""
        processing_time = time.time() - start_time
        return PDPResponseDTO.with_error(
            error_message=f"Failed to process productivity data: {error_message}",
            processing_time=processing_time,
        )
