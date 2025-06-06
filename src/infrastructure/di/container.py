from dependency_injector import containers, providers

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
    settings = providers.Configuration()

    database = providers.Container(DatabaseModule, config=config)

    repositories = providers.Container(RepositoryModule, database=database)

    services = providers.Container(ServiceModule, config=config)

    use_cases = providers.Container(
        UseCaseModule, repositories=repositories, services=services
    )
