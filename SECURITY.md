# 🔐 Guía de Seguridad - API de Licitaciones

## Autenticación con API Key

Esta API utiliza autenticación mediante **API Key** en los headers de las peticiones.

### Configuración

1. **Copia el archivo de ejemplo:**
```bash
cp .env.example .env
```

2. **Genera tu API Key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. **Edita `.env` y reemplaza el API_KEY:**
```env
API_KEY=tu_api_key_generada_aqui
```

⚠️ **IMPORTANTE**: El archivo `.env` está en `.gitignore` y **NUNCA** debe subirse a GitHub.

---

## Uso de la API

### Sin autenticación (endpoints públicos):
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Con autenticación (endpoints protegidos):
```bash
curl -H "X-API-Key: w78JOFqGDFzDj3nYP0TIj11q3qrDDwxmdgrhz9tmpKk" \
     "http://localhost:8000/licitaciones?cpv_codes=48000000"
```

### Desde Python:
```python
import requests

headers = {
    "X-API-Key": "w78JOFqGDFzDj3nYP0TIj11q3qrDDwxmdgrhz9tmpKk"
}

response = requests.get(
    "http://localhost:8000/licitaciones",
    headers=headers,
    params={"cpv_codes": "48000000"}
)

print(response.json())
```

### Desde JavaScript:
```javascript
fetch('http://localhost:8000/licitaciones?cpv_codes=48000000', {
  headers: {
    'X-API-Key': 'w78JOFqGDFzDj3nYP0TIj11q3qrDDwxmdgrhz9tmpKk'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Respuestas de error

### Sin API Key:
```json
{
  "detail": "API Key inválida. Incluye el header 'X-API-Key' con tu token de acceso."
}
```
Status: `403 Forbidden`

### API Key incorrecta:
```json
{
  "detail": "API Key inválida. Incluye el header 'X-API-Key' con tu token de acceso."
}
```
Status: `403 Forbidden`

---

## Despliegue en Producción

### 1. Cambiar host a localhost:
En [main.py](main.py#L195):
```python
uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
```

### 2. Generar nueva API Key en el servidor:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))" > api_key.txt
```

### 3. Configurar .env en el servidor:
```bash
nano .env
# Pegar el API Key generado
```

### 4. Usar Nginx como reverse proxy con HTTPS:
```nginx
server {
    listen 443 ssl;
    server_name tu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## Mejoras de seguridad adicionales (opcional)

### Rate Limiting:
```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/licitaciones")
@limiter.limit("10/minute")
async def obtener_licitaciones(...):
    ...
```

### Whitelist de IPs:
Agrega en `.env`:
```env
ALLOWED_IPS=127.0.0.1,192.168.1.100,tu-ip-publica
```

---

## Rotación de API Keys

Para cambiar tu API Key:

1. Genera nueva: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Actualiza `.env` en el servidor
3. Reinicia la API: `sudo systemctl restart scraping-api`
4. Actualiza clientes con la nueva key

---

**Mantén tu API Key segura y nunca la compartas públicamente.**
