from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from loguru import logger

from src.infrastructure.database.bigquery_client import BigQueryClient
from src.infrastructure.di.container import Container
from src.infrastructure.http.http_client import HttpClient

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Telefonica PDP Analytics API",
    }


@router.get("/health/detailed")
@inject
async def detailed_health_check(
    bigquery_client: BigQueryClient = Depends(
        Provide[Container.database.bigquery_client]
    ),
    http_client: HttpClient = Depends(Provide[Container.database.http_client]),
):
    """Detailed health check with dependencies status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {"bigquery": "unknown", "call_api": "unknown"},
    }

    # Check BigQuery
    try:
        await bigquery_client.execute_query("SELECT 1")
        health_status["dependencies"]["bigquery"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["bigquery"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"BigQuery health check failed: {str(e)}")

    # Check Call API
    try:
        # Try to get auth token
        await http_client._get_headers()
        health_status["dependencies"]["call_api"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["call_api"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Call API health check failed: {str(e)}")

    return health_status
