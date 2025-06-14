from typing import Any

import numpy as np
import pandas as pd

from src.application.ports.services.data_transformation_service import (
    DataTransformationService,
)
from src.domain.entities.pdp_record import PDPRecord
from src.shared.constants import ExcelHeaders


class PandasTransformationService(DataTransformationService):
    """Pandas implementation of data transformation service"""

    def transform_to_tabular_format(
        self, records: list[PDPRecord]
    ) -> list[dict[str, Any]]:
        """Convert PDP records to tabular format using pandas"""

        if not records:
            return []

        # Create DataFrame directly from records
        df = pd.DataFrame([record.__dict__ for record in records]).rename(
            columns={
                "record_date": ExcelHeaders.DATE,
                "hour": ExcelHeaders.HOUR,
                "dni": ExcelHeaders.DNI,
                "agent_name": ExcelHeaders.AGENT_NAME,
                "total_operations": ExcelHeaders.TOTAL_OPERATIONS,
                "effective_contacts": ExcelHeaders.EFFECTIVE_CONTACTS,
                "no_contacts": ExcelHeaders.NO_CONTACTS,
                "non_effective_contacts": ExcelHeaders.NON_EFFECTIVE_CONTACTS,
                "pdp_count": ExcelHeaders.PDP_COUNT,
            }
        )
        df[ExcelHeaders.HOUR] = df[ExcelHeaders.HOUR].apply(lambda h: f"{h:02d}:00")

        return df.to_dict("records")

    def create_productivity_heatmap(
        self, records: list[PDPRecord], metric_field: str = "pdp_count"
    ) -> list[dict[str, Any]]:
        """Transform records into heatmap data (metric per hour by day)"""
        if not records:
            return []
        df = pd.DataFrame([record.__dict__ for record in records])

        df["day"] = pd.to_datetime(df["record_date"]).dt.day

        grouped = (
            df.groupby(["dni", "agent_name", "day"])
            .agg({metric_field: "sum", "hour": "nunique"})
            .reset_index()
        )
        grouped["average"] = (grouped[metric_field] / grouped["hour"]).round(1)

        pivot_result = grouped.pivot_table(
            index=["dni", "agent_name"],
            columns="day",
            values="average",
            fill_value=np.nan,
        )

        pivot_result["Promedio"] = pivot_result.mean(axis=1, skipna=True).round(1)

        result_df = pivot_result.reset_index()
        result = []
        for _, row in result_df.iterrows():
            row_dict = {"DNI": row["dni"], "EJECUTIVO": row["agent_name"]}
            for col in result_df.columns:
                if isinstance(col, (int, np.integer)):
                    value = row[col]
                    row_dict[str(col)] = "" if pd.isna(value) else value

            row_dict["Promedio"] = row["Promedio"]
            result.append(row_dict)

        return sorted(result, key=lambda x: x["Promedio"], reverse=True)
