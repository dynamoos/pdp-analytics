from dependency_injector import containers, providers

from src.application.use_cases import ProcessPDPDataUseCase


class UseCaseModule(containers.DeclarativeContainer):
    """Use cases module"""

    repositories = providers.DependenciesContainer()
    services = providers.DependenciesContainer()

    # Process PDP Data Use Case
    process_pdp_data = providers.Factory(
        ProcessPDPDataUseCase,
        productivity_repository=repositories.productivity_repository,
        excel_service=services.excel_service,
        data_transformation_service=services.data_transformation_service,
    )
