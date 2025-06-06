import pytest

from src.domain.value_objects.email import Email


class TestEmailValueObject:
    """Test cases for Email value object"""

    def test_create_valid_email(self):
        """Test creating a valid email"""
        email = Email("user@example.com")
        assert email.value == "user@example.com"

    def test_email_normalization(self):
        """Test email is normalized to lowercase"""
        email = Email("User@Example.COM")
        assert email.normalized == "user@example.com"

    def test_api_format_transformation(self):
        """Test @ is replaced with _ for API format"""
        email = Email("user@gmail.com")
        assert email.api_format == "user_gmail.com"

    def test_api_format_with_uppercase(self):
        """Test API format normalizes and transforms"""
        email = Email("User@gmail.com")
        assert email.api_format == "user_gmail.com"

    def test_extract_domain(self):
        """Test domain extraction from email"""
        email = Email("user@example.com")
        assert email.domain == "example.com"

    def test_empty_email_raises_error(self):
        """Test empty email raises ValueError"""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            Email("")

    def test_invalid_email_format_raises_error(self):
        """Test invalid email formats raise ValueError"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@@example.com",
            "user@example",
            "user example@example.com",
            "user@.com",
        ]

        for invalid_email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                Email(invalid_email)

    def test_email_string_representation(self):
        """Test string representation returns original value"""
        email = Email("user@example.com")
        assert str(email) == "user@example.com"

    def test_email_equality(self):
        """Test email equality comparison"""
        email1 = Email("user@example.com")
        email2 = Email("user@example.com")
        email3 = Email("other@example.com")

        assert email1 == email2
        assert email1 != email3

    def test_email_immutability(self):
        """Test email value cannot be changed"""
        email = Email("user@example.com")

        # This should raise an error since Email is frozen
        with pytest.raises(AttributeError):
            email.value = "new@example.com"
