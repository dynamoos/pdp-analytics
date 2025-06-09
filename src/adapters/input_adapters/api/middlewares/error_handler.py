import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


async def error_handler_middleware(request: Request, call_next):
    """Middleware for error handling and request logging"""
    # Generate request ID
    request_id = str(uuid.uuid4())

    # Log request
    logger.info(
        f"Request {request_id} - {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )

    # Track request time
    start_time = time.time()

    try:
        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Request {request_id} completed - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.3f}s"
        )

        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(duration)

        return response

    except Exception as e:
        # Log error
        duration = time.time() - start_time
        logger.error(
            f"Request {request_id} failed - Error: {str(e)} - Duration: {duration:.3f}s"
        )

        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "request_id": request_id,
                "message": "An unexpected error occurred",
            },
        )
