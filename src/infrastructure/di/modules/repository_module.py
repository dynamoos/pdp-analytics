from dependency_injector import containers, providers

from src.adapters.output.database.bigquery_pdp_repository import BigQueryPDPRepository
from src.adapters.output.external_apis.http_call_api_repository import (
    HttpCallApiRepository,
)


class RepositoryModule(containers.DeclarativeContainer):
    """Repository implementations module"""

    database = providers.DependenciesContainer()

    # PDP Repository
    pdp_repository = providers.Singleton(
        BigQueryPDPRepository, client=database.bigquery_client
    )

    # Call API Repository
    call_api_repository = providers.Singleton(
        HttpCallApiRepository, http_client=database.http_client
    )
