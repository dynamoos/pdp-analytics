class ExcelHeaders:
    """Excel report headers"""

    YEAR = "Año"
    MONTH = "Mes"
    DAY = "Día"
    DATE = "Fecha"
    PERIOD = "Periodo"
    SERVICE = "Servicio"
    PORTFOLIO = "Cartera"
    DUE_DAY = "Vencimiento"
    DNI = "DNI"
    SUPERVISOR = "Supervisor"
    AGENT_NAME = "Nombre Agente"
    AGENT_EMAIL = "Correo Agente"
    PDP_COUNT = "Cantidad PDP"
    TOTAL_OPERATIONS = "Total Gestiones"
    MANAGED_AMOUNT = "Monto Gestionado"
    CONNECTED_TIME = "Tiempo Conectado"
    PDP_HOURS = "PDP/Hora"


# Excel Configuration
EXCEL_OUTPUT_PATH = "./output"
EXCEL_MAX_ROWS = 1048576
EXCEL_MAX_COLUMNS = 16384
HEATMAP_COLOR_SCALE = {"min": "#63BE7B", "mid": "#FFEB84", "max": "#F8696B"}

# BigQuery Configuration
BQ_BATCH_SIZE = 1000
BQ_TIMEOUT_SECONDS = 300
