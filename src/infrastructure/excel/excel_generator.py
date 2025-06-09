import pandas as pd
from loguru import logger

from src.application.dto.excel_dto import ExcelGenerationDTO, SheetConfig


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

    @staticmethod
    def _create_sheet(writer: pd.ExcelWriter, sheet_config: SheetConfig) -> None:
        """Create a sheet with data"""
        df = pd.DataFrame(sheet_config.data)

        if sheet_config.headers:
            existing_columns = [h for h in sheet_config.headers if h in df.columns]
            df = df[existing_columns]

        df.to_excel(writer, sheet_name=sheet_config.sheet_name, index=False)

        # Apply column widths if specified
        if sheet_config.column_widths:
            worksheet = writer.sheets[sheet_config.sheet_name]
            for col, width in sheet_config.column_widths.items():
                col_idx = df.columns.get_loc(col) if col in df.columns else None
                if col_idx is not None:
                    worksheet.set_column(col_idx, col_idx, width)

    @staticmethod
    def _apply_filters(worksheet, sheet_config: SheetConfig) -> None:
        """Apply autofilters to worksheet"""
        df = pd.DataFrame(sheet_config.data)
        if not df.empty:
            last_row = len(df)
            last_col = len(df.columns) - 1
            worksheet.autofilter(0, 0, last_row, last_col)

    @staticmethod
    def _apply_heatmap(workbook, worksheet, sheet_config: SheetConfig) -> None:
        """Apply heatmap formatting to numeric columns"""
        df = pd.DataFrame(sheet_config.data)

        # Define formats for the heatmap with borders
        format_red = workbook.add_format(
            {
                "bg_color": "#F8696B",
                "border": 1,
                "border_color": "#D3D3D3",
                "align": "center",
                "valign": "vcenter",
                "num_format": "0.00",
            }
        )
        format_yellow = workbook.add_format(
            {
                "bg_color": "#FFEB84",
                "border": 1,
                "border_color": "#D3D3D3",
                "align": "center",
                "valign": "vcenter",
                "num_format": "0.00",
            }
        )
        format_green = workbook.add_format(
            {
                "bg_color": "#63BE7B",
                "border": 1,
                "border_color": "#D3D3D3",
                "align": "center",
                "valign": "vcenter",
                "num_format": "0.00",
            }
        )
        format_white = workbook.add_format(
            {
                "bg_color": "#FFFFFF",
                "border": 1,
                "border_color": "#D3D3D3",
                "align": "center",
                "valign": "vcenter",
            }
        )

        # Header format
        header_format = workbook.add_format(
            {
                "bg_color": "#366092",
                "font_color": "#FFFFFF",
                "bold": True,
                "border": 1,
                "border_color": "#D3D3D3",
                "align": "center",
                "valign": "vcenter",
            }
        )

        # Apply header format
        for col_idx in range(len(df.columns)):
            worksheet.write(0, col_idx, df.columns[col_idx], header_format)

        # Find numeric columns (days)
        numeric_columns = []
        for col in df.columns:
            if isinstance(col, int) or (
                isinstance(col, str) and col.isdigit() and 1 <= int(col) <= 31
            ):
                numeric_columns.append(col)

        # Apply conditional formatting to each cell
        for row_idx in range(len(df)):
            for col in numeric_columns:
                col_idx = df.columns.get_loc(col)
                cell_value = df.iloc[row_idx][col]

                # Skip if value is empty or NaN
                if pd.isna(cell_value) or cell_value == "":
                    worksheet.write(row_idx + 1, col_idx, "", format_white)
                else:
                    try:
                        value = float(cell_value)
                        if value >= 3:
                            worksheet.write(row_idx + 1, col_idx, value, format_green)
                        elif value >= 2:
                            worksheet.write(row_idx + 1, col_idx, value, format_yellow)
                        elif value > 0:
                            worksheet.write(row_idx + 1, col_idx, value, format_red)
                        else:
                            worksheet.write(row_idx + 1, col_idx, "", format_white)
                    except:
                        worksheet.write(row_idx + 1, col_idx, "", format_white)

        # Set column widths
        worksheet.set_column(0, 0, 10)  # DNI
        worksheet.set_column(1, 1, 35)  # SUPERVISOR
        for idx, col in enumerate(numeric_columns):
            col_idx = df.columns.get_loc(col)
            worksheet.set_column(col_idx, col_idx, 5)  # Days columns

        # Total column
        if "Total" in df.columns:
            total_idx = df.columns.get_loc("Total")
            worksheet.set_column(total_idx, total_idx, 8)
