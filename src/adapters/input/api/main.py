from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.adapters.input.api.routes import health_routes, pdp_routes
from src.infrastructure.config.settings import settings
from src.infrastructure.di.container import Container
from src.infrastructure.logging.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info(f"Starting {settings.name} in {settings.env} mode")

    setup_logging(settings.log_level)

    # Initialize DI container
    container = Container()

    # Load configuration
    container.settings.excel.output_path.from_value(settings.excel.output_path)
    container.settings.excel.template_path.from_value(settings.excel.template_path)

    container.config.google.auth_email.from_value(settings.google.auth_email)
    container.config.google.auth_password.from_value(settings.google.auth_password)
    container.config.google.api_key.from_value(settings.google.api_key)
    container.config.google.project_id.from_value(settings.google.project_id)
    container.config.google.credentials_path.from_value(
        settings.google.credentials_path
    )

    container.config.mibot.api_base_url.from_value(settings.mibot.api_base_url)
    container.config.mibot.project_uid.from_value(settings.mibot.project_uid)
    container.config.mibot.client_uid.from_value(settings.mibot.client_uid)

    container.config.api.timeout.from_value(settings.api.timeout)
    container.config.api.max_retries.from_value(settings.api.max_retries)

    # container.config.from_yaml("config/config.yaml")
    # container.config.from_env("APP", as_=dict)

    # Wire the container
    container.wire(
        modules=[
            "src.adapters.input.api.routes.pdp_routes",
            "src.adapters.input.api.routes.health_routes",
        ]
    )

    app.state.container = container

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")
    # Cleanup resources if needed


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title=settings.name,
        description="Telefonica PDP Analytics",
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    # app.middleware("http")(error_handler_middleware)

    # Setup exception handlers
    # setup_exception_handlers(app)

    # Include routers
    app.include_router(health_routes.router, tags=["Health"])
    app.include_router(pdp_routes.router, prefix=settings.api.prefix, tags=["PDP"])

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "src.adapters.input.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.debug,
    )
