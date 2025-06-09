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

        # Ensure columns are in the correct order based on headers
        if sheet_config.headers:
            # Reorder columns to match headers
            ordered_columns = []
            for header in sheet_config.headers:
                if header in df.columns:
                    ordered_columns.append(header)

            df = df[ordered_columns]

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
        """Apply filters to the worksheet"""
        df = pd.DataFrame(sheet_config.data)
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

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
        day_columns = []
        for col in df.columns:
            if col.isdigit() and 1 <= int(col) <= 31:
                day_columns.append(col)

        # Apply conditional formatting to each cell
        for row_idx in range(len(df)):
            # Format DNI and SUPERVISOR columns
            for col_idx, col in enumerate(df.columns):
                if col in ["DNI", "SUPERVISOR"]:
                    worksheet.write(
                        row_idx + 1, col_idx, df.iloc[row_idx][col], format_white
                    )

            # Format day columns
            for col in day_columns:
                col_idx = df.columns.get_loc(col)
                cell_value = df.iloc[row_idx][col]

                # Handle empty, NaN, or empty string
                if pd.isna(cell_value) or cell_value == "" or cell_value is None:
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
                    except (ValueError, TypeError):
                        worksheet.write(row_idx + 1, col_idx, "", format_white)

        # Format para la columna Promedio (con fondo azul claro)
        format_average = workbook.add_format(
            {
                "bg_color": "#DCE6F1",
                "border": 1,
                "border_color": "#D3D3D3",
                "align": "center",
                "valign": "vcenter",
                "num_format": "0.00",
                "bold": True,
            }
        )

        # Aplicar formato a la columna Promedio
        if "Promedio" in df.columns:
            avg_idx = df.columns.get_loc("Promedio")
            for row_idx in range(len(df)):
                value = df.iloc[row_idx]["Promedio"]
                worksheet.write(row_idx + 1, avg_idx, value, format_average)

        # Set column widths
        worksheet.set_column(0, 0, 12)  # DNI
        worksheet.set_column(1, 1, 40)  # SUPERVISOR

        # Day columns
        for col in day_columns:
            col_idx = df.columns.get_loc(col)
            worksheet.set_column(col_idx, col_idx, 6)

        # Promedio column
        if "Promedio" in df.columns:
            avg_idx = df.columns.get_loc("Promedio")
            worksheet.set_column(avg_idx, avg_idx, 12)

        # Freeze panes (optional - keeps headers visible when scrolling)
        worksheet.freeze_panes(1, 2)  # Freeze first row and first two columns
