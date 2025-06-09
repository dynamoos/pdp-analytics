"""Domain and application exceptions"""


class DomainException(Exception):
    """Base exception for domain errors"""

    pass


class RepositoryException(Exception):
    """Base exception for repository errors"""

    pass


class ExternalApiException(RepositoryException):
    """Raised when external API call fails"""

    pass


class DatabaseException(RepositoryException):
    """Raised when database operation fails"""

    pass


class ApplicationException(Exception):
    """Base exception for application layer errors"""

    pass


class UseCaseException(ApplicationException):
    """Raised when use case execution fails"""

    pass
