# 🏛️ API de Licitaciones - contrataciondelestado.es

API REST construida con FastAPI para obtener licitaciones del portal oficial de contratación del estado español mediante web scraping con Selenium.

## 📋 Características

- ✅ Scraping automático de licitaciones en tiempo real
- ✅ Filtrado por códigos CPV (Clasificación de Productos y Servicios)
- ✅ Búsqueda por rangos de fechas personalizables
- ✅ Filtro por estado (Publicada, Evaluación, Adjudicada, etc.)
- ✅ Paginación automática de resultados
- ✅ Exportación a CSV y JSON
- ✅ Documentación interactiva (Swagger UI)
- ✅ Modo headless (sin interfaz gráfica)
- ✅ Autenticación con API Key

## 🚀 Instalación

### Requisitos previos

**Windows:**
- Python 3.8+
- Google Chrome instalado
- pip

**Ubuntu/Linux:**
```bash
# Instalar Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# Dependencias de Chrome headless
sudo apt install -y libnss3 libatk-bridge2.0-0t64 libdrm2 libxkbcommon0 libgbm1 libasound2t64
```

### Pasos de instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/scraping-contrataciones.git
cd scraping-contrataciones
```

2. **Crear entorno virtual:**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Ubuntu
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```
4. **Configurar autenticación:**

Crea un archivo `.env` en la raíz del proyecto:
```bash
# Windows
copy .env.example .env

# Linux
cp .env.example .env
```

Edita el archivo `.env` y genera tu API Key:
```env
API_KEY=tu_clave_secreta_aqui
```
 (público)
```bash
curl http://localhost:8000/
```

#### **GET /health** - Estado del servicio (público)
```bash
curl http://localhost:8000/health
```

#### **GET /licitaciones** - Obtener licitaciones (requiere autenticación)

⚠️ **Todos los ejemplos requieren el header `X-API-Key` con tu clave**

**Sin parámetros** (licitaciones de hoy):
```bash
curl -H "X-API-Key: TU_API_KEY" http://localhost:8000/licitaciones
```

**Con códigos CPV** (Software y Servicios TI):
```bash
curl -H "X-API-Key: TU_API_KEY" \
     "http://localhost:8000/licitaciones?cpv_codes=48000000,72000000"
```

**Con rango de fechas:**
```bash
curl -H "X-API-Key: TU_API_KEY" \
     "http://localhost:8000/licitaciones?fecha_desde=01-01-2026&fecha_hasta=31-01-2026"
```

**Ejemplo completo:**
```bash
curl -H "X-API-Key: TU_API_KEY" \
    

#### **GET /licitaciones** - Obtener licitaciones

**Sin parámetros** (licitaciones de hoy):
```bash
curl http://localhost:8000/licitaciones
```

**Con códigos CPV** (Software y Servicios TI):
```bash
curl "http://localhost:8000/licitaciones?cpv_codes=48000000,72000000"
```

**Con rango de fechas:**
```bash
curl "http://localhost:8000/licitaciones?fecha_desde=01-01-2026&fecha_hasta=31-01-2026"
```

**Ejemplo completo:**
```bash
curl "http://localhost:8000/licitaciones?cpv_codes=48000000&fecha_desde=10-01-2026&fecha_hasta=15-01-2026"
```

### Respuesta ejemplo

```json
{
  "success": true,
  "timestamp": "2026-01-16T10:30:00",
  "total_licitaciones": 25,
  "codigos_cpv": ["48000000", "72000000"],
  "fecha_desde": "15-01-2026",
  "fecha_hasta": "15-01-2026",
  "licitaciones": [
    {
      "expediente": "2026/001234",
      "descripcion": "Servicio de desarrollo de aplicación web",
      "tipo": "Servicios",
      "subtipo": "Servicios informáticos",
      "estado": "Publicada",
      "importe": "50,000

El archivo `.env` es **obligatorio** para la autenticación:

```env
# Seguridad (OBLIGATORIO)
API_KEY=tu_clave_secreta_generada

# API Configuration (opcional)
API_HOST=127.0.0.1
API_PORT=8000

# Scraping Configuration (opcional)
HEADLESS=true
TIMEOUT=120
```

**Generar API Key segura:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
scraping-contrataciones/
├── main.py                 # FastAPI app principal
├── scraper_selenium.py     # Lógica de scraping con Selenium
├── config.py               # Configuración y constantes
├── logger.py               # Sistema de logging
├── requirements.txt        # Dependencias Python
├── .gitignore             # Archivos ignorados por Git
├── README.md              # Este archivo
├── datos_licitaciones/    # Datos extraídos (CSV/JSON)
└── logs/                  # Archivos de log
```

## 🔧 Configuración

### Variables de entorno (opcional)

Puedes crear un archivo `.env` para configuraciones personalizadas:

```env
# API Configuration
API_HOST=127.0.0.1
API_PORT=8000

# Scraping Configuration
HEADLESS=true
TIMEOUT=120
```

## 🐧 Despliegue en Ubuntu Server

### 1. Configurar el servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Chrome y dependencias (ver sección de requisitos)

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# IMPORTANTE: Crear archivo .env con tu API Key
nano .env
# Agregar: API_KEY=tu_clave_generada_aqui

# Ejecutar

```bash
# Desde Windows (PowerShell)
scp -r *.py *.txt *.md root@TU_IP:/root/scraping-api/
```

### 3. Configurar y ejecutar

```bash
cd /root/scraping-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### 4. Ejecutar como servicio (systemd)

Crear `/etc/systemd/system/scraping-api.service`:

```ini
[Unit]
Description=API de Licitaciones
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/scraping-api
Environment="PATH=/root/scraping-api/venv/bin"
ExecStart=/root/scraping-api/venv/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable scraping-api
sudo systemctl start scraping-api
sudo systemctl status scraping-api
```

## 📊 Logs y debugging

Los logs se guardan automáticamente en:
- `logs/scraping_YYYYMMDD.log` - Log general
- Capturas de pantalla en `datos_licitaciones/timestamp_id/`

Ver logs en tiempo real:
```bash
tail -f logs/scraping_*.log
```

## 🛡️ Seguridad

**IMPORTANTE**: Para producción, configura:

1. **Cambiar host a localhost:**
```python
# main.py
uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
```

2. **Implementar autenticación** (API Key, OAuth2)
3. **Usar reverse proxy** (Nginx con HTTPS)
4. **Configurar firewall** (UFW en Ubuntu)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto para fines educativos.

## ⚠️ Disclaimer

Este proyecto realiza web scraping del portal público contrataciondelestado.es. Asegúrate de cumplir con los términos de uso del sitio web y no realizar peticiones excesivas que puedan afectar su disponibilidad.

## 📞 Soporte

Para reportar problemas o sugerencias, abre un issue en GitHub.

---

**Desarrollado con ❤️ usando FastAPI y Selenium**
