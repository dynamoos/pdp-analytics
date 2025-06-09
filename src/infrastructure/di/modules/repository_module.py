from dependency_injector import containers, providers

from src.adapters.output_adapters.persistence.bigquery_pdp_repository import (
    BigQueryPDPRepository,
)
from src.adapters.output_adapters.persistence.postgres_call_repository import (
    PostgresCallRepository,
)


class RepositoryModule(containers.DeclarativeContainer):
    """Repository implementations module"""

    database = providers.DependenciesContainer()

    # PDP Repository
    pdp_repository = providers.Singleton(
        BigQueryPDPRepository, client=database.bigquery_client
    )

    # Call Repository
    call_repository = providers.Singleton(
        PostgresCallRepository, postgres_manager=database.postgres_manager
    )
