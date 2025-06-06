from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest

from src.adapters.output.external_apis.http_call_api_repository import (
    HttpCallApiRepository,
)
from src.domain.entities.call_data import AgentCallData, CallApiResponse
from src.domain.value_objects.email import Email
from src.infrastructure.http.http_client import HttpClient
from src.shared.exceptions import ExternalApiException


class TestHttpCallApiRepository:
    """Integration tests for HttpCallApiRepository"""

    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client"""
        client = Mock(spec=HttpClient)
        client.get = AsyncMock()
        return client

    @pytest.fixture
    def sample_api_response(self):
        """Sample response from call API"""
        return [
            {
                "agente": "edithtelefonica_gmail.com",
                "total_segundos_conectado": "1728",
                "tiempo_total_hms": "00:28:48",
            },
            {
                "agente": "dannetelefonica_gmail.com",
                "total_segundos_conectado": "3600",
                "tiempo_total_hms": "01:00:00",
            },
            {
                "agente": "karentelefonica_gmail.com",
                "total_segundos_conectado": "5400",
                "tiempo_total_hms": "01:30:00",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_agent_calls_success(self, mock_http_client, sample_api_response):
        """Test successful retrieval of agent call data"""
        # Setup mock - return only data for requested agent
        mock_http_client.get.return_value = sample_api_response

        # Create repository
        repository = HttpCallApiRepository(mock_http_client)

        # Execute
        email = Email("edithtelefonica@gmail.com")
        query_date = date(2025, 5, 14)

        result = await repository.get_agent_calls(email, query_date)

        # Assertions
        assert isinstance(result, CallApiResponse)
        assert result.success is True
        assert len(result.data) == 1

        # Check call data
        call_data = result.data[0]
        assert isinstance(call_data, AgentCallData)
        assert call_data.agent_email.value == "edithtelefonica@gmail.com"
        assert call_data.call_date == query_date
        assert call_data.total_connected_seconds == 1728
        assert call_data.total_time_hms == "00:28:48"

        # Verify API was called correctly
        mock_http_client.get.assert_called_once_with(
            endpoint="v2/api/productividad/tiempo_conectado.php",
            params={"date": "2025-05-14"},
        )

    @pytest.mark.asyncio
    async def test_get_agent_calls_not_found(
        self, mock_http_client, sample_api_response
    ):
        """Test when agent is not in API response"""
        # Setup mock
        mock_http_client.get.return_value = sample_api_response

        # Create repository
        repository = HttpCallApiRepository(mock_http_client)

        # Execute with agent not in response
        email = Email("notfound@telefonica.com")
        query_date = date(2025, 5, 14)

        result = await repository.get_agent_calls(email, query_date)

        # Assertions
        assert result.success is True
        assert len(result.data) == 0  # No data for this agent

    @pytest.mark.asyncio
    async def test_get_agent_calls_api_error(self, mock_http_client):
        """Test error handling when API fails"""
        # Setup mock to raise exception
        mock_http_client.get.side_effect = ExternalApiException("API connection failed")

        # Create repository
        repository = HttpCallApiRepository(mock_http_client)

        # Execute
        email = Email("edithtelefonica@gmail.com")
        query_date = date(2025, 5, 14)

        result = await repository.get_agent_calls(email, query_date)

        # Assertions
        assert result.success is False
        assert len(result.data) == 0
        assert "API connection failed" in result.error_message

    @pytest.mark.asyncio
    async def test_get_multiple_agents_calls(
        self, mock_http_client, sample_api_response
    ):
        """Test batch retrieval for multiple agents"""
        # Setup mock
        mock_http_client.get.return_value = sample_api_response

        # Create repository
        repository = HttpCallApiRepository(mock_http_client)

        # Execute
        agents_data = [
            {"email": Email("edithtelefonica@gmail.com"), "dni": "48099652"},
            {"email": Email("dannetelefonica@gmail.com"), "dni": "10181768"},
            {"email": Email("notfound@telefonica.com"), "dni": "12345678"},
        ]
        query_date = date(2025, 5, 14)

        results = await repository.get_multiple_agents_calls(agents_data, query_date)

        # Assertions
        assert len(results) == 3

        # Check first agent
        assert "edithtelefonica_gmail.com" in results
        assert results["edithtelefonica_gmail.com"].success is True
        assert len(results["edithtelefonica_gmail.com"].data) == 1
        assert (
            results["edithtelefonica_gmail.com"].data[0].total_connected_seconds == 1728
        )

        # Check second agent
        assert "dannetelefonica_gmail.com" in results
        assert results["dannetelefonica_gmail.com"].success is True
        assert (
            results["dannetelefonica_gmail.com"].data[0].total_connected_seconds == 3600
        )

        # Check agent not found
        assert "notfound_telefonica.com" in results
        assert results["notfound_telefonica.com"].success is True
        assert len(results["notfound_telefonica.com"].data) == 0

        # Verify API was called only once (batch optimization)
        assert mock_http_client.get.call_count == 1

    @pytest.mark.asyncio
    async def test_parse_seconds_as_integer(self, mock_http_client):
        """Test parsing when seconds is integer instead of string"""
        response_with_int_seconds = [
            {
                "agente": "edithtelefonica_gmail.com",
                "total_segundos_conectado": 2700,  # Integer instead of string
                "tiempo_total_hms": "00:45:00",
            }
        ]

        mock_http_client.get.return_value = response_with_int_seconds

        # Create repository
        repository = HttpCallApiRepository(mock_http_client)

        # Execute
        email = Email("edithtelefonica@gmail.com")
        query_date = date(2025, 5, 14)

        result = await repository.get_agent_calls(email, query_date)

        # Should handle integer seconds
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0].total_connected_seconds == 2700

    @pytest.mark.asyncio
    async def test_email_transformation(self, mock_http_client):
        """Test that email @ is transformed to _ for API"""
        # Response with underscore format
        response_with_underscore = [
            {
                "agente": "test.user_telefonica.com",  # With underscore
                "total_segundos_conectado": "900",
                "tiempo_total_hms": "00:15:00",
            }
        ]

        mock_http_client.get.return_value = response_with_underscore

        # Create repository
        repository = HttpCallApiRepository(mock_http_client)

        # Execute with email containing @
        email = Email("test.user@telefonica.com")
        query_date = date(2025, 5, 14)

        result = await repository.get_agent_calls(email, query_date)

        # Should find the agent with transformed email
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0].agent_email.value == "test.user@telefonica.com"
        assert result.data[0].total_connected_seconds == 900

    @pytest.mark.asyncio
    async def test_handle_empty_response(self, mock_http_client):
        """Test handling empty API response"""
        # Setup mock to return empty list
        mock_http_client.get.return_value = []

        # Create repository
        repository = HttpCallApiRepository(mock_http_client)

        # Execute
        email = Email("edithtelefonica@gmail.com")
        query_date = date(2025, 5, 14)

        result = await repository.get_agent_calls(email, query_date)

        # Should handle empty response gracefully
        assert result.success is True
        assert len(result.data) == 0
