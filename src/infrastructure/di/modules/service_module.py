from dependency_injector import containers, providers

from src.application.services.excel_service import ExcelService


class ServiceModule(containers.DeclarativeContainer):
    """Application services module"""

    settings = providers.DependenciesContainer()

    # Excel Service
    excel_service = providers.Singleton(
        ExcelService, output_path=settings.provided.excel.output_path
    )
