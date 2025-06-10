import pandas as pd
from loguru import logger

from src.application.dto import ExcelGenerationDTO, SheetConfig


class ExcelGenerator:
    """Excel file generator with formatting and heatmap capabilities"""

    def generate(self, excel_dto: ExcelGenerationDTO) -> None:
        try:
            logger.info(f"Generating Excel file: {excel_dto.output_filename}")

            with pd.ExcelWriter(
                excel_dto.output_filename, engine="xlsxwriter"
            ) as writer:
                for sheet_config in excel_dto.sheet_configs:
                    self._create_sheet(writer, sheet_config)

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
        df = pd.DataFrame(sheet_config.data)

        if sheet_config.headers:
            ordered_columns = []

            for header in sheet_config.headers:
                if header in df.columns:
                    ordered_columns.append(header)

            for col in df.columns:
                if col not in ordered_columns:
                    ordered_columns.append(col)

            df = df[ordered_columns]

        df.to_excel(writer, sheet_name=sheet_config.sheet_name, index=False)

        if sheet_config.column_widths:
            worksheet = writer.sheets[sheet_config.sheet_name]
            for col, width in sheet_config.column_widths.items():
                col_idx = df.columns.get_loc(col) if col in df.columns else None
                if col_idx is not None:
                    worksheet.set_column(col_idx, col_idx, width)

    @staticmethod
    def _apply_filters(worksheet, sheet_config: SheetConfig) -> None:
        df = pd.DataFrame(sheet_config.data)
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

    @staticmethod
    def _apply_heatmap(workbook, worksheet, sheet_config: SheetConfig) -> None:
        """Apply heatmap formatting to numeric columns"""
        df = pd.DataFrame(sheet_config.data)

        # Obtener la configuración del heatmap
        config = sheet_config.heatmap_config

        # Crear formato base común usando la configuración
        base_format = {
            "align": "center",
            "valign": "vcenter",
        }

        # Agregar bordes si está configurado
        if config.include_borders:
            base_format.update(
                {
                    "border": 1,
                    "border_color": "#D3D3D3",
                }
            )

        # Definir formatos usando los colores de la configuración
        formats = {
            "high": workbook.add_format(
                {
                    **base_format,
                    "bg_color": config.min_color,  # Verde para valores altos (buenos)
                    "num_format": "0.0",
                }
            ),
            "medium": workbook.add_format(
                {
                    **base_format,
                    "bg_color": config.mid_color,  # Amarillo para valores medios
                    "num_format": "0.0",
                }
            ),
            "low": workbook.add_format(
                {
                    **base_format,
                    "bg_color": config.max_color,  # Rojo para valores bajos
                    "num_format": "0.0",
                }
            ),
            "null": workbook.add_format(
                {
                    **base_format,
                    "bg_color": config.null_color,  # Blanco para vacíos
                }
            ),
            "header": workbook.add_format(
                {
                    **base_format,
                    "bg_color": config.header_color,
                    "font_color": "#FFFFFF",
                    "bold": True,
                }
            ),
        }

        # Aplicar formato a headers
        for col_idx, col_name in enumerate(df.columns):
            worksheet.write(0, col_idx, col_name, formats["header"])

        # Identificar columnas de días
        day_columns = [
            col for col in df.columns if col.isdigit() and 1 <= int(col) <= 31
        ]

        # Identificar columnas a formatear con heatmap
        heatmap_columns = set(day_columns)
        if "Promedio" in df.columns:
            heatmap_columns.add("Promedio")

        # Aplicar formato a celdas
        for row_idx in range(len(df)):
            for col_idx, col in enumerate(df.columns):
                cell_value = df.iloc[row_idx, col_idx]
                excel_row = row_idx + 1

                # Columnas de texto (DNI, EJECUTIVO)
                if col in ["DNI", "EJECUTIVO"]:
                    worksheet.write(excel_row, col_idx, cell_value, formats["null"])

                # Columnas numéricas con heatmap
                elif col in heatmap_columns:
                    # Determinar formato basado en valor
                    if cell_value == "" or cell_value is None or pd.isna(cell_value):
                        worksheet.write(excel_row, col_idx, "", formats["null"])
                    else:
                        try:
                            value = float(cell_value)
                            if value >= 3:
                                cell_format = formats["high"]
                            elif value >= 2:
                                cell_format = formats["medium"]
                            else:
                                cell_format = formats["low"]
                            worksheet.write(excel_row, col_idx, value, cell_format)
                        except (ValueError, TypeError):
                            worksheet.write(excel_row, col_idx, "", formats["null"])

        # Configurar anchos de columna
        worksheet.set_column(0, 0, 12)  # DNI
        worksheet.set_column(1, 1, 40)  # EJECUTIVO

        # Días - ancho uniforme
        for col in day_columns:
            col_idx = df.columns.get_loc(col)
            worksheet.set_column(col_idx, col_idx, 6)

        # Promedio
        if "Promedio" in df.columns:
            avg_idx = df.columns.get_loc("Promedio")
            worksheet.set_column(avg_idx, avg_idx, 12)

        # Congelar paneles
        worksheet.freeze_panes(1, 2)
