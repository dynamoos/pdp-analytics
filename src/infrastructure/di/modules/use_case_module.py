from dependency_injector import containers, providers

from src.application.use_cases.generate_excel_report import GenerateExcelReportUseCase
from src.application.use_cases.process_pdp_data import ProcessPDPDataUseCase


class UseCaseModule(containers.DeclarativeContainer):
    """Use cases module"""

    repositories = providers.DependenciesContainer()
    services = providers.DependenciesContainer()

    # Process PDP Data Use Case
    process_pdp_data = providers.Factory(
        ProcessPDPDataUseCase,
        pdp_repository=repositories.pdp_repository,
        call_api_repository=repositories.call_api_repository,
        excel_service=services.excel_service,
    )

    # Generate Excel Report Use Case
    generate_excel_report = providers.Factory(
        GenerateExcelReportUseCase, excel_service=services.excel_service
    )
