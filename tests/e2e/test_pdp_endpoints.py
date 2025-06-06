import os
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Set test environment variables before any imports
os.environ.update(
    {
        "GCP_PROJECT_ID": "test-project",
        "GOOGLE_AUTH_EMAIL": "test@test.com",
        "GOOGLE_AUTH_PASSWORD": "test-password",
        "GOOGLE_API_KEY": "test-key",
        "MIBOT_PROJECT_UID": "test-uid",
        "MIBOT_CLIENT_UID": "test-client",
        "APP_ENV": "test",
        "LOG_LEVEL": "ERROR",
    }
)

from fastapi.testclient import TestClient

from src.adapters.input.api.main import app
from src.application.dto.pdp_dto import PDPResponseDTO


class TestPDPEndpoints:
    """End-to-end tests for PDP API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client with mocked container"""
        # Mock the container to avoid DI initialization
        with patch("src.adapters.input.api.main.Container") as mock_container:
            mock_instance = Mock()
            mock_container.return_value = mock_instance

            # Mock the wire method
            mock_instance.wire = Mock()

            # Create test client
            with TestClient(app) as test_client:
                yield test_client

    def test_health_check(self, client):
        """Test basic health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "Telefonica PDP Analytics API"

    def test_process_pdp_invalid_date_format(self, client):
        """Test PDP processing with invalid date format"""
        response = client.post(
            "/api/v1/pdp/process",
            params={
                "start_date": "01-05-2025",  # Wrong format
                "end_date": "31-05-2025",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_download_excel_success(self, client):
        """Test downloading generated Excel file"""
        # Create a test file
        os.makedirs("output", exist_ok=True)
        test_file = Path("output/test_download.xlsx")
        test_file.write_text("test content")

        try:
            response = client.get("/api/v1/pdp/download/test_download.xlsx")

            assert response.status_code == 200
            assert (
                response.headers["content-type"]
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            assert b"test content" in response.content
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()

    def test_download_excel_not_found(self, client):
        """Test downloading non-existent file"""
        response = client.get("/api/v1/pdp/download/nonexistent.xlsx")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "File not found"

    def test_download_excel_path_traversal(self, client):
        """Test security against path traversal attacks"""
        response = client.get("/api/v1/pdp/download/../../../etc/passwd")

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Invalid filename"

    def test_api_documentation(self, client):
        """Test that API documentation is accessible"""
        response = client.get("/docs")

        assert response.status_code == 200
        assert "swagger-ui" in response.text.lower()

    def test_openapi_schema(self, client):
        """Test OpenAPI schema generation"""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Telefonica PDP Analytics API"
        assert "/api/v1/pdp/download/{filename}" in data["paths"]
        assert "/health" in data["paths"]


class TestPDPEndpointsWithMocks:
    """Tests that require deeper mocking of the use case"""

    @pytest.fixture
    def mock_use_case_response(self):
        """Mock response from use case"""
        return PDPResponseDTO(
            total_records=1,
            total_pdps=9,
            total_amount=Decimal("3220.21"),
            excel_file_path="./output/test_report_20250514_120000.xlsx",
            processing_time_seconds=2.5,
            errors=None,
        )

    @patch("src.infrastructure.di.container.Container")
    @patch("src.adapters.input.api.routes.pdp_routes.Depends")
    def test_process_pdp_success(
        self, mock_depends, mock_container, mock_use_case_response
    ):
        """Test successful PDP processing with mocked use case"""
        # Create mock use case
        mock_use_case = Mock()
        mock_use_case.execute = AsyncMock(return_value=mock_use_case_response)

        # Configure Depends to return our mock
        mock_depends.return_value = lambda: mock_use_case

        # Create client
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/pdp/process",
                params={
                    "start_date": "2025-05-01",
                    "end_date": "2025-05-31",
                    "service_type": "FIJA",
                    "include_call_data": True,
                    "generate_heatmap": True,
                },
            )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 1
        assert data["total_pdps"] == 9
        assert float(data["total_amount"]) == 3220.21
        assert "test_report" in data["excel_file_path"]

    def test_process_pdp_invalid_dates(self):
        """Test PDP processing with invalid date range"""
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/pdp/process",
                params={
                    "start_date": "2025-05-31",
                    "end_date": "2025-05-01",  # End before start
                },
            )

        assert response.status_code == 400
        data = response.json()
        assert "Start date must be before or equal to end date" in data["detail"]
