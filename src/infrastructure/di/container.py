from dependency_injector import containers, providers

from src.infrastructure.config.settings import AppSettings
from src.infrastructure.di.modules import (
    DatabaseModule,
    RepositoryModule,
    ServiceModule,
    UseCaseModule,
)


class Container(containers.DeclarativeContainer):
    """Main DI container"""

    # Configuration
    config = providers.Configuration()

    # Load settings
    settings = providers.Singleton(AppSettings)

    database = providers.Container(DatabaseModule, config=config)

    repositories = providers.Container(RepositoryModule, database=database)

    services = providers.Container(ServiceModule, settings=settings)

    use_cases = providers.Container(
        UseCaseModule, repositories=repositories, services=services
    )
