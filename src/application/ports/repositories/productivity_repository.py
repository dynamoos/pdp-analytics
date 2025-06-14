from abc import ABC, abstractmethod
from datetime import date

from src.domain.entities import PDPRecord


class ProductivityRepository(ABC):
    """
    Abstract base class for a repository that manages productivity data.

    The purpose of this class is to define an interface for retrieving
    productivity data records filtered by specific criteria such as date
    ranges. Any subclass inheriting from this class must implement the
    abstract methods defined here. This ensures consistent behavior
    across different repository implementations.
    """

    @abstractmethod
    async def get_by_filters(self, start_date: date, end_date: date) -> list[PDPRecord]:
        """
        An abstract method that retrieves a list of PDPRecord objects filtered by
        a specified start and end date. This method must be implemented by any
        subclass inheriting it, ensuring the functionality to fetch filtered records
        asynchronously.

        :param start_date: The starting date for filtering the records.
        :param end_date: The ending date for filtering the records.
        :return: A list of PDPRecord objects that match the specified date filters.
        """
        pass
