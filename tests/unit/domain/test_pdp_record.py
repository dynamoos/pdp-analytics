from datetime import date
from decimal import Decimal

import pytest

from src.domain.entities.pdp_record import PDPRecord
from src.domain.value_objects.email import Email
from src.domain.value_objects.period import Period


class TestPDPRecord:
    """Test cases for PDPRecord entity"""

    @pytest.fixture
    def valid_pdp_data(self):
        """Fixture with valid PDP record data"""
        return {
            "dni": "48099652",
            "agent_full_name": "JANAMPA RAMOS EDITH VANESA",
            "agent_email": Email("edithtelefonica@gmail.com"),
            "record_date": date(2025, 5, 14),
            "period": Period(2025, 5),
            "month_name": "Mayo",
            "service_type": "FIJA",
            "portfolio": "Gestión Temprana",
            "due_day": 5,
            "pdp_count": 9,
            "total_pdp_operations": 18,
            "total_managed_amount": Decimal("3220.21"),
            "days_with_pdp": 1,
            "documents_with_debt": 18,
            "average_amount_per_document": Decimal("178.90"),
        }

    def test_create_valid_pdp_record(self, valid_pdp_data):
        """Test creating a valid PDP record"""
        record = PDPRecord(**valid_pdp_data)

        assert record.dni == "48099652"
        assert record.agent_full_name == "JANAMPA RAMOS EDITH VANESA"
        assert record.pdp_count == 9
        assert record.service_type == "FIJA"

    def test_pdp_record_with_call_data(self, valid_pdp_data):
        """Test PDP record with optional call data"""
        valid_pdp_data["total_connected_seconds"] = 1728
        valid_pdp_data["total_time_hms"] = "00:28:48"
        valid_pdp_data["pdp_per_hour"] = Decimal("18.75")

        record = PDPRecord(**valid_pdp_data)

        assert record.total_connected_seconds == 1728
        assert record.total_time_hms == "00:28:48"
        assert record.pdp_per_hour == Decimal("18.75")

    def test_negative_pdp_count_raises_error(self, valid_pdp_data):
        """Test negative PDP count raises ValueError"""
        valid_pdp_data["pdp_count"] = -1

        with pytest.raises(ValueError, match="PDP count cannot be negative"):
            PDPRecord(**valid_pdp_data)

    def test_negative_managed_amount_raises_error(self, valid_pdp_data):
        """Test negative managed amount raises ValueError"""
        valid_pdp_data["total_managed_amount"] = Decimal("-100.00")

        with pytest.raises(ValueError, match="Total managed amount cannot be negative"):
            PDPRecord(**valid_pdp_data)

    def test_invalid_due_day_raises_error(self, valid_pdp_data):
        """Test invalid due day raises ValueError"""
        # Test due day < 1
        valid_pdp_data["due_day"] = 0
        with pytest.raises(ValueError, match="Due day must be between 1 and 31"):
            PDPRecord(**valid_pdp_data)

        # Test due day > 31
        valid_pdp_data["due_day"] = 32
        with pytest.raises(ValueError, match="Due day must be between 1 and 31"):
            PDPRecord(**valid_pdp_data)

    def test_invalid_service_type_raises_error(self, valid_pdp_data):
        """Test invalid service type raises ValueError"""
        valid_pdp_data["service_type"] = "INVALID"

        with pytest.raises(ValueError, match="Invalid service type: INVALID"):
            PDPRecord(**valid_pdp_data)

    def test_valid_service_types(self, valid_pdp_data):
        """Test both valid service types"""
        # Test FIJA
        valid_pdp_data["service_type"] = "FIJA"
        record = PDPRecord(**valid_pdp_data)
        assert record.service_type == "FIJA"

        # Test MOVIL
        valid_pdp_data["service_type"] = "MOVIL"
        record = PDPRecord(**valid_pdp_data)
        assert record.service_type == "MOVIL"

    def test_average_pdp_per_day_calculation(self, valid_pdp_data):
        """Test average PDPs per day calculation"""
        # Normal case
        record = PDPRecord(**valid_pdp_data)
        assert record.average_pdp_per_day == 9.0  # 9 PDPs / 1 day

        # Multiple days
        valid_pdp_data["pdp_count"] = 30
        valid_pdp_data["days_with_pdp"] = 5
        record = PDPRecord(**valid_pdp_data)
        assert record.average_pdp_per_day == 6.0  # 30 PDPs / 5 days

        # Zero days (edge case)
        valid_pdp_data["days_with_pdp"] = 0
        record = PDPRecord(**valid_pdp_data)
        assert record.average_pdp_per_day == 0.0

    def test_effectiveness_rate_calculation(self, valid_pdp_data):
        """Test effectiveness rate calculation"""
        # Normal case
        record = PDPRecord(**valid_pdp_data)
        # 18 documents with debt / 18 total operations = 1.0
        assert record.effectiveness_rate == 1.0

        # Partial effectiveness
        valid_pdp_data["documents_with_debt"] = 9
        valid_pdp_data["total_pdp_operations"] = 18
        record = PDPRecord(**valid_pdp_data)
        assert record.effectiveness_rate == 0.5

        # Zero operations (edge case)
        valid_pdp_data["total_pdp_operations"] = 0
        record = PDPRecord(**valid_pdp_data)
        assert record.effectiveness_rate == 0.0

    def test_connected_hours_property(self, valid_pdp_data):
        """Test connected hours calculation from seconds"""
        # With call data
        valid_pdp_data["total_connected_seconds"] = 3600
        record = PDPRecord(**valid_pdp_data)
        assert record.connected_hours == 1.0

        # 1728 seconds = 0.48 hours
        valid_pdp_data["total_connected_seconds"] = 1728
        record = PDPRecord(**valid_pdp_data)
        assert record.connected_hours == 0.48

        # Without call data
        record = PDPRecord(**valid_pdp_data)
        record = PDPRecord(
            **{
                k: v
                for k, v in valid_pdp_data.items()
                if k != "total_connected_seconds"
            }
        )
        assert record.connected_hours is None

    def test_pdp_record_immutability(self, valid_pdp_data):
        """Test PDP record is immutable (frozen)"""
        record = PDPRecord(**valid_pdp_data)

        with pytest.raises(AttributeError):
            record.pdp_count = 100
