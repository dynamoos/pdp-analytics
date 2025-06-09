from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from src.application.dto.excel_dto import ExcelGenerationDTO, HeatmapConfig, SheetConfig
from src.domain.entities.pdp_record import PDPRecord
from src.infrastructure.excel.excel_generator import ExcelGenerator
from src.shared.constants import EXCEL_OUTPUT_PATH


class ExcelService:
    """Service for generating Excel reports"""

    def __init__(
        self,
        output_path: str = EXCEL_OUTPUT_PATH,
        excel_generator: ExcelGenerator = None,
    ):
        self._output_path = Path(output_path)
        self._output_path.mkdir(exist_ok=True)
        self._excel_generator = excel_generator or ExcelGenerator()

    async def generate_pdp_report(
        self,
        pdp_records: List[PDPRecord],
    ) -> str:
        logger.info(f"Generating Excel report for {len(pdp_records)} records")

        heatmap_data = self._prepare_heatmap_data(pdp_records)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pdp_report_{timestamp}.xlsx"
        filepath = self._output_path / filename

        # Get unique days from data
        unique_days = sorted(set(record.record_date.day for record in pdp_records))
        day_columns = [str(day) for day in unique_days]

        headers = ["DNI", "SUPERVISOR"] + day_columns + ["Total"]

        sheet_configs = [
            SheetConfig(
                sheet_name="Productividad",
                data=heatmap_data,
                headers=headers,
                apply_filters=False,
                heatmap_config=HeatmapConfig(value_column="promises_per_hour"),
            )
        ]

        excel_dto = ExcelGenerationDTO(
            output_filename=str(filepath), sheet_configs=sheet_configs
        )

        self._excel_generator.generate(excel_dto)
        logger.info(f"Excel report generated: {filepath}")
        return str(filepath)

    @staticmethod
    def _prepare_heatmap_data(pdp_records: List[PDPRecord]) -> List[Dict[str, Any]]:
        """Prepare data for heatmap visualization"""

        agent_data = {}

        logger.info(f"Preparing heatmap for {len(pdp_records)} records")

        for record in pdp_records:
            if record.dni not in agent_data:
                agent_data[record.dni] = {
                    "DNI": record.dni,
                    "SUPERVISOR": record.agent_name,
                    "days_with_data": 0,
                    "Total": 0,
                }
            day = str(record.record_date.day)
            agent_data[record.dni][day] = float(record.promises_per_hour)
            agent_data[record.dni]["days_with_data"] += 1
            agent_data[record.dni]["Total"] += float(record.promises_per_hour)

        # Round totals
        for agent in agent_data.values():
            days_count = agent.pop("days_with_data")
            total = agent.pop("Total")
            if days_count > 0:
                agent["Promedio"] = round(total / days_count, 2)
            else:
                agent["Promedio"] = 0

        return sorted(agent_data.values(), key=lambda x: x["Promedio"], reverse=True)
