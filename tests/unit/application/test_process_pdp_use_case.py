from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.dto.pdp_dto import PDPRequestDTO, PDPResponseDTO
from src.application.use_cases.process_pdp_data import ProcessPDPDataUseCase
from src.domain.entities.call_data import AgentCallData, CallApiResponse
from src.domain.entities.pdp_record import PDPRecord
from src.domain.value_objects.email import Email
from src.domain.value_objects.period import Period
from src.shared.exceptions import UseCaseException


class TestProcessPDPDataUseCase:
    """Test cases for ProcessPDPDataUseCase"""

    @pytest.fixture
    def mock_repositories(self):
        """Create mock repositories and services"""
        pdp_repo = Mock()
        pdp_repo.get_by_date_range = AsyncMock()

        call_api_repo = Mock()
        call_api_repo.get_multiple_agents_calls = AsyncMock()

        excel_service = Mock()
        excel_service.generate_pdp_report = AsyncMock()

        return pdp_repo, call_api_repo, excel_service

    @pytest.fixture
    def sample_pdp_records(self):
        """Create sample PDP records without call data"""
        return [
            PDPRecord(
                dni="48099652",
                agent_full_name="JANAMPA RAMOS EDITH VANESA",
                agent_email=Email("edithtelefonica@gmail.com"),
                record_date=date(2025, 5, 14),
                period=Period(2025, 5),
                month_name="Mayo",
                service_type="FIJA",
                portfolio="Gestión Temprana",
                due_day=5,
                pdp_count=9,
                total_pdp_operations=18,
                total_managed_amount=Decimal("3220.21"),
                days_with_pdp=1,
                documents_with_debt=18,
                average_amount_per_document=Decimal("178.90"),
            ),
            PDPRecord(
                dni="10181768",
                agent_full_name="VALDIVIA SOTO JORGE LOUI",
                agent_email=Email("dannetelefonica@gmail.com"),
                record_date=date(2025, 5, 14),
                period=Period(2025, 5),
                month_name="Mayo",
                service_type="FIJA",
                portfolio="Gestión Temprana",
                due_day=5,
                pdp_count=10,
                total_pdp_operations=19,
                total_managed_amount=Decimal("2548.03"),
                days_with_pdp=1,
                documents_with_debt=19,
                average_amount_per_document=Decimal("134.10"),
            ),
        ]

    @pytest.fixture
    def sample_call_responses(self):
        """Create sample call API responses"""
        return {
            "edithtelefonica_gmail.com": CallApiResponse(
                success=True,
                data=[
                    AgentCallData(
                        agent_email=Email("edithtelefonica@gmail.com"),
                        call_date=date(2025, 5, 14),
                        total_connected_seconds=1728,
                        total_time_hms="00:28:48",
                    )
                ],
            ),
            "dannetelefonica_gmail.com": CallApiResponse(
                success=True,
                data=[
                    AgentCallData(
                        agent_email=Email("dannetelefonica@gmail.com"),
                        call_date=date(2025, 5, 14),
                        total_connected_seconds=3600,
                        total_time_hms="01:00:00",
                    )
                ],
            ),
        }

    @pytest.mark.asyncio
    async def test_execute_success_with_call_data(
        self, mock_repositories, sample_pdp_records, sample_call_responses
    ):
        """Test successful execution with call data enrichment"""
        pdp_repo, call_api_repo, excel_service = mock_repositories

        # Setup mocks
        pdp_repo.get_by_date_range.return_value = sample_pdp_records
        call_api_repo.get_multiple_agents_calls.return_value = sample_call_responses
        excel_service.generate_pdp_report.return_value = "./output/test_report.xlsx"

        # Create use case
        use_case = ProcessPDPDataUseCase(pdp_repo, call_api_repo, excel_service)

        # Create request
        request = PDPRequestDTO(
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 31),
            service_type="FIJA",
            portfolio="Gestión Temprana",
            include_call_data=True,
            generate_heatmap=True,
        )

        # Execute
        result = await use_case.execute(request)

        # Assertions
        assert isinstance(result, PDPResponseDTO)
        assert result.total_records == 2
        assert result.total_pdps == 19  # 9 + 10
        assert result.total_amount == Decimal("5768.24")  # 3220.21 + 2548.03
        assert result.excel_file_path == "./output/test_report.xlsx"
        assert result.processing_time_seconds > 0
        assert result.errors is None or len(result.errors) == 0

        # Verify calls
        pdp_repo.get_by_date_range.assert_called_once_with(
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 31),
            service_type="FIJA",
            portfolio="Gestión Temprana",
        )

        # Verify call API was called
        assert call_api_repo.get_multiple_agents_calls.called

        # Verify Excel was generated
        excel_service.generate_pdp_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_without_call_data(
        self, mock_repositories, sample_pdp_records
    ):
        """Test execution without call data enrichment"""
        pdp_repo, call_api_repo, excel_service = mock_repositories

        # Setup mocks
        pdp_repo.get_by_date_range.return_value = sample_pdp_records
        excel_service.generate_pdp_report.return_value = "./output/test_report.xlsx"

        # Create use case
        use_case = ProcessPDPDataUseCase(pdp_repo, call_api_repo, excel_service)

        # Create request without call data
        request = PDPRequestDTO(
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 31),
            include_call_data=False,
            generate_heatmap=True,
        )

        # Execute
        result = await use_case.execute(request)

        # Assertions
        assert result.total_records == 2
        assert result.total_pdps == 19

        # Verify call API was NOT called
        call_api_repo.get_multiple_agents_calls.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_no_records_found(self, mock_repositories):
        """Test when no PDP records are found"""
        pdp_repo, call_api_repo, excel_service = mock_repositories

        # Setup mocks
        pdp_repo.get_by_date_range.return_value = []

        # Create use case
        use_case = ProcessPDPDataUseCase(pdp_repo, call_api_repo, excel_service)

        # Create request
        request = PDPRequestDTO(start_date=date(2025, 5, 1), end_date=date(2025, 5, 31))

        # Execute and expect exception
        with pytest.raises(UseCaseException, match="No PDP records found"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_productivity_calculation(
        self, mock_repositories, sample_pdp_records
    ):
        """Test PDPs per hour calculation"""
        pdp_repo, call_api_repo, excel_service = mock_repositories

        # Setup mocks
        pdp_repo.get_by_date_range.return_value = sample_pdp_records

        # Mock call responses with specific times
        call_responses = {
            "edithtelefonica_gmail.com": CallApiResponse(
                success=True,
                data=[
                    AgentCallData(
                        agent_email=Email("edithtelefonica@gmail.com"),
                        call_date=date(2025, 5, 14),
                        total_connected_seconds=1800,  # 0.5 hours
                        total_time_hms="00:30:00",
                    )
                ],
            )
        }

        call_api_repo.get_multiple_agents_calls.return_value = call_responses

        # Capture the records passed to Excel service
        excel_records = None

        async def capture_records(pdp_records=None, include_heatmap=True):
            nonlocal excel_records
            excel_records = pdp_records
            return "./output/test.xlsx"

        excel_service.generate_pdp_report.side_effect = capture_records

        # Create use case
        use_case = ProcessPDPDataUseCase(pdp_repo, call_api_repo, excel_service)

        # Create request
        request = PDPRequestDTO(
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 31),
            include_call_data=True,
        )

        # Execute
        await use_case.execute(request)

        # Check productivity calculation
        # First record should have pdp_per_hour = 9 / 0.5 = 18
        enriched_record = next(r for r in excel_records if r.dni == "48099652")
        assert enriched_record.pdp_per_hour == Decimal("18")

        # Second record should have pdp_per_hour = 0 (no call data)
        other_record = next(r for r in excel_records if r.dni == "10181768")
        assert other_record.pdp_per_hour == Decimal("0")
