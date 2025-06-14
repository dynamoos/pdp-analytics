import pandas as pd
from loguru import logger

from src.application.dto import ExcelGenerationDTO, SheetConfig


class ExcelGenerator:
    """Excel file generator with formatting and heatmap capabilities"""

    def generate(self, excel_dto: ExcelGenerationDTO) -> None:
        """Generate Excel file from DTO configuration."""
        try:
            logger.info(f"Generating Excel file: {excel_dto.output_filename}")

            with pd.ExcelWriter(
                excel_dto.output_filename, engine="xlsxwriter"
            ) as writer:
                self._create_all_sheets(writer, excel_dto.sheet_configs)
                self._apply_sheet_formatting(writer, excel_dto.sheet_configs)

            logger.info(
                f"Excel file generated successfully: {excel_dto.output_filename}"
            )

        except Exception as e:
            logger.error(f"Error generating Excel: {str(e)}")
            raise

    @staticmethod
    def _create_all_sheets(
        writer: pd.ExcelWriter, sheet_configs: list[SheetConfig]
    ) -> None:
        """Create all Excel sheets with data."""
        for config in sheet_configs:
            df = pd.DataFrame(config.data)
            df.to_excel(writer, sheet_name=config.sheet_name, index=False)

    def _apply_sheet_formatting(
        self, writer: pd.ExcelWriter, sheet_configs: list[SheetConfig]
    ) -> None:
        """Apply formatting to all sheets."""
        workbook = writer.book

        for config in sheet_configs:
            worksheet = writer.sheets[config.sheet_name]

            if config.apply_filters:
                self._apply_filters(worksheet, config)

            if config.heatmap_ranges:
                formatter = HeatmapFormatter(workbook, worksheet, config)
                formatter.apply()

            self._auto_fit_columns(worksheet, config)

    @staticmethod
    def _apply_filters(worksheet, sheet_config: SheetConfig) -> None:
        """Apply autofilters to worksheet."""
        df = pd.DataFrame(sheet_config.data)
        if not df.empty:
            worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

    @staticmethod
    def _auto_fit_columns(worksheet, sheet_config: SheetConfig) -> None:
        """Auto-fit all columns based on content."""
        df = pd.DataFrame(sheet_config.data)

        for col_idx, col_name in enumerate(df.columns):
            max_length = len(str(col_name))

            if not df.empty:
                content_max = df[col_name].astype(str).str.len().max()
                max_length = max(max_length, content_max)

            adjusted_width = min(max_length * 1.1 + 2, 50)
            adjusted_width = max(adjusted_width, 8)

            worksheet.set_column(col_idx, col_idx, adjusted_width)


class HeatmapFormatter:
    """Handles heatmap formatting for Excel worksheets."""

    def __init__(self, workbook, worksheet, sheet_config: SheetConfig):
        self.workbook = workbook
        self.worksheet = worksheet
        self.config = sheet_config
        self.df = pd.DataFrame(sheet_config.data)
        self.formats = self._create_formats()

    def apply(self) -> None:
        """Apply heatmap formatting to worksheet."""
        self._format_headers()
        self._format_data_cells()

    def _create_formats(self) -> dict:
        """Create cell formats for heatmap."""
        base_format = {
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#D3D3D3",
            "num_format": "0.0",
        }

        return {
            "high": self.workbook.add_format(
                {
                    **base_format,
                    "bg_color": "#63BE7B",  # Green
                }
            ),
            "medium": self.workbook.add_format(
                {
                    **base_format,
                    "bg_color": "#FFEB84",  # Yellow
                }
            ),
            "low": self.workbook.add_format(
                {
                    **base_format,
                    "bg_color": "#F8696B",  # Red
                }
            ),
            "text": self.workbook.add_format(
                {
                    **base_format,
                    "bg_color": "#FFFFFF",  # White
                }
            ),
            "header": self.workbook.add_format(
                {
                    **base_format,
                    "bg_color": "#366092",
                    "font_color": "#FFFFFF",
                    "bold": True,
                }
            ),
        }

    def _format_headers(self) -> None:
        """Format header row."""
        for col_idx, col_name in enumerate(self.df.columns):
            self.worksheet.write(0, col_idx, col_name, self.formats["header"])

    def _format_data_cells(self) -> None:
        """Format data cells based on content type and value."""
        numeric_columns = self._identify_numeric_columns()

        for row_idx in range(len(self.df)):
            for col_idx, col_name in enumerate(self.df.columns):
                cell_value = self.df.iloc[row_idx, col_idx]
                excel_row = row_idx + 1

                if col_name in numeric_columns:
                    self._format_numeric_cell(excel_row, col_idx, cell_value)
                else:
                    self._format_text_cell(excel_row, col_idx, cell_value)

    def _identify_numeric_columns(self) -> set[str]:
        """Identify columns that should have numeric formatting."""
        numeric_cols = set()

        # Day columns (1-31)
        for col in self.df.columns:
            if col.isdigit() and 1 <= int(col) <= 31:
                numeric_cols.add(col)

        # Average column
        if "Promedio" in self.df.columns:
            numeric_cols.add("Promedio")

        return numeric_cols

    def _format_numeric_cell(self, row: int, col: int, value) -> None:
        """Format numeric cell with heatmap colors."""
        if pd.isna(value) or value == "":
            self.worksheet.write(row, col, "", self.formats["text"])
        else:
            try:
                numeric_value = float(value)
                cell_format = self._get_format_for_value(numeric_value)
                self.worksheet.write(row, col, numeric_value, cell_format)
            except (ValueError, TypeError):
                self.worksheet.write(row, col, "", self.formats["text"])

    def _get_format_for_value(self, value: float) -> object:
        """Determine format based on value and configured ranges."""
        ranges = self.config.heatmap_ranges

        if value >= ranges["high"]:
            return self.formats["high"]
        elif value >= ranges["medium"]:
            return self.formats["medium"]
        else:
            return self.formats["low"]

    def _format_text_cell(self, row: int, col: int, value) -> None:
        """Format text cell."""
        self.worksheet.write(row, col, value, self.formats["text"])
