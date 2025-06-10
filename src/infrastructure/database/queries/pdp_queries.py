"""BigQuery queries for PDP data"""

from datetime import date


class PDPQueries:
    """SQL queries for PDP data retrieval"""

    @staticmethod
    def get_pdps_by_filters(start_date: date, end_date: date) -> str:
        """Get PDPs filtered by specific dates"""

        query = """
        SELECT
          -- Dimensiones temporales
          EXTRACT(DATE FROM mba.date) AS fecha,
          EXTRACT(HOUR FROM mba.date) AS hora,

          -- Información del ejecutivo
          COALESCE(u.nombre_apellidos, mba.nombre_agente, 'SIN NOMBRE') AS ejecutivo,
          COALESCE(CAST(u.dni AS STRING), 'SIN DNI') AS dni_ejecutivo,

          -- Solo cantidades
          COUNT(*) AS total_gestiones,
          COUNTIF(h.contactabilidad = 'Contacto Efectivo') AS contactos_efectivos,
          COUNTIF(h.contactabilidad = 'No contacto') AS no_contactos,
          COUNTIF(h.contactabilidad = 'Contacto No Efectivo') AS contactos_no_efectivos,
          COUNTIF(h.pdp = 'SI') AS gestiones_pdp

        FROM `BI_USA.mibotair_P3fV4dWNeMkN5RJMhV8e` mba
            LEFT JOIN `BI_USA.homologacion_P3fV4dWNeMkN5RJMhV8e_usuarios` u
                ON mba.correo_agente = u.usuario
            LEFT JOIN `BI_USA.homologacion_P3fV4dWNeMkN5RJMhV8e_v2` h
                ON mba.n1 = h.n_1 AND mba.n2 = h.n_2 AND mba.n3 = h.n_3

        WHERE COALESCE(u.nombre_apellidos, mba.nombre_agente, 'SIN NOMBRE') != ''
            AND COALESCE(u.nombre_apellidos, mba.nombre_agente, 'SIN NOMBRE') != 'SIN NOMBRE'
            AND EXTRACT(DATE FROM mba.date) >= @start_date
            AND EXTRACT(DATE FROM mba.date) <= @end_date

        GROUP BY
            fecha,
            hora,
            ejecutivo,
            dni_ejecutivo

        ORDER BY
            fecha ASC,
            hora ASC,
            total_gestiones DESC
        """

        return query
