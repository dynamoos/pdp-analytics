from datetime import date
from typing import Any, Dict, List

import pandas as pd
from loguru import logger

from src.shared.constants import HEATMAP_COLOR_SCALE


class HeatmapFormatter:
    """Formatter for creating heatmap data structure"""

    def format_productivity_heatmap(
        self, data: List[Dict[str, Any]], month: int, year: int
    ) -> pd.DataFrame:
        """
        Format data for productivity heatmap (agents x days)
        """
        logger.info(f"Formatting heatmap for {year}-{month:02d}")

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Ensure we have the required columns
        required_columns = ["dni", "agent_name", "day", "pdp_per_hour"]
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Create pivot table: agents as rows, days as columns
        pivot = df.pivot_table(
            values="pdp_per_hour",
            index=["dni", "agent_name"],
            columns="day",
            fill_value=0,
            aggfunc="mean",  # Average if multiple records per day
        )

        # Ensure all days of month are present
        days_in_month = self._get_days_in_month(year, month)
        for day in range(1, days_in_month + 1):
            if day not in pivot.columns:
                pivot[day] = 0

        # Sort columns (days)
        pivot = pivot.reindex(columns=sorted(pivot.columns))

        # Reset index to make dni and agent_name regular columns
        pivot = pivot.reset_index()

        # Add supervisor column (placeholder for now)
        pivot.insert(2, "supervisor", "N/A")

        # Round values to 2 decimals
        numeric_columns = [col for col in pivot.columns if isinstance(col, int)]
        pivot[numeric_columns] = pivot[numeric_columns].round(2)

        # Calculate totals
        pivot["Total"] = pivot[numeric_columns].sum(axis=1).round(2)

        # Sort by total descending
        pivot = pivot.sort_values("Total", ascending=False)

        logger.info(
            f"Heatmap formatted with {len(pivot)} "
            f"agents and {len(numeric_columns)} days"
        )

        return pivot

    @staticmethod
    def _get_days_in_month(year: int, month: int) -> int:
        """Get number of days in a month"""
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        last_day = next_month - pd.Timedelta(days=1)
        return last_day.day

    def apply_color_gradient(self, value: float, min_val: float, max_val: float) -> str:
        """
        Calculate color based on value within range
        Returns hex color code
        """
        if max_val == min_val:
            return HEATMAP_COLOR_SCALE["mid"]

        # Normalize value to 0-1 range
        normalized = (value - min_val) / (max_val - min_val)

        # Determine color based on normalized value
        if normalized < 0.5:
            # Green to Yellow
            return self._interpolate_color(
                HEATMAP_COLOR_SCALE["min"], HEATMAP_COLOR_SCALE["mid"], normalized * 2
            )
        else:
            # Yellow to Red
            return self._interpolate_color(
                HEATMAP_COLOR_SCALE["mid"],
                HEATMAP_COLOR_SCALE["max"],
                (normalized - 0.5) * 2,
            )

    def _interpolate_color(self, color1: str, color2: str, factor: float) -> str:
        """Interpolate between two hex colors"""
        # Convert hex to RGB
        c1 = self._hex_to_rgb(color1)
        c2 = self._hex_to_rgb(color2)

        # Interpolate
        r = int(c1[0] + (c2[0] - c1[0]) * factor)
        g = int(c1[1] + (c2[1] - c1[1]) * factor)
        b = int(c1[2] + (c2[2] - c1[2]) * factor)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
