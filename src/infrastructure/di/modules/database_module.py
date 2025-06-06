from dependency_injector import containers, providers

from src.infrastructure.database.bigquery_client import BigQueryClient
from src.infrastructure.http.auth_client import AuthClient
from src.infrastructure.http.http_client import HttpClient


class DatabaseModule(containers.DeclarativeContainer):
    """Database and external clients module"""

    config = providers.Configuration()

    # Google Auth Client
    auth_client = providers.Singleton(
        AuthClient,
        auth_email=config.google.auth_email,
        auth_password=config.google.auth_password,
        api_key=config.google.api_key,
    )

    # BigQuery Client
    bigquery_client = providers.Singleton(
        BigQueryClient,
        project_id=config.google.project_id,
        credentials_path=config.google.credentials_path,
        location="us-east1",
    )

    # HTTP Client for external API
    http_client = providers.Singleton(
        HttpClient,
        base_url=config.mibot.api_base_url,
        auth_client=auth_client,
        mibot_session=providers.Dict(
            {
                "project_uid": config.mibot.project_uid,
                "client_uid": config.mibot.client_uid,
            }
        ),
        timeout=config.api.timeout,
        max_retries=config.api.max_retries,
    )
