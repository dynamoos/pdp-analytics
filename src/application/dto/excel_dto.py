from dataclasses import dataclass
from typing import Any


@dataclass
class HeatmapConfig:
    """Configuration for heatmap formatting"""

    value_column: str
    min_color: str = "#63BE7B"
    mid_color: str = "#FFEB84"
    max_color: str = "#F8696B"
    null_color: str = "#FFFFFF"
    header_color: str = "#366092"
    include_borders: bool = True


@dataclass
class SheetConfig:
    """Configuration for each Excel sheet"""

    sheet_name: str
    data: list[dict[str, Any]]
    apply_filters: bool = True
    heatmap_ranges: dict[str, float] | None = None


@dataclass
class ExcelGenerationDTO:
    """DTO for Excel generation parameters"""

    output_filename: str
    sheet_configs: list[SheetConfig]
