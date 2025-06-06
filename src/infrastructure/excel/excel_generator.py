import pandas as pd
from loguru import logger

from src.application.dto.excel_dto import ExcelGenerationDTO, SheetConfig
from src.shared.constants import HEATMAP_COLOR_SCALE


class ExcelGenerator:
    """Excel file generator with formatting and heatmap capabilities"""

    def generate(self, excel_dto: ExcelGenerationDTO) -> None:
        """Generate Excel file with multiple sheets and formatting"""
        try:
            logger.info(f"Generating Excel file: {excel_dto.output_filename}")

            # Create workbook
            with pd.ExcelWriter(
                excel_dto.output_filename, engine="xlsxwriter"
            ) as writer:
                for sheet_config in excel_dto.sheet_configs:
                    self._create_sheet(writer, sheet_config)

                # Get workbook and apply additional formatting
                workbook = writer.book

                for sheet_config in excel_dto.sheet_configs:
                    worksheet = writer.sheets[sheet_config.sheet_name]

                    if sheet_config.apply_filters:
                        self._apply_filters(worksheet, sheet_config)

                    if sheet_config.heatmap_config:
                        self._apply_heatmap(workbook, worksheet, sheet_config)

            logger.info(
                f"Excel file generated successfully: {excel_dto.output_filename}"
            )

        except Exception as e:
            logger.error(f"Error generating Excel: {str(e)}")
            raise

    def _create_sheet(self, writer: pd.ExcelWriter, sheet_config: SheetConfig) -> None:
        """Create a sheet with data"""
        # Convert data to DataFrame
        df = pd.DataFrame(sheet_config.data)

        # Reorder columns if headers are specified
        if sheet_config.headers:
            # Only include columns that exist in the data
            existing_columns = [h for h in sheet_config.headers if h in df.columns]
            df = df[existing_columns]

        # Write to Excel
        df.to_excel(writer, sheet_name=sheet_config.sheet_name, index=False)

        # Apply column widths if specified
        if sheet_config.column_widths:
            worksheet = writer.sheets[sheet_config.sheet_name]
            for col, width in sheet_config.column_widths.items():
                col_idx = df.columns.get_loc(col) if col in df.columns else None
                if col_idx is not None:
                    worksheet.set_column(col_idx, col_idx, width)

    def _apply_filters(self, worksheet, sheet_config: SheetConfig) -> None:
        """Apply autofilters to worksheet"""
        # Get dimensions
        df = pd.DataFrame(sheet_config.data)
        if not df.empty:
            last_row = len(df)
            last_col = len(df.columns) - 1
            worksheet.autofilter(0, 0, last_row, last_col)

    def _apply_heatmap(self, workbook, worksheet, sheet_config: SheetConfig) -> None:
        """Apply heatmap formatting to numeric columns"""
        df = pd.DataFrame(sheet_config.data)

        # Define formats for heatmap
        format_green = workbook.add_format({"bg_color": HEATMAP_COLOR_SCALE["min"]})
        format_yellow = workbook.add_format({"bg_color": HEATMAP_COLOR_SCALE["mid"]})
        format_red = workbook.add_format({"bg_color": HEATMAP_COLOR_SCALE["max"]})

        # Find numeric columns (days 1-31)
        numeric_columns = []
        for col in df.columns:
            if col.isdigit() and 1 <= int(col) <= 31:
                numeric_columns.append(col)

        # Apply conditional formatting to each numeric column
        for col in numeric_columns:
            col_idx = df.columns.get_loc(col)

            # Apply 3-color scale
            worksheet.conditional_format(
                1,
                col_idx,
                len(df),
                col_idx,
                {
                    "type": "3_color_scale",
                    "min_color": HEATMAP_COLOR_SCALE["min"],
                    "mid_color": HEATMAP_COLOR_SCALE["mid"],
                    "max_color": HEATMAP_COLOR_SCALE["max"],
                    "min_type": "min",
                    "mid_type": "percentile",
                    "max_type": "max",
                    "mid_value": 50,
                },
            )
