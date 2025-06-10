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

        # Prepare data for both sheets
        detailed_data = self._prepare_detailed_data(pdp_records)
        heatmap_data = self._prepare_heatmap_data(pdp_records)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pdp_report_{timestamp}.xlsx"
        filepath = self._output_path / filename

        # Get unique days from data
        unique_days = sorted(set(record.record_date.day for record in pdp_records))
        day_columns = [str(day) for day in unique_days]

        # Headers for detailed sheet
        detailed_headers = [
            "Fecha",
            "Hora",
            "DNI",
            "Ejecutivo",
            "Total Gestiones",
            "Contactos Efectivos",
            "No Contactos",
            "Contactos No Efectivos",
            "Gestiones PDP",
        ]

        # Headers for heatmap sheet
        heatmap_headers = ["DNI", "EJECUTIVO"] + day_columns + ["Promedio"]

        sheet_configs = [
            # Detailed data sheet
            SheetConfig(
                sheet_name="Detalle Por Hora",
                data=detailed_data,
                headers=detailed_headers,
                apply_filters=True,
                column_widths={
                    "Fecha": 12,
                    "Hora": 8,
                    "DNI": 12,
                    "Ejecutivo": 30,
                    "Total Gestiones": 15,
                    "Contactos Efectivos": 18,
                    "No Contactos": 15,
                    "Contactos No Efectivos": 20,
                    "Gestiones PDP": 15,
                },
            ),
            # Heatmap sheet - Changed name to remove invalid character
            SheetConfig(
                sheet_name="Mapa de Calor PDP por Hora",
                data=heatmap_data,
                headers=heatmap_headers,
                apply_filters=False,
                heatmap_config=HeatmapConfig(value_column="pdp_per_hour"),
            ),
        ]

        excel_dto = ExcelGenerationDTO(
            output_filename=str(filepath), sheet_configs=sheet_configs
        )

        self._excel_generator.generate(excel_dto)
        logger.info(f"Excel report generated: {filepath}")
        return str(filepath)

    @staticmethod
    def _prepare_detailed_data(pdp_records: List[PDPRecord]) -> List[Dict[str, Any]]:
        """Prepare detailed hourly data"""
        data = []
        for record in pdp_records:
            data.append(
                {
                    "Fecha": record.record_date.strftime("%Y-%m-%d"),
                    "Hora": f"{record.hour:02d}:00",
                    "DNI": record.dni,
                    "Ejecutivo": record.agent_name,
                    "Total Gestiones": record.total_operations,
                    "Contactos Efectivos": record.effective_contacts,
                    "No Contactos": record.no_contacts,
                    "Contactos No Efectivos": record.non_effective_contacts,
                    "Gestiones PDP": record.pdp_count,
                }
            )

        return sorted(data, key=lambda x: (x["Fecha"], x["Hora"], x["DNI"]))

    @staticmethod
    def _prepare_heatmap_data(pdp_records: List[PDPRecord]) -> List[Dict[str, Any]]:
        """Prepare data for heatmap visualization - PDP per hour by day"""

        agent_data = {}

        logger.info(f"Preparing heatmap for {len(pdp_records)} records")

        # Group data by agent and day
        for record in pdp_records:
            if record.dni not in agent_data:
                agent_data[record.dni] = {
                    "DNI": record.dni,
                    "EJECUTIVO": record.agent_name,
                    "total_pdp": 0,
                    "total_distinct_hours": 0,
                    "daily_data": {},
                }

            day = str(record.record_date.day)

            # Initialize daily data if not exists
            if day not in agent_data[record.dni]["daily_data"]:
                agent_data[record.dni]["daily_data"][day] = {
                    "pdp_count": 0,
                    "hours_worked": set(),  # Using set to store distinct hours
                }

            # Accumulate data
            agent_data[record.dni]["daily_data"][day]["pdp_count"] += record.pdp_count
            agent_data[record.dni]["daily_data"][day]["hours_worked"].add(record.hour)
            agent_data[record.dni]["total_pdp"] += record.pdp_count

        # Calculate total distinct hours for each agent
        for dni, data in agent_data.items():
            all_hours = set()
            for day_data in data["daily_data"].values():
                all_hours.update(day_data["hours_worked"])
            data["total_distinct_hours"] = len(all_hours)

        # Calculate PDP per hour for each day
        result = []
        for dni, data in agent_data.items():
            row = {"DNI": data["DNI"], "EJECUTIVO": data["EJECUTIVO"]}

            # Calculate PDP/hour for each day
            for day, day_data in data["daily_data"].items():
                distinct_hours = len(day_data["hours_worked"])
                if distinct_hours > 0:
                    pdp_per_hour = round(day_data["pdp_count"] / distinct_hours, 1)
                else:
                    pdp_per_hour = 0
                row[day] = pdp_per_hour

            # Calculate average (total PDP / total distinct hours)
            if data["total_distinct_hours"] > 0:
                row["Promedio"] = round(
                    data["total_pdp"] / data["total_distinct_hours"], 1
                )
            else:
                row["Promedio"] = 0

            result.append(row)

        # Sort by average PDP/hour descending
        return sorted(result, key=lambda x: x["Promedio"], reverse=True)
