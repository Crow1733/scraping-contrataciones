"""
Script de prueba para la API de licitaciones
Prueba los endpoints principales de la API
"""

import requests
import time

# URL base de la API
BASE_URL = "http://localhost:8000"

def test_root():
    """Prueba el endpoint raíz"""
    print("\n" + "="*80)
    print("TEST 1: Endpoint raíz (/)")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Respuesta recibida:")
            print(f"  - Mensaje: {data.get('mensaje')}")
            print(f"  - Versión: {data.get('version')}")
            print(f"  - Endpoints: {data.get('endpoints')}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error al conectar: {e}")
        return False


def test_health():
    """Prueba el endpoint de health"""
    print("\n" + "="*80)
    print("TEST 2: Endpoint health (/health)")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Respuesta recibida:")
            print(f"  - Status: {data.get('status')}")
            print(f"  - Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error al conectar: {e}")
        return False


def test_licitaciones():
    """Prueba el endpoint de licitaciones"""
    print("\n" + "="*80)
    print("TEST 3: Endpoint licitaciones (/licitaciones)")
    print("="*80)
    print("⚠ ADVERTENCIA: Este test puede tardar 30-60 segundos")
    print("Se iniciará el scraping de contrataciondelestado.es...")
    
    try:
        print("\nIniciando solicitud...")
        inicio = time.time()
        
        response = requests.get(f"{BASE_URL}/licitaciones", timeout=180)
        
        tiempo_transcurrido = time.time() - inicio
        
        print(f"Status Code: {response.status_code}")
        print(f"Tiempo: {tiempo_transcurrido:.2f} segundos")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Scraping completado exitosamente:")
            print(f"  - Success: {data.get('success')}")
            print(f"  - Total licitaciones: {data.get('total_licitaciones')}")
            print(f"  - Total páginas: {data.get('total_paginas')}")
            print(f"  - Carpeta salida: {data.get('carpeta_salida')}")
            print(f"  - Timestamp: {data.get('timestamp')}")
            
            # Mostrar primeras 3 licitaciones
            licitaciones = data.get('licitaciones', [])
            if licitaciones:
                print(f"\n  Primeras {min(3, len(licitaciones))} licitaciones:")
                for i, lic in enumerate(licitaciones[:3], 1):
                    print(f"\n  Licitación {i}:")
                    print(f"    - Expediente: {lic.get('expediente')}")
                    print(f"    - Descripción: {lic.get('descripcion', '')[:70]}...")
                    print(f"    - Estado: {lic.get('estado')}")
                    print(f"    - Importe: {lic.get('importe')}")
                    print(f"    - Fecha: {lic.get('fecha')}")
            
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.Timeout:
        print("✗ Timeout: La solicitud tardó demasiado")
        return False
    except Exception as e:
        print(f"✗ Error al conectar: {e}")
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*80)
    print("PRUEBAS DE LA API DE LICITACIONES")
    print("="*80)
    print(f"URL Base: {BASE_URL}")
    print("\nAsegúrate de que el servidor esté ejecutándose:")
    print("  python main.py")
    print("\nPresiona Enter para continuar o Ctrl+C para cancelar...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nPruebas canceladas.")
        return
    
    # Ejecutar tests
    resultados = []
    
    resultados.append(("Endpoint raíz", test_root()))
    time.sleep(1)
    
    resultados.append(("Endpoint health", test_health()))
    time.sleep(1)
    
    print("\n¿Deseas ejecutar el test de scraping? (tarda 30-60 segundos)")
    print("Escribe 'si' para continuar o Enter para omitir:")
    respuesta = input().strip().lower()
    
    if respuesta in ['si', 'sí', 's', 'yes', 'y']:
        resultados.append(("Endpoint licitaciones", test_licitaciones()))
    else:
        print("\nTest de licitaciones omitido.")
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)
    
    for nombre, resultado in resultados:
        estado = "✓ PASÓ" if resultado else "✗ FALLÓ"
        print(f"{estado}: {nombre}")
    
    total = len(resultados)
    exitosos = sum(1 for _, r in resultados if r)
    
    print(f"\nTotal: {exitosos}/{total} pruebas exitosas")
    
    if exitosos == total:
        print("\n✓ ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("\n⚠ Algunas pruebas fallaron. Revisa los logs.")


if __name__ == "__main__":
    main()
