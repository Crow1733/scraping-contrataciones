# API de Scraping de Licitaciones

API REST con FastAPI para realizar scraping de licitaciones de contrataciondelestado.es con filtros dinámicos por códigos CPV.

## 🚀 Características

- **API REST** con FastAPI
- **Filtros CPV opcionales**: Si no se especifican códigos CPV, busca todas las licitaciones del día
- **Búsqueda por fecha**: Filtra licitaciones publicadas hoy
- **Documentación automática**: Swagger UI disponible en `/docs`
- **Formato JSON**: Respuestas estructuradas en JSON

## 📋 Instalación

1. Instalar dependencias:
```powershell
pip install -r requirements.txt
```

## 🏃 Ejecutar la API

```powershell
python main.py
```

O directamente con uvicorn:
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

## 📡 Endpoints

### 1. Raíz - GET `/`
Información general de la API

**Ejemplo:**
```powershell
curl http://localhost:8000/
```

### 2. Health Check - GET `/health`
Verificar el estado de la API

**Ejemplo:**
```powershell
curl http://localhost:8000/health
```

### 3. Obtener Licitaciones - GET `/licitaciones`

Realiza scraping de licitaciones publicadas hoy.

**Parámetros (Query):**
- `cpv_codes` (opcional): Códigos CPV separados por comas

**Comportamiento:**
- ✅ **Con CPV**: Filtra solo por los códigos especificados
- ✅ **Sin CPV**: Devuelve todas las licitaciones del día (no filtra por CPV)

#### Ejemplos de uso:

##### Sin filtro CPV (todas las licitaciones):
```powershell
# PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/licitaciones" -Method GET

# curl
curl http://localhost:8000/licitaciones
```

##### Con un código CPV:
```powershell
# PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/licitaciones?cpv_codes=48000000" -Method GET

# curl
curl "http://localhost:8000/licitaciones?cpv_codes=48000000"
```

##### Con múltiples códigos CPV:
```powershell
# PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/licitaciones?cpv_codes=48000000,72000000" -Method GET

# curl
curl "http://localhost:8000/licitaciones?cpv_codes=48000000,72000000"
```

#### Respuesta exitosa:

```json
{
  "success": true,
  "timestamp": "2026-01-05T10:30:00.123456",
  "total_licitaciones": 15,
  "carpeta_salida": "datos_licitaciones/20260105_103000_abc123de",
  "filtro_cpv": "ninguno",
  "licitaciones": [
    {
      "expediente": "EXP-2026-001",
      "descripcion": "Suministro de software...",
      "tipo": "Suministros",
      "subtipo": "Compra",
      "estado": "Publicada",
      "importe": "50.000,00 EUR",
      "fecha": "05/01/2026",
      "organismo": "Ministerio...",
      "enlace": "https://..."
    }
  ]
}
```

#### Respuesta con códigos CPV:

```json
{
  "success": true,
  "timestamp": "2026-01-05T10:30:00.123456",
  "total_licitaciones": 8,
  "carpeta_salida": "datos_licitaciones/20260105_103000_abc123de",
  "codigos_cpv": ["48000000", "72000000"],
  "licitaciones": [...]
}
```

#### Respuesta de error:

```json
{
  "detail": {
    "success": false,
    "error": "Descripción del error",
    "timestamp": "2026-01-05T10:30:00.123456"
  }
}
```

## 🔍 Códigos CPV comunes

- **48000000**: Paquetes de software y sistemas de información
- **72000000**: Servicios de tecnología de la información (TI)
- **45000000**: Obras de construcción
- **50000000**: Servicios de reparación y mantenimiento
- **71000000**: Servicios de arquitectura, ingeniería y planificación

## 📁 Archivos generados

Cada ejecución crea una carpeta con timestamp único en `datos_licitaciones/`:

```
datos_licitaciones/
└── 20260105_103000_abc123de/
    ├── licitaciones_extraidas.json
    ├── licitaciones_20260105.csv
    ├── screenshot_formulario.png
    ├── resultados_pagina_1.html
    └── ...
```

## 📝 Logs

Los logs se guardan en la carpeta `logs/` con el formato:
```
logs/scraping_YYYYMMDD.log
```

## 🛠️ Desarrollo

Para desarrollo con recarga automática:
```powershell
uvicorn main:app --reload
```

## 📚 Documentación interactiva

Una vez la API esté ejecutándose, visita:
- **Swagger UI**: http://localhost:8000/docs
  - Interfaz interactiva para probar endpoints
  - Incluye ejemplos y validación automática
  
- **ReDoc**: http://localhost:8000/redoc
  - Documentación alternativa más limpia

## ⚙️ Configuración

La configuración se gestiona en `config.py`:
- `TIMEOUT`: Tiempo de espera para operaciones
- `OUTPUT_DIR`: Directorio de salida
- `LOG_DIR`: Directorio de logs

## 🐛 Troubleshooting

### Error: "ChromeDriver not found"
- El script instala automáticamente ChromeDriver con `webdriver-manager`
- Asegúrate de tener Google Chrome instalado

### Error: Timeout al cargar la página
- Aumenta el `TIMEOUT` en `config.py`
- Verifica tu conexión a internet

### No se encuentran licitaciones
- Verifica los códigos CPV
- Revisa los logs en `logs/`
- Comprueba los archivos HTML generados para debugging
