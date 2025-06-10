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

        # Get unique days from data and sort them numerically
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

        # Headers for heatmap sheet - IMPORTANT: Promedio goes at the end
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
            # Heatmap sheet
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

        # First, get all unique days across all records
        all_days = sorted(set(record.record_date.day for record in pdp_records))

        logger.info(f"Preparing heatmap for {len(pdp_records)} records")

        # Group data by agent - use a combination of DNI and agent name for uniqueness
        for record in pdp_records:
            # Create a unique key for each agent
            # If DNI is "SIN DNI", use agent name as part of the key
            if record.dni == "SIN DNI":
                agent_key = f"SIN_DNI_{record.agent_name}"
            else:
                agent_key = record.dni

            if agent_key not in agent_data:
                agent_data[agent_key] = {
                    "DNI": record.dni,
                    "EJECUTIVO": record.agent_name,
                    "daily_data": {},
                }

            day = record.record_date.day

            # Initialize daily data if not exists
            if day not in agent_data[agent_key]["daily_data"]:
                agent_data[agent_key]["daily_data"][day] = {
                    "pdp_count": 0,
                    "hours_worked": set(),  # Using set to store distinct hours
                }

            # Accumulate data
            agent_data[agent_key]["daily_data"][day]["pdp_count"] += record.pdp_count
            agent_data[agent_key]["daily_data"][day]["hours_worked"].add(record.hour)

        # Calculate PDP per hour for each day
        result = []
        for agent_key, data in agent_data.items():
            # Start with DNI and EJECUTIVO
            row = {"DNI": data["DNI"], "EJECUTIVO": data["EJECUTIVO"]}

            # List to store daily PDP/hour values for average calculation
            daily_pdp_per_hour_values = []

            # Add all days in order
            for day in all_days:
                day_str = str(day)

                if day in data["daily_data"]:
                    day_data = data["daily_data"][day]
                    distinct_hours = len(day_data["hours_worked"])
                    if distinct_hours > 0:
                        pdp_per_hour = round(day_data["pdp_count"] / distinct_hours, 2)
                    else:
                        pdp_per_hour = 0

                    # Add to list for average calculation (only if > 0)
                    if pdp_per_hour > 0:
                        daily_pdp_per_hour_values.append(pdp_per_hour)
                else:
                    # If no data for this day, leave empty
                    pdp_per_hour = ""

                row[day_str] = pdp_per_hour

            # Calculate average as the mean of daily PDP/hour values - ADD AT THE END
            if daily_pdp_per_hour_values:
                row["Promedio"] = round(
                    sum(daily_pdp_per_hour_values) / len(daily_pdp_per_hour_values), 2
                )
            else:
                row["Promedio"] = 0

            result.append(row)

        # Sort by average PDP/hour descending
        return sorted(result, key=lambda x: x["Promedio"], reverse=True)
