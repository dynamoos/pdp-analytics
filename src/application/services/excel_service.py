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

        # Get unique days from data and sort them
        unique_days = sorted(set(record.record_date.day for record in pdp_records))

        # Prepare the data
        heatmap_data = self._prepare_heatmap_data(pdp_records, unique_days)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pdp_report_{timestamp}.xlsx"
        filepath = self._output_path / filename

        # Create headers with sorted day columns
        day_columns = [str(day) for day in unique_days]
        headers = ["DNI", "SUPERVISOR"] + day_columns + ["Promedio"]

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
    def _prepare_heatmap_data(
        pdp_records: List[PDPRecord], unique_days: List[int]
    ) -> List[Dict[str, Any]]:
        """Prepare data for heatmap visualization"""

        agent_data = {}

        logger.info(f"Preparing heatmap for {len(pdp_records)} records")

        # Initialize agent data structure
        for record in pdp_records:
            if record.dni not in agent_data:
                agent_data[record.dni] = {
                    "DNI": record.dni,
                    "SUPERVISOR": record.agent_name,
                    "days_data": {},
                    "total": 0,
                    "count": 0,
                }

            # Store the data for the specific day
            day = record.record_date.day
            agent_data[record.dni]["days_data"][day] = float(record.promises_per_hour)
            agent_data[record.dni]["total"] += float(record.promises_per_hour)
            agent_data[record.dni]["count"] += 1

        # Convert to final format
        result = []
        for dni, data in agent_data.items():
            row = {"DNI": data["DNI"], "SUPERVISOR": data["SUPERVISOR"]}

            # Add data for each day in the correct order
            for day in unique_days:
                day_str = str(day)
                if day in data["days_data"]:
                    row[day_str] = data["days_data"][day]
                else:
                    row[day_str] = ""  # Empty cell for days without data

            # Calculate average
            if data["count"] > 0:
                row["Promedio"] = round(data["total"] / data["count"], 2)
            else:
                row["Promedio"] = 0

            result.append(row)

        # Sort by average (descending)
        return sorted(result, key=lambda x: x["Promedio"], reverse=True)
