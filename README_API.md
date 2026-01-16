# API de Licitaciones - contrataciondelestado.es

API REST construida con FastAPI para obtener licitaciones del portal de contratación del estado español.

## Características

- Scraping automático de licitaciones publicadas en contrataciondelestado.es
- Filtrado por códigos CPV (48000000 - Software y 72000000 - Servicios TI)
- Búsqueda de licitaciones publicadas el día actual
- Resultados en formato JSON
- Documentación interactiva automática (Swagger UI)

## Instalación

1. Asegúrate de tener el entorno virtual activado

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Iniciar el servidor

```bash
python main.py
```

O usando uvicorn directamente:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

### Endpoints disponibles

#### 1. Raíz - Información de la API
```
GET /
```

Respuesta:
```json
{
  "mensaje": "API de Licitaciones - contrataciondelestado.es",
  "version": "1.0.0",
  "endpoints": {
    "/licitaciones": "Obtener licitaciones del día",
    "/health": "Estado de la API"
  }
}
```

#### 2. Estado de la API
```
GET /health
```

Respuesta:
```json
{
  "status": "ok",
  "timestamp": "2025-12-28T10:30:00.123456"
}
```

#### 3. Obtener licitaciones del día
```
GET /licitaciones
GET /licitaciones?cpv_codes=48000000,72000000
```

**Parámetros de query:**
- `cpv_codes` (opcional): Códigos CPV separados por comas
  - Por defecto: `48000000,72000000` (Software y Servicios TI)
  - Ejemplo: `48000000` (solo Software)
  - Ejemplo: `72000000,48000000,30200000` (múltiples códigos)

**Ejemplos de uso:**
```bash
# Usar códigos CPV por defecto (48000000,72000000)
GET /licitaciones

# Buscar solo software (CPV 48000000)
GET /licitaciones?cpv_codes=48000000

# Buscar múltiples códigos CPV personalizados
GET /licitaciones?cpv_codes=48000000,72000000,30200000
```

Respuesta exitosa (200):
```json
{
  "success": true,
  "timestamp": "2025-12-28T10:30:00.123456",
  "codigos_cpv": ["48000000", "72000000"],
  "total_licitaciones": 15,
  "total_paginas": 2,
  "carpeta_salida": "datos_licitaciones/20251228_103000_abc123de",
  "licitaciones": [
    {
      "expediente": "EXP-2025-001",
      "descripcion": "Contratación de servicios de desarrollo de software",
      "tipo": "Servicios",
      "subtipo": "Servicios de TI",
      "estado": "Publicada",
      "importe": "150.000,00 EUR",
      "fecha": "28/12/2025",
      "organismo": "Ministerio de Administraciones Públicas",
      "enlace": "https://..."
    }
  ]
}
```

Respuesta con error (500):
```json
{
  "success": false,
  "error": "Descripción del error",
  "timestamp": "2025-12-28T10:30:00.123456"
}
```

### Documentación interactiva

Una vez iniciado el servidor, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Aquí podrás probar todos los endpoints de forma interactiva.

## Estructura del proyecto

```
.
├── main.py                          # Aplicación FastAPI con endpoints
├── scraper_selenium.py              # Lógica de scraping con Selenium
├── config.py                        # Configuración
├── logger.py                        # Configuración de logging
├── requirements.txt                 # Dependencias
├── datos_licitaciones/             # Carpeta con resultados de scraping
│   └── YYYYMMDD_HHMMSS_xxxxx/     # Carpeta por ejecución
│       ├── licitaciones_extraidas.json
│       ├── licitaciones_YYYYMMDD.csv
│       └── ...
└── logs/                           # Logs de la aplicación
```

## Notas

- El scraping tarda aproximadamente 30-60 segundos dependiendo del número de resultados
- Cada consulta al endpoint `/licitaciones` genera una carpeta nueva con los resultados
- Los resultados se guardan tanto en JSON como en CSV
- El navegador Chrome se ejecuta en modo headless (sin interfaz gráfica)

## Uso con cURL

```bash
# Obtener licitaciones con códigos CPV por defecto
curl http://localhost:8000/licitaciones

# Obtener solo licitaciones de software (CPV 48000000)
curl "http://localhost:8000/licitaciones?cpv_codes=48000000"

# Obtener múltiples códigos CPV personalizados
curl "http://localhost:8000/licitaciones?cpv_codes=48000000,72000000,30200000"

# Verificar estado
curl http://localhost:8000/health
```

## Uso con Python

```python
import requests

# Obtener licitaciones con códigos CPV por defecto
response = requests.get("http://localhost:8000/licitaciones")
data = response.json()

if data["success"]:
    print(f"Total licitaciones: {data['total_licitaciones']}")
    print(f"Códigos CPV usados: {data['codigos_cpv']}")
    for licitacion in data["licitaciones"]:
        print(f"- {licitacion['expediente']}: {licitacion['descripcion']}")
else:
    print(f"Error: {data['error']}")

# Buscar solo software (CPV 48000000)
response = requests.get("http://localhost:8000/licitaciones", params={"cpv_codes": "48000000"})

# Buscar múltiples códigos CPV
response = requests.get("http://localhost:8000/licitaciones", params={"cpv_codes": "48000000,72000000,30200000"})
```

## Desarrollo

Para ejecutar en modo desarrollo con recarga automática:

```bash
uvicorn main:app --reload
```

## Producción

Para producción, considera:

1. Desactivar el modo `--reload`
2. Usar múltiples workers: `--workers 4`
3. Configurar un reverse proxy (nginx)
4. Usar HTTPS
5. Implementar rate limiting
6. Agregar autenticación si es necesario

Ejemplo para producción:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```
