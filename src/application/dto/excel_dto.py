from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ExcelGenerationDTO:
    """DTO for Excel generation parameters"""

    output_filename: str
    sheet_configs: List["SheetConfig"]


@dataclass
class SheetConfig:
    """Configuration for each Excel sheet"""

    sheet_name: str
    data: List[Dict[str, Any]]
    headers: List[str]
    column_widths: Dict[str, int] = None
    apply_filters: bool = True
    heatmap_config: Optional["HeatmapConfig"] = None


@dataclass
class HeatmapConfig:
    """Configuration for heatmap formatting"""

    value_column: str
    min_color: str = "#63BE7B"
    mid_color: str = "#FFEB84"
    max_color: str = "#F8696B"
    include_borders: bool = True
