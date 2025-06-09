from dependency_injector import containers, providers

from src.adapters.output_adapters.persistence.bigquery_pdp_repository import (
    BigQueryProductivityRepository,
)


class RepositoryModule(containers.DeclarativeContainer):
    """Repository implementations module"""

    database = providers.DependenciesContainer()

    # PDP Repository
    productivity_repository = providers.Singleton(
        BigQueryProductivityRepository, client=database.bigquery_client
    )
