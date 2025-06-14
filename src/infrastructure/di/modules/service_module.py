from dependency_injector import containers, providers

from src.adapters.output_adapters.services import PandasTransformationService
from src.application.services import ExcelService
from src.infrastructure.excel import ExcelGenerator
from src.shared.constants import EXCEL_OUTPUT_PATH


class ServiceModule(containers.DeclarativeContainer):
    """Application services module"""

    config = providers.Configuration()

    data_transformation_service = providers.Singleton(PandasTransformationService)

    excel_generator = providers.Singleton(ExcelGenerator)

    excel_service = providers.Singleton(
        ExcelService,
        output_path=EXCEL_OUTPUT_PATH,
        excel_generator=excel_generator,
    )
