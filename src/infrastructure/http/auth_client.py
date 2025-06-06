from datetime import datetime, timedelta

import httpx
from loguru import logger

from src.shared.exceptions import ExternalApiException


class AuthClient:
    """Client for handling Google Identity authentication"""

    def __init__(self, auth_email: str, auth_password: str, api_key: str):
        self._auth_email = auth_email
        self._auth_password = auth_password
        self._api_key = api_key
        self._token = None
        self._token_expiry = None
        self._auth_url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={api_key}"

    async def get_access_token(self) -> str:
        """Get access token, refresh if expired"""
        if self._token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._token

        # Request new token
        await self._authenticate()
        return self._token

    async def _authenticate(self):
        """Authenticate and get access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._auth_url,
                    json={
                        "email": self._auth_email,
                        "password": self._auth_password,
                        "returnSecureToken": True,
                    },
                    headers={"Content-Type": "application/json"},
                )

                response.raise_for_status()
                data = response.json()

                self._token = data.get("idToken")
                # Token expires in 1 hour, refresh 5 minutes before
                self._token_expiry = datetime.now() + timedelta(minutes=55)

                logger.info("Successfully authenticated with Google Identity")

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise ExternalApiException(f"Failed to authenticate: {str(e)}")
