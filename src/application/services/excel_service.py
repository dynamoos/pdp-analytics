from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from src.application.dto.excel_dto import ExcelGenerationDTO, HeatmapConfig, SheetConfig
from src.domain.entities.pdp_record import PDPRecord
from src.infrastructure.excel.excel_generator import ExcelGenerator
from src.infrastructure.excel.heatmap_formatter import HeatmapFormatter
from src.shared.constants import EXCEL_OUTPUT_PATH, ExcelHeaders


class ExcelService:
    """Service for generating Excel reports"""

    def __init__(self, output_path: str = EXCEL_OUTPUT_PATH):
        self._output_path = Path(output_path)
        self._output_path.mkdir(exist_ok=True)
        self._excel_generator = ExcelGenerator()
        self._heatmap_formatter = HeatmapFormatter()

    async def generate_pdp_report(
        self, pdp_records: List[PDPRecord], include_heatmap: bool = True
    ) -> str:
        logger.info(f"Generating Excel report for {len(pdp_records)} records")

        records_data = self._convert_records_to_dict(pdp_records)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pdp_report_{timestamp}.xlsx"
        filepath = self._output_path / filename

        sheet_configs = [
            SheetConfig(
                sheet_name="Datos_Detalle",
                data=records_data,
                headers=list(ExcelHeaders.__dict__.values()),
                apply_filters=True,
            )
        ]

        if include_heatmap:
            heatmap_data = self._prepare_heatmap_data(pdp_records)
            sheet_configs.append(
                SheetConfig(
                    sheet_name="Mapa_Calor",
                    data=heatmap_data,
                    headers=["DNI", "Nombre", "Supervisor"]
                    + [str(i) for i in range(1, 32)],
                    heatmap_config=HeatmapConfig(value_column="pdp_per_hour"),
                )
            )

        excel_dto = ExcelGenerationDTO(
            output_filename=str(filepath), sheet_configs=sheet_configs
        )

        self._generate_excel_file(excel_dto)

        logger.info(f"Excel report generated: {filepath}")
        return str(filepath)

    @staticmethod
    def _convert_records_to_dict(pdp_records: List[PDPRecord]) -> List[Dict[str, Any]]:
        """Convert PDP records to dictionary format for Excel"""
        return [
            {
                ExcelHeaders.YEAR: record.period.year,
                ExcelHeaders.MONTH: record.period.month,
                ExcelHeaders.DAY: record.record_date.day,
                ExcelHeaders.DATE: record.record_date.strftime("%Y-%m-%d"),
                ExcelHeaders.PERIOD: record.period.formatted,
                ExcelHeaders.SERVICE: record.service_type,
                ExcelHeaders.PORTFOLIO: record.portfolio,
                ExcelHeaders.DUE_DAY: record.due_day,
                ExcelHeaders.DNI: record.dni,
                ExcelHeaders.AGENT_NAME: record.agent_full_name,
                ExcelHeaders.AGENT_EMAIL: record.agent_email.value,
                ExcelHeaders.PDP_COUNT: record.pdp_count,
                ExcelHeaders.TOTAL_OPERATIONS: record.total_pdp_operations,
                ExcelHeaders.MANAGED_AMOUNT: float(record.total_managed_amount),
                ExcelHeaders.CONNECTED_TIME: record.total_time_hms or "00:00:00",
                "PDPs por Hora": (
                    float(record.pdp_per_hour) if record.pdp_per_hour else 0
                ),
            }
            for record in pdp_records
        ]

    def _prepare_heatmap_data(
        self, pdp_records: List[PDPRecord]
    ) -> List[Dict[str, Any]]:
        """Prepare data for heatmap visualization"""
        # Group records by month
        records_by_month = {}
        for record in pdp_records:
            month_key = (record.period.year, record.period.month)
            if month_key not in records_by_month:
                records_by_month[month_key] = []
            records_by_month[month_key].append(
                {
                    "dni": record.dni,
                    "agent_name": record.agent_full_name,
                    "day": record.record_date.day,
                    "pdp_per_hour": (
                        float(record.pdp_per_hour) if record.pdp_per_hour else 0
                    ),
                }
            )

        # For now, use the first month (or implement month selection)
        if records_by_month:
            (year, month), month_records = list(records_by_month.items())[0]
            heatmap_df = self._heatmap_formatter.format_productivity_heatmap(
                month_records, month, year
            )
            return heatmap_df.to_dict("records")

        return []

    def _generate_excel_file(self, excel_dto: ExcelGenerationDTO):
        """Generate Excel file using infrastructure component"""
        self._excel_generator.generate(excel_dto)
