from dependency_injector import containers, providers

from src.infrastructure.database.bigquery_client import BigQueryClient


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
