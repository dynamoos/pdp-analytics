from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from src.application.dto import ExcelGenerationDTO, HeatmapConfig, SheetConfig
from src.domain.entities import PDPRecord
from src.infrastructure.excel import ExcelGenerator
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
        day_columns = sorted({str(record.record_date.day) for record in pdp_records})

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
        data = [
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
            for record in pdp_records
        ]

        return sorted(data, key=lambda x: (x["Fecha"], x["Hora"], x["DNI"]))

    @staticmethod
    def _prepare_heatmap_data(pdp_records: List[PDPRecord]) -> List[Dict[str, Any]]:
        """Prepare data for heatmap visualization - PDP per hour by day"""

        if not pdp_records:
            return []

        from collections import defaultdict

        all_days = sorted(set(r.record_date.day for r in pdp_records))

        agents = {}
        for r in pdp_records:
            key = r.dni if r.dni != "SIN DNI" else f"SIN_DNI_{r.agent_name}"
            if key not in agents:
                agents[key] = {
                    "info": {"DNI": r.dni, "EJECUTIVO": r.agent_name},
                    "days": defaultdict(lambda: {"pdp": 0, "hours": set()}),
                }
            agents[key]["days"][r.record_date.day]["pdp"] += r.pdp_count
            agents[key]["days"][r.record_date.day]["hours"].add(r.hour)

        result = []
        for agent_data in agents.values():
            row = {
                "DNI": agent_data["info"]["DNI"],
                "EJECUTIVO": agent_data["info"]["EJECUTIVO"],
            }
            pdp_rates = []

            for day in all_days:
                if day in agent_data["days"]:
                    hours_count = len(agent_data["days"][day]["hours"])
                    rate = (
                        round(agent_data["days"][day]["pdp"] / hours_count, 1)
                        if hours_count
                        else 0
                    )
                    if rate > 0:
                        pdp_rates.append(rate)
                    row[str(day)] = rate
                else:
                    row[str(day)] = ""

            from statistics import mean

            row["Promedio"] = round(mean(pdp_rates), 1) if pdp_rates else 0
            result.append(row)
        return sorted(result, key=lambda x: x["Promedio"], reverse=True)
