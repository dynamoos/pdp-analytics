from datetime import date

import pytest

from src.domain.value_objects.period import Period


class TestPeriodValueObject:
    """Test cases for Period value object"""

    def test_create_valid_period(self):
        """Test creating a valid period"""
        period = Period(year=2025, month=5)
        assert period.year == 2025
        assert period.month == 5

    def test_period_from_date(self):
        """Test creating period from date object"""
        test_date = date(2025, 5, 14)
        period = Period.from_date(test_date)

        assert period.year == 2025
        assert period.month == 5

    def test_period_from_string(self):
        """Test creating period from string format"""
        # Test formato normal
        period = Period.from_string("2025-05")
        assert period.year == 2025
        assert period.month == 5

        # Test con mes de un dígito (también válido)
        period = Period.from_string("2025-5")
        assert period.year == 2025
        assert period.month == 5

    def test_invalid_string_format_raises_error(self):
        """Test invalid string formats raise ValueError"""
        # Test wrong separator
        with pytest.raises(ValueError, match="Invalid period format"):
            Period.from_string("2025/05")

        # Test missing month
        with pytest.raises(ValueError, match="Invalid period format"):
            Period.from_string("2025")

        # Test wrong order
        with pytest.raises(ValueError, match="Invalid period format"):
            Period.from_string("May-2025")

        # Test empty string
        with pytest.raises(ValueError, match="Invalid period format"):
            Period.from_string("")

        # Test cases that are caught by validation (also show as Invalid period format)
        # Two digit year
        with pytest.raises(ValueError, match="Invalid period format"):
            Period.from_string("25-05")

        # Invalid month
        with pytest.raises(ValueError, match="Invalid period format"):
            Period.from_string("2025-13")

        # Month = 0
        with pytest.raises(ValueError, match="Invalid period format"):
            Period.from_string("2025-0")

    def test_formatted_output(self):
        """Test formatted string output"""
        period = Period(2025, 5)
        assert period.formatted == "2025-05"

        # Test con mes de un dígito que se formatea con cero
        period = Period.from_string("2025-5")
        assert period.formatted == "2025-05"

        # Test with December
        period = Period(2025, 12)
        assert period.formatted == "2025-12"

    def test_month_name_spanish(self):
        """Test Spanish month names"""
        months = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre",
        }

        for month_num, month_name in months.items():
            period = Period(2025, month_num)
            assert period.month_name == month_name

    def test_invalid_year_raises_error(self):
        """Test invalid years raise ValueError when created directly"""
        # Year too old
        with pytest.raises(ValueError, match="Invalid year: 2019"):
            Period(year=2019, month=5)

        # Year too far in future
        with pytest.raises(ValueError, match="Invalid year: 2101"):
            Period(year=2101, month=5)

    def test_invalid_month_raises_error(self):
        """Test invalid months raise ValueError when created directly"""
        # Month < 1
        with pytest.raises(ValueError, match="Invalid month: 0"):
            Period(year=2025, month=0)

        # Month > 12
        with pytest.raises(ValueError, match="Invalid month: 13"):
            Period(year=2025, month=13)

    def test_get_date_range(self):
        """Test getting start and end dates for period"""
        # Regular month
        period = Period(2025, 5)
        start_date, end_date = period.get_date_range()

        assert start_date == date(2025, 5, 1)
        assert end_date == date(2025, 5, 31)

        # February (28 days in non-leap year)
        period = Period(2025, 2)
        start_date, end_date = period.get_date_range()

        assert start_date == date(2025, 2, 1)
        assert end_date == date(2025, 2, 28)

        # February (29 days in leap year)
        period = Period(2024, 2)
        start_date, end_date = period.get_date_range()

        assert start_date == date(2024, 2, 1)
        assert end_date == date(2024, 2, 29)

        # December (test year boundary)
        period = Period(2025, 12)
        start_date, end_date = period.get_date_range()

        assert start_date == date(2025, 12, 1)
        assert end_date == date(2025, 12, 31)

    def test_string_representation(self):
        """Test string representation"""
        period = Period(2025, 5)
        assert str(period) == "2025-05"

    def test_period_immutability(self):
        """Test period values cannot be changed"""
        period = Period(2025, 5)

        with pytest.raises(AttributeError):
            period.year = 2026

        with pytest.raises(AttributeError):
            period.month = 6

    @pytest.mark.parametrize(
        "year,month,expected_days",
        [
            (2025, 1, 31),  # January
            (2025, 2, 28),  # February (non-leap)
            (2024, 2, 29),  # February (leap)
            (2025, 4, 30),  # April
            (2025, 12, 31),  # December
        ],
    )
    def test_days_in_month(self, year, month, expected_days):
        """Test correct number of days per month"""
        period = Period(year, month)
        start_date, end_date = period.get_date_range()
        actual_days = (end_date - start_date).days + 1

        assert actual_days == expected_days
