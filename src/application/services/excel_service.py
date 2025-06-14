from datetime import datetime
from pathlib import Path

from loguru import logger

from src.application.dto import ExcelGenerationDTO, SheetConfig
from src.infrastructure.excel import ExcelGenerator


class ExcelService:
    """Service for generating Excel reports"""

    def __init__(self, output_path: str, excel_generator: ExcelGenerator):
        self._output_path = Path(output_path)
        self._output_path.mkdir(exist_ok=True)
        self._excel_generator = excel_generator

    async def generate_from_sheet_configs(
        self, sheet_configs: list[SheetConfig], filename_prefix: str = "report"
    ) -> str:
        """
        Generate Excel report from sheet configurations.

        Args:
            sheet_configs: List of sheet configurations
            filename_prefix: Prefix for the filename

        Returns:
            Path to generated Excel file
        """
        logger.info(f"Generating Excel report with {len(sheet_configs)} sheets")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        filepath = self._output_path / filename

        excel_dto = ExcelGenerationDTO(
            output_filename=str(filepath), sheet_configs=sheet_configs
        )

        self._excel_generator.generate(excel_dto)
        logger.info(f"Excel report generated: {filepath}")
        return str(filepath)
