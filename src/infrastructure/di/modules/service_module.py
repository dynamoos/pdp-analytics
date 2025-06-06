from dependency_injector import containers, providers

from src.application.services.excel_service import ExcelService
from src.shared.constants import EXCEL_OUTPUT_PATH


class ServiceModule(containers.DeclarativeContainer):
    """Application services module"""

    config = providers.Configuration()

    # Excel Service con valor por defecto
    excel_service = providers.Singleton(
        ExcelService, output_path=config.excel_output_path.provided(EXCEL_OUTPUT_PATH)
    )
