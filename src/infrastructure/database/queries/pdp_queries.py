"""BigQuery queries for PDP data"""

from datetime import date


class PDPQueries:
    """SQL queries for PDP data retrieval"""

    @staticmethod
    def get_pdps_by_filters(start_date: date, end_date: date) -> str:
        """Get PDPs filtered by specific dates and emails"""

        query = """
        SELECT
            date(fecha_hora) fecha,
            dni_ejecutivo,
            ejecutivo,
            ROUND(SUM(q_promesas) / COUNT(DISTINCT
                                          IF(EXTRACT(HOUR from fecha_hora) < 5,
                                             EXTRACT(HOUR from fecha_hora) + 19,
                                             EXTRACT(HOUR from fecha_hora) - 5)
                                    ), 2) as promesas_por_hora_dia
        FROM mibot-222814.BI_USA.dash_P3fV4dWNeMkN5RJMhV8e_fact_gestion_horaria g
                 LEFT JOIN mibot-222814.BI_USA.dash_P3fV4dWNeMkN5RJMhV8e_fact_asignacion a
                           ON g.cod_luna = a.cod_luna
        WHERE canal = 'CALL'
          AND dni_ejecutivo != 'SIN_DNI'
          AND date(fecha_hora) >= fecha_inicio_campana
          AND date(fecha_hora) <= fin_campana
          AND date(fecha_hora) >= @start_date
          AND date(fecha_hora) <= @end_date
        GROUP BY dni_ejecutivo, ejecutivo, date(fecha_hora)
        ORDER BY fecha, ejecutivo
        """

        return query
