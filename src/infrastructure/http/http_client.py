import json
from typing import Any, Dict, Optional

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.infrastructure.http.auth_client import AuthClient
from src.shared.constants import API_MAX_RETRIES, API_TIMEOUT_SECONDS
from src.shared.exceptions import ExternalApiException


class HttpClient:
    """HTTP client wrapper with authentication and retry logic"""

    def __init__(
        self,
        base_url: str,
        auth_client: Optional[AuthClient] = None,
        mibot_session: Optional[Dict[str, str]] = None,
        timeout: int = API_TIMEOUT_SECONDS,
        max_retries: int = API_MAX_RETRIES,
    ):
        self._base_url = base_url.rstrip("/")
        self._auth_client = auth_client
        self._mibot_session = mibot_session
        self._timeout = timeout
        self._max_retries = max_retries
        logger.info(f"HTTP client initialized for {base_url}")

    async def _get_headers(self) -> Dict[str, str]:
        """Build request headers with authentication"""
        headers = {}

        # Add Bearer token if auth client is available
        if self._auth_client:
            token = await self._auth_client.get_access_token()
            headers["Authorization"] = f"Bearer {token}"

        # Add mibot session if available
        if self._mibot_session:
            import json

            session_data = {
                "project_uid": str(self._mibot_session.get("project_uid", "")),
                "client_uid": str(self._mibot_session.get("client_uid", "")),
            }
            headers["mibot_session"] = json.dumps(session_data)

        return headers

    @retry(
        stop=stop_after_attempt(API_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute GET request with retry logic"""
        import ssl

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(self._timeout), verify=ssl_context
        ) as client:
            try:
                # Build headers
                request_headers = await self._get_headers()
                if headers:
                    request_headers.update(headers)

                url = (
                    f"{self._base_url}/{endpoint.lstrip('/')}"
                    if endpoint
                    else self._base_url
                )

                logger.debug(f"GET request to: {url} with params: {params}")

                response = await client.get(url, params=params, headers=request_headers)
                response.raise_for_status()

                response_text = response.text

                if response_text.startswith("<br"):
                    json_start = response_text.find("{")
                    if json_start != -1:
                        response_text = response_text[json_start:]
                        logger.warning("Cleaned PHP error from response")

                try:
                    data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Failed to parse JSON. Response: {response_text[:200]}"
                    )
                    raise ExternalApiException(
                        f"Invalid JSON response: {str(e)}"
                    ) from e

                logger.debug(f"Response received: {response.status_code}")
                return data

            except httpx.ReadTimeout as e:
                logger.error(
                    f"Read timeout after {self._timeout}s waiting for response from {url}"
                )
                raise ExternalApiException(
                    "API response timeout - the server took too long to respond"
                ) from e
            except httpx.ConnectTimeout as e:
                logger.error(f"Connection timeout after 10s trying to connect to {url}")
                raise ExternalApiException("Could not connect to API server") from e
            except httpx.TimeoutException as e:
                logger.error(f"General timeout: {type(e).__name__}: {str(e)}")
                raise ExternalApiException(f"Request timed out: {str(e)}") from e
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise ExternalApiException(
                    f"API request failed with status {e.response.status_code}"
                ) from e
            except httpx.RequestError as e:
                logger.error(f"Request error: {type(e).__name__}: {str(e)}")
                raise ExternalApiException(f"Failed to connect to API: {str(e)}") from e
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise ExternalApiException(
                    f"Unexpected error calling API: {str(e)}"
                ) from e
