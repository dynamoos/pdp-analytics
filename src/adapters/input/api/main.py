from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.adapters.input.api.exception_handlers import setup_exception_handlers
from src.adapters.input.api.middlewares.error_handler import error_handler_middleware
from src.adapters.input.api.routes import health_routes, pdp_routes
from src.infrastructure.di.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting Telefonica PDP Analytics API")

    # Initialize DI container
    container = Container()
    container.config.from_yaml("config/config.yaml")
    container.config.from_env("APP", as_=dict)

    app.state.container = container

    yield

    # Shutdown
    logger.info("Shutting down Telefonica PDP Analytics API")
    # Cleanup resources if needed


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="Telefonica PDP Analytics API",
        description="API for processing PDP data with call enrichment and Excel generation",
        version="1.0.0",
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
    app.middleware("http")(error_handler_middleware)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include routers
    app.include_router(health_routes.router, tags=["Health"])
    app.include_router(pdp_routes.router, prefix="/api/v1", tags=["PDP"])

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "src.adapters.input.api.main:app", host="0.0.0.0", port=8000, reload=True
    )
