from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
from pathlib import Path

from src.domain.entities.pdp_record import PDPRecord
from src.application.dto.excel_dto import ExcelGenerationDTO, SheetConfig, HeatmapConfig
from src.shared.constants import ExcelHeaders, EXCEL_OUTPUT_PATH
from loguru import logger


class ExcelService:
    """Service for generating Excel reports"""

    def __init__(self, output_path: str = EXCEL_OUTPUT_PATH):
        self._output_path = Path(output_path)
        self._output_path.mkdir(exist_ok=True)

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

    def _convert_records_to_dict(
        self, pdp_records: List[PDPRecord]
    ) -> List[Dict[str, Any]]:
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
        df = pd.DataFrame(
            [
                {
                    "dni": record.dni,
                    "name": record.agent_full_name,
                    "day": record.record_date.day,
                    "pdp_per_hour": (
                        float(record.pdp_per_hour) if record.pdp_per_hour else 0
                    ),
                }
                for record in pdp_records
            ]
        )

        # Pivot to create matrix
        pivot = df.pivot_table(
            values="pdp_per_hour", index=["dni", "name"], columns="day", fill_value=0
        )

        heatmap_data = []
        for (dni, name), row in pivot.iterrows():
            row_data = {"DNI": dni, "Nombre": name, "Supervisor": "N/A"}
            for day in range(1, 32):
                row_data[str(day)] = row.get(day, 0)
            heatmap_data.append(row_data)

        return heatmap_data

    def _generate_excel_file(self, excel_dto: ExcelGenerationDTO):
        """Placeholder for Excel generation - will be implemented in infrastructure"""
        # This will be replaced by the actual Excel generator in infrastructure
        pass
