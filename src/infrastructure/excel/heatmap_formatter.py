from typing import Any, Dict, List

import pandas as pd
from loguru import logger


class HeatmapFormatter:
    """Formatter for creating heatmap data structure"""

    @staticmethod
    def format_productivity_heatmap(data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Format data for productivity heatmap (agents x days)
        """
        logger.info("Formatting heatmap")

        df = pd.DataFrame(data)
        HeatmapFormatter._ensure_columns(df)

        pivot = (
            df.pivot_table(
                values="pdp_per_hour",
                index=["dni", "agent_name"],
                columns="day",
                aggfunc="mean",
            )
            .reindex(columns=sorted(df["day"].unique()), fill_value=None)
            .reset_index()
            .rename(columns={"agent_name": "SUPERVISOR"})
        )

        # Round values to 2 decimals
        numeric_columns = [col for col in pivot.columns if isinstance(col, int)]
        pivot[numeric_columns] = pivot[numeric_columns].round(2).replace([0, pd.NA], "")

        # Calculate totals (ignoring empty values)
        pivot["Total"] = (
            pivot[numeric_columns]
            .apply(pd.to_numeric, errors="coerce")
            .sum(axis=1)
            .round(2)
        )

        # Sort by total descending
        pivot = pivot.sort_values("Total", ascending=False)

        logger.info(
            f"Heatmap formatted with {len(pivot)} "
            f"agents and {len(numeric_columns)} days"
        )

        return pivot

    @staticmethod
    def _ensure_columns(df):
        required_columns = {"dni", "agent_name", "day", "pdp_per_hour"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
