from abc import ABC, abstractmethod
from typing import Any

from src.domain.entities import PDPRecord


class DataTransformationService(ABC):
    """
    Provides abstract methods for data transformation services.

    This class outlines the key methods required for transforming
    PDP records into various tabular data formats and generating
    productivity heatmaps.
    """

    @abstractmethod
    def transform_to_tabular_format(
        self, records: list[PDPRecord]
    ) -> list[dict[str, Any]]:
        """
        Transforms PDP records into tabular data structure.

        :param records: List of PDP records to be converted.
        :return: A list of dictionaries containing the tabular representation of records.
        """
        pass

    @abstractmethod
    def create_productivity_heatmap(
        self, records: list[PDPRecord], metric_field: str = "pdp_count"
    ) -> list[dict[str, Any]]:
        """
        Convert PDP records into heatmap-friendly tabular format.


        :param records: A list of PDP records to be converted.
        :param metric_field: The field in the PDP records representing the productivity
        :return:
            A list where each element is a dictionary containing the
            tabular data for each row.
        """
        pass
