from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.adapters.input_adapters.api.routes import health_routes, pdp_routes
from src.infrastructure.config.settings import settings
from src.infrastructure.di.container import Container
from src.infrastructure.logging.logger import setup_logging

from .exception_handlers import setup_exception_handlers


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info(f"Starting {settings.name} in {settings.env} mode")

    setup_logging(settings.log_level)

    # Initialize DI container
    container = Container()

    container.config.from_dict(settings.to_container_config())

    # Wire the container
    container.wire(
        modules=[
            "src.adapters.input_adapters.api.routes.pdp_routes",
            "src.adapters.input_adapters.api.routes.health_routes",
        ]
    )

    fastapi.state.container = container

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title=settings.name,
        description="PDP Analytics",
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
    # app.middleware("http")(error_handler_midcledleware)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include routers
    app.include_router(health_routes.router, tags=["Health"])
    app.include_router(pdp_routes.router, prefix=settings.api.prefix, tags=["PDP"])

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "src.adapters.input_adapters.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.debug,
    )
