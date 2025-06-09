from dependency_injector import containers, providers

from src.application.services.excel_service import ExcelService
from src.infrastructure.excel.excel_generator import ExcelGenerator
from src.infrastructure.excel.heatmap_formatter import HeatmapFormatter
from src.shared.constants import EXCEL_OUTPUT_PATH


class ServiceModule(containers.DeclarativeContainer):
    """Application services module"""

    config = providers.Configuration()

    excel_generator = providers.Singleton(ExcelGenerator)
    heatmap_formatter = providers.Singleton(HeatmapFormatter)

    excel_service = providers.Singleton(
        ExcelService,
        output_path=EXCEL_OUTPUT_PATH,
        excel_generator=excel_generator,
        heatmap_formatter=heatmap_formatter,
    )
