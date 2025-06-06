"""Domain constants"""

import os
from enum import Enum


class ServiceType(str, Enum):
    """Service type enumeration"""

    MOBILE = "MOVIL"
    FIXED = "FIJO"


class Portfolio(str, Enum):
    """Portfolio/Cartera enumeration"""

    EARLY_MANAGEMENT = "Gestión Temprana"
    FRACTIONING = "Fraccionamiento"
    NEW_ACCOUNTS = "Altas Nuevas"
    OTHER = "Otro"


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


# API Configuration
API_DATE_FORMAT = "%Y-%m-%d"
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "60"))
API_MAX_RETRIES = 3
API_RETRY_DELAY = 1
MAX_CONCURRENT_API_CALLS = int(os.getenv("MAX_CONCURRENT_API_CALLS", "10"))

# Excel Configuration
EXCEL_OUTPUT_PATH = os.getenv("EXCEL_OUTPUT_PATH", "./output")
EXCEL_MAX_ROWS = 1048576
EXCEL_MAX_COLUMNS = 16384
HEATMAP_COLOR_SCALE = {"min": "#63BE7B", "mid": "#FFEB84", "max": "#F8696B"}

# BigQuery Configuration
BQ_BATCH_SIZE = 1000
BQ_TIMEOUT_SECONDS = 300
