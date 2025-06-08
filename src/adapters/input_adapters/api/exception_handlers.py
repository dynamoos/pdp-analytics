from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException

from src.shared.exceptions import (
    DomainException,
    ExternalApiException,
    RepositoryException,
    UseCaseException,
)


def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers"""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle validation errors"""
        logger.error(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error", "details": exc.errors()},
        )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        """Handle domain exceptions"""
        logger.error(f"Domain error: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content={"error": "Business rule violation", "message": str(exc)},
        )

    @app.exception_handler(UseCaseException)
    async def use_case_exception_handler(request: Request, exc: UseCaseException):
        """Handle use case exceptions"""
        logger.error(f"Use case error: {str(exc)}")
        return JSONResponse(
            status_code=400, content={"error": "Operation failed", "message": str(exc)}
        )

    @app.exception_handler(RepositoryException)
    async def repository_exception_handler(request: Request, exc: RepositoryException):
        """Handle repository exceptions"""
        logger.error(f"Repository error: {str(exc)}")
        return JSONResponse(
            status_code=503,
            content={
                "error": "Data access error",
                "message": "Unable to access data source",
            },
        )

    @app.exception_handler(ExternalApiException)
    async def external_api_exception_handler(
        request: Request, exc: ExternalApiException
    ):
        """Handle external API exceptions"""
        logger.error(f"External API error: {str(exc)}")
        return JSONResponse(
            status_code=502,
            content={
                "error": "External service error",
                "message": "External service is unavailable",
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "HTTP error", "message": exc.detail},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle any unhandled exceptions"""
        logger.exception(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            },
        )
