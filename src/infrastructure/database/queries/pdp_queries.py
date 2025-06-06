"""BigQuery queries for PDP data"""

from datetime import date


class PDPQueries:
    """SQL queries for PDP data retrieval"""

    @staticmethod
    def get_pdps_by_date_range(
        start_date: date,
        end_date: date,
    ) -> str:
        """Get PDPs filtered by date range and optional filters"""

        # Base query with CTEs
        query = """
        WITH asignacion_base AS (
            SELECT
                cod_luna,
                CAST(cuenta AS STRING) AS cuenta,
                EXTRACT(DAY FROM min_vto) AS dia_vencimiento,
                CASE
                    WHEN UPPER(negocio) = 'MOVIL' THEN 'MOVIL'
                    ELSE 'FIJA'
                END AS servicio,
                CASE
                    WHEN LOWER(archivo) LIKE '%temprana%' THEN 'Gestión Temprana'
                    WHEN LOWER(archivo) LIKE '%cf%ann%' THEN 'Fraccionamiento'
                    WHEN LOWER(archivo) LIKE '%an%' THEN 'Altas Nuevas'
                    ELSE 'Otro'
                END AS cartera,
                ROW_NUMBER() OVER (
                    PARTITION BY cod_luna, negocio, min_vto
                    ORDER BY creado_el ASC
                ) AS rn
            FROM mibot-222814.BI_USA.batch_P3fV4dWNeMkN5RJMhV8e_asignacion
            WHERE cod_luna IS NOT NULL
              AND creado_el >= @start_date
        ),

        deudas_base AS (
            SELECT
                cod_cuenta,
                nro_documento,
                monto_exigible,
                creado_el,
                ROW_NUMBER() OVER (
                    PARTITION BY cod_cuenta, nro_documento
                    ORDER BY creado_el DESC
                ) AS rn_deuda
            FROM mibot-222814.BI_USA.batch_P3fV4dWNeMkN5RJMhV8e_tran_deuda
            WHERE creado_el >= @start_date
        ),

        calendario_normalizado AS (
            SELECT
                servicio,
                CASE
                    WHEN mes = 'Enero' THEN 1 WHEN mes = 'Febrero' THEN 2 WHEN mes = 'Marzo' THEN 3
                    WHEN mes = 'Abril' THEN 4 WHEN mes = 'Mayo' THEN 5 WHEN mes = 'Junio' THEN 6
                    WHEN mes = 'Julio' THEN 7 WHEN mes = 'Agosto' THEN 8 WHEN mes = 'Septiembre' THEN 9
                    WHEN mes = 'Octubre' THEN 10 WHEN mes = 'Noviembre' THEN 11 WHEN mes = 'Diciembre' THEN 12
                END AS mes_numero,
                mes AS nombre_mes,
                CASE
                    WHEN segmento = 'Temprana' THEN 'Gestión Temprana'
                    WHEN segmento = 'AN' THEN 'Altas Nuevas'
                    WHEN segmento = 'CF' THEN 'Fraccionamiento'
                    ELSE segmento
                END AS cartera,
                vct AS dia_vencimiento
            FROM mibot-222814.BI_USA.calendario_telf_peru
            WHERE inicio_gestion <= CURRENT_DATE()
              AND fin >= @start_date
        )

        SELECT
            -- Temporal fields
            EXTRACT(YEAR FROM g.date) AS anio,
            EXTRACT(MONTH FROM g.date) AS mes,
            EXTRACT(DAY FROM g.date) AS dia,
            DATE(g.date) AS fecha,
            FORMAT_DATE('%Y-%m', DATE(g.date)) AS periodo_mes,
            COALESCE(c.nombre_mes, 'Sin Mes') AS nombre_mes,

            -- Classification fields
            COALESCE(a.servicio, 'Sin Servicio') AS servicio,
            COALESCE(a.cartera, 'Sin Cartera') AS cartera,
            COALESCE(a.dia_vencimiento, 0) AS vencimiento,

            -- Agent fields
            u.dni,
            u.nombre_apellidos,
            g.correo_agente,

            -- Metrics
            COUNT(DISTINCT g.document) AS cant_pdp,
            COUNT(*) AS total_gestiones_pdp,
            SUM(COALESCE(d.monto_exigible, 0)) AS monto_total_gestionado,
            COUNT(DISTINCT DATE(g.date)) AS dias_con_pdp,
            COUNT(DISTINCT d.nro_documento) AS documentos_con_deuda,
            AVG(COALESCE(d.monto_exigible, 0)) AS monto_promedio_por_documento

        FROM mibot-222814.BI_USA.mibotair_P3fV4dWNeMkN5RJMhV8e g

        -- JOIN with users
        JOIN mibot-222814.BI_USA.homologacion_P3fV4dWNeMkN5RJMhV8e_usuarios u
            ON g.correo_agente = u.usuario

        -- JOIN with assignments
        LEFT JOIN asignacion_base a
            ON CAST(g.document AS STRING) = CAST(a.cod_luna AS STRING)
            AND a.rn = 1

        -- JOIN with debts
        LEFT JOIN deudas_base d
            ON a.cuenta = d.cod_cuenta
            AND d.rn_deuda = 1

        -- JOIN with calendar
        LEFT JOIN calendario_normalizado c
            ON a.servicio = c.servicio
            AND a.cartera = c.cartera
            AND a.dia_vencimiento = c.dia_vencimiento
            AND EXTRACT(MONTH FROM g.date) = c.mes_numero

        WHERE g.n2 = 'PDP'
          AND g.date >= @start_date
          AND g.date <= @end_date
        """

        query += """
        GROUP BY
            anio, mes, dia, fecha, periodo_mes,
            servicio, cartera, vencimiento, nombre_mes,
            u.dni, u.nombre_apellidos, g.correo_agente

        ORDER BY
            monto_total_gestionado DESC,
            fecha DESC,
            servicio,
            cartera,
            u.nombre_apellidos
        """

        return query
