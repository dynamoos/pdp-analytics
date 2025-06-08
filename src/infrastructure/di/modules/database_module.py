from dependency_injector import containers, providers

from src.infrastructure.database.bigquery_client import BigQueryClient
from src.infrastructure.database.postgres_manager import PostgresManager


class DatabaseModule(containers.DeclarativeContainer):
    """Database and external clients module"""

    config = providers.Configuration()

    # BigQuery Client
    bigquery_client = providers.Singleton(
        BigQueryClient,
        project_id=config.google.project_id,
        credentials_path=config.google.credentials_path,
        location=config.google.location,
    )

    # Postgres Manager
    postgres_manager = providers.Singleton(
        PostgresManager,
        connection_string=config.postgres.connection_string,
        min_size=config.postgres.min_pool_size,
        max_size=config.postgres.max_pool_size,
    )
