class ExcelHeaders:
    """Excel report headers"""

    # Temporal headers
    YEAR = "Año"
    MONTH = "Mes"
    DAY = "Día"
    DATE = "Fecha"
    HOUR = "Hora"
    PERIOD = "Periodo"

    # Agent headers
    DNI = "DNI"
    AGENT_NAME = "Ejecutivo"
    SUPERVISOR = "Supervisor"
    AGENT_EMAIL = "Correo Agente"

    # Metrics headers
    TOTAL_OPERATIONS = "Total Gestiones"
    EFFECTIVE_CONTACTS = "Contactos Efectivos"
    NO_CONTACTS = "No Contactos"
    NON_EFFECTIVE_CONTACTS = "Contactos No Efectivos"
    PDP_COUNT = "Gestiones PDP"
    PDP_PER_HOUR = "PDP/Hora"
    AVERAGE = "Promedio"

    # Legacy headers
    SERVICE = "Servicio"
    PORTFOLIO = "Cartera"
    DUE_DAY = "Vencimiento"
    MANAGED_AMOUNT = "Monto Gestionado"
    CONNECTED_TIME = "Tiempo Conectado"


# Excel Configuration
EXCEL_OUTPUT_PATH = "./output"
EXCEL_MAX_ROWS = 1048576
EXCEL_MAX_COLUMNS = 16384
HEATMAP_COLOR_SCALE = {"min": "#63BE7B", "mid": "#FFEB84", "max": "#F8696B"}

# BigQuery Configuration
BQ_BATCH_SIZE = 1000
BQ_TIMEOUT_SECONDS = 300
