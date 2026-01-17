"""
API FastAPI para scraping de licitaciones
Endpoint principal para consultar licitaciones del día
"""

from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, List, Optional
import traceback
from scraper_selenium import ejecutar_scraping
from logger import setup_logger
from config import API_KEY

# Configurar logger
logger = setup_logger(__name__)

# Crear instancia de FastAPI
app = FastAPI(
    title="API de Licitaciones",
    description="API para obtener licitaciones de contrataciondelestado.es",
    version="1.0.0"
)


# Middleware de autenticación
async def verify_api_key(x_api_key: str = Header(..., description="API Key de autenticación")):
    """Verifica que el API Key sea válido"""
    if x_api_key != API_KEY:
        logger.warning(f"Intento de acceso con API Key inválida")
        raise HTTPException(
            status_code=403,
            detail="API Key inválida. Incluye el header 'X-API-Key' con tu token de acceso."
        )
    return x_api_key


@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "mensaje": "API de Licitaciones - contrataciondelestado.es",
        "version": "1.0.0",
        "endpoints": {
            "/licitaciones": "Obtener licitaciones (parámetros opcionales: cpv_codes, fecha_desde, fecha_hasta)",
            "/health": "Estado de la API"
        },
        "parametros": {
            "cpv_codes": {
                "descripcion": "Códigos CPV separados por comas (opcional)",
                "ejemplo": "48000000,72000000",
                "comportamiento": "Si no se especifica, no filtra por CPV. Si se especifica, filtra solo por los códigos dados."
            },
            "fecha_desde": {
                "descripcion": "Fecha de inicio del rango de búsqueda en formato DD-MM-YYYY (opcional)",
                "ejemplo": "01-01-2026",
                "comportamiento": "Si no se especifica, usa la fecha de ayer. Debe estar en formato DD-MM-YYYY."
            },
            "fecha_hasta": {
                "descripcion": "Fecha de fin del rango de búsqueda en formato DD-MM-YYYY (opcional)",
                "ejemplo": "31-01-2026",
                "comportamiento": "Si no se especifica, usa la fecha de ayer. Debe estar en formato DD-MM-YYYY."
            }
        }
    }


@app.get("/health")
async def health():
    """Endpoint para verificar el estado de la API"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/licitaciones", dependencies=[Depends(verify_api_key)])
async def obtener_licitaciones(
    cpv_codes: Optional[str] = Query(
        default=None,
        description="Códigos CPV separados por comas (ej: 48000000,72000000). Si no se especifica, no filtra por CPV.",
        examples=["48000000,72000000"]
    ),
    fecha_desde: Optional[str] = Query(
        default=None,
        description="Fecha desde en formato DD-MM-YYYY (ej: 01-01-2026). Si no se especifica, usa la fecha de hoy.",
        examples=["01-01-2026"]
    ),
    fecha_hasta: Optional[str] = Query(
        default=None,
        description="Fecha hasta en formato DD-MM-YYYY (ej: 31-01-2026). Si no se especifica, usa la fecha de hoy.",
        examples=["31-01-2026"]
    )
):
    """
    Endpoint principal para obtener licitaciones
    
    Realiza scraping de licitaciones publicadas en contrataciondelestado.es
    Filtra por:
    - Estado: Publicada
    - CPV: Códigos CPV personalizables (opcional - si no se especifica, no filtra por CPV)
    - Fecha: Rango de fechas personalizable (opcional - si no se especifica, usa ayer)
    
    Args:
        cpv_codes: Códigos CPV separados por comas (ej: 48000000,72000000). 
                   Si no se proporciona, NO filtra por CPV y devuelve todas las licitaciones.
        fecha_desde: Fecha desde en formato DD-MM-YYYY (ej: 01-01-2026).
                     Si no se proporciona, usa la fecha de ayer.
        fecha_hasta: Fecha hasta en formato DD-MM-YYYY (ej: 31-01-2026).
                     Si no se proporciona, usa la fecha de ayer.
    
    Returns:
        JSONResponse con las licitaciones encontradas
    """
    try:
        logger.info("=" * 80)
        logger.info("SOLICITUD DE LICITACIONES VIA API")
        logger.info("=" * 80)
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        
        # Procesar códigos CPV
        if cpv_codes:
            cpv_list = [code.strip() for code in cpv_codes.split(",") if code.strip()]
            logger.info(f"Códigos CPV solicitados: {cpv_list}")
        else:
            cpv_list = None
            logger.info("Sin filtro de códigos CPV")
        
        # Procesar fechas
        if fecha_desde:
            logger.info(f"Fecha desde: {fecha_desde}")
        else:
            logger.info("Fecha desde: ayer")
        
        if fecha_hasta:
            logger.info(f"Fecha hasta: {fecha_hasta}")
        else:
            logger.info("Fecha hasta: ayer")
        
        # Ejecutar el scraping con los parámetros especificados
        resultado = ejecutar_scraping(
            cpv_codes=cpv_list,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        
        if resultado["success"]:
            logger.info(f"✓ Scraping exitoso: {resultado['total_licitaciones']} licitaciones encontradas")
            
            response_content = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "total_licitaciones": resultado["total_licitaciones"],
                "carpeta_salida": resultado.get("output_folder", ""),
                "fecha_desde": resultado.get("fecha_desde"),
                "fecha_hasta": resultado.get("fecha_hasta"),
                "licitaciones": resultado["licitaciones"]
            }
            
            # Solo incluir códigos CPV si se especificaron
            if cpv_list:
                response_content["codigos_cpv"] = cpv_list
            else:
                response_content["filtro_cpv"] = "ninguno"
            
            return JSONResponse(
                status_code=200,
                content=response_content
            )
        else:
            logger.error(f"✗ Error en scraping: {resultado.get('error', 'Error desconocido')}")
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": resultado.get("error", "Error al ejecutar el scraping"),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        logger.error(f"Error en endpoint /licitaciones: {error_msg}")
        logger.error(f"Traceback: {error_trace}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Iniciando servidor FastAPI...")
    logger.info("Servidor disponible en: http://localhost:8000")
    logger.info("Documentación en: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Recarga automática en desarrollo
    )
