import os
from datetime import datetime

# Configuración base
BASE_URL = "https://contrataciondelestado.es"
PLATAFORMA_URL = "https://contrataciondelestado.es/wps/portal/plataforma"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "datos_licitaciones")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

# Crear directorios si no existen
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Configuración de scraping
TIMEOUT = 30
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5

# Rutas de archivo
def get_output_file(date=None):
    """Genera el nombre del archivo de salida con la fecha"""
    if date is None:
        date = datetime.now()
    filename = f"licitaciones_{date.strftime('%Y%m%d')}.csv"
    return os.path.join(OUTPUT_DIR, filename)

def get_log_file(date=None):
    """Genera el nombre del archivo de log con la fecha"""
    if date is None:
        date = datetime.now()
    filename = f"scraping_{date.strftime('%Y%m%d')}.log"
    return os.path.join(LOG_DIR, filename)

# Configuración de horarios
SCRAP_TIME = "09:00"  # Hora diaria para ejecutar el scraping
