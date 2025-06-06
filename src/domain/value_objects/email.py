from dataclasses import dataclass
import re
from typing import Pattern


@dataclass(frozen=True)
class Email:
    """Value object for email addresses with transformation capabilities"""

    value: str

    def __post_init__(self):
        """Validate email format"""
        if not self.value:
            raise ValueError("Email cannot be empty")

        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        if not email_pattern.match(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    @property
    def normalized(self) -> str:
        """Return email in lowercase"""
        return self.value.lower()

    @property
    def api_format(self) -> str:
        """Transform email for API usage (@ -> _)"""
        return self.normalized.replace("@", "_")

    @property
    def domain(self) -> str:
        """Extract domain from email"""
        return self.value.split("@")[1]

    def __str__(self) -> str:
        return self.value
