import os
from typing import Any, Dict, List, Optional

from google.cloud import bigquery
from google.oauth2 import service_account
from loguru import logger

from src.shared.exceptions import DatabaseException


class BigQueryClient:
    """BigQuery client wrapper with connection management"""

    def __init__(
        self,
        project_id: str,
        credentials_path: Optional[str] = None,
        location: str = "us-east1",
    ):
        self._project_id = project_id
        self._location = location

        try:
            logger.debug(f"Credentials path received: {credentials_path}")
            if credentials_path and os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                self._client = bigquery.Client(
                    project=project_id, credentials=credentials, location=location
                )
            else:
                # Use default credentials (from environment)
                self._client = bigquery.Client(project=project_id, location=location)

            logger.info(f"BigQuery client initialized for project: {project_id}")

        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {str(e)}")
            raise DatabaseException(f"BigQuery initialization failed: {str(e)}")

    async def execute_query(
        self,
        query: str,
        parameters: Optional[List[bigquery.ScalarQueryParameter]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        try:
            logger.debug(f"Executing query: {query[:100]}...")

            job_config = bigquery.QueryJobConfig()
            if parameters:
                job_config.query_parameters = parameters

            query_job = self._client.query(query, job_config=job_config)
            results = query_job.result()

            # Convert results to list of dictionaries
            rows = []
            for row in results:
                rows.append(dict(row))

            logger.info(f"Query returned {len(rows)} rows")
            return rows

        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise DatabaseException(f"BigQuery query failed: {str(e)}")

    def get_client(self) -> bigquery.Client:
        """Get the underlying BigQuery client"""
        return self._client
