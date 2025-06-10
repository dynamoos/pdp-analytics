from datetime import datetime, timezone

from dependency_injector.wiring import inject
from fastapi import APIRouter
from loguru import logger

from src.adapters.input_adapters.api.dependencies import BigQueryClient

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "PDP Analytics API",
    }


@router.get("/health/detailed")
@inject
async def detailed_health_check(bigquery_client: BigQueryClient):
    """Detailed health check with dependencies status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {"bigquery": "unknown", "postgres": "unknown"},
    }

    # Check BigQuery
    try:
        await bigquery_client.execute_query("SELECT 1")
        health_status["dependencies"]["bigquery"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["bigquery"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"BigQuery health check failed: {str(e)}")
    return health_status
