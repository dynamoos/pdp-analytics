from typing import List

from src.domain.entities.pdp_record import PDPRecord
from src.application.services.excel_service import ExcelService
from src.shared.exceptions import UseCaseException
from loguru import logger


class GenerateExcelReportUseCase:
    """Use case for generating Excel report from existing PDP data"""

    def __init__(self, excel_service: ExcelService):
        self._excel_service = excel_service

    async def execute(
        self,
        pdp_records: List[PDPRecord],
        output_filename: str = None,
        include_heatmap: bool = True,
    ) -> str:
        """Generate Excel report from PDP records"""
        try:
            if not pdp_records:
                raise UseCaseException("No PDP records provided for report generation")

            logger.info(f"Generating Excel report for {len(pdp_records)} records")

            excel_path = await self._excel_service.generate_pdp_report(
                pdp_records=pdp_records, include_heatmap=include_heatmap
            )

            return excel_path

        except Exception as e:
            logger.error(f"Error generating Excel report: {str(e)}")
            raise UseCaseException(f"Failed to generate Excel report: {str(e)}")
