"""
Script de prueba para la API de licitaciones con códigos CPV personalizados
Prueba diferentes combinaciones de códigos CPV
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
            print(f"  - Parámetros: {data.get('parametros')}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error al conectar: {e}")
        return False


def test_licitaciones_default():
    """Prueba el endpoint de licitaciones con CPV por defecto"""
    print("\n" + "="*80)
    print("TEST 2: Licitaciones con CPV por defecto (48000000,72000000)")
    print("="*80)
    print("⚠ ADVERTENCIA: Este test puede tardar 30-60 segundos")
    
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
            print(f"  - Códigos CPV: {data.get('codigos_cpv')}")
            print(f"  - Total licitaciones: {data.get('total_licitaciones')}")
            print(f"  - Total páginas: {data.get('total_paginas')}")
            print(f"  - Carpeta salida: {data.get('carpeta_salida')}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_licitaciones_software():
    """Prueba el endpoint solo con CPV de software"""
    print("\n" + "="*80)
    print("TEST 3: Licitaciones solo Software (CPV 48000000)")
    print("="*80)
    print("⚠ ADVERTENCIA: Este test puede tardar 30-60 segundos")
    
    try:
        print("\nIniciando solicitud...")
        inicio = time.time()
        
        response = requests.get(
            f"{BASE_URL}/licitaciones",
            params={"cpv_codes": "48000000"},
            timeout=180
        )
        
        tiempo_transcurrido = time.time() - inicio
        
        print(f"Status Code: {response.status_code}")
        print(f"Tiempo: {tiempo_transcurrido:.2f} segundos")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Scraping completado exitosamente:")
            print(f"  - Success: {data.get('success')}")
            print(f"  - Códigos CPV: {data.get('codigos_cpv')}")
            print(f"  - Total licitaciones: {data.get('total_licitaciones')}")
            print(f"  - Total páginas: {data.get('total_paginas')}")
            
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
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_licitaciones_custom():
    """Prueba el endpoint con múltiples CPV personalizados"""
    print("\n" + "="*80)
    print("TEST 4: Licitaciones con CPV personalizados (48000000,72000000,30200000)")
    print("="*80)
    print("CPV 30200000 = Equipo y material informático")
    print("⚠ ADVERTENCIA: Este test puede tardar 30-60 segundos")
    
    try:
        print("\nIniciando solicitud...")
        inicio = time.time()
        
        response = requests.get(
            f"{BASE_URL}/licitaciones",
            params={"cpv_codes": "48000000,72000000,30200000"},
            timeout=180
        )
        
        tiempo_transcurrido = time.time() - inicio
        
        print(f"Status Code: {response.status_code}")
        print(f"Tiempo: {tiempo_transcurrido:.2f} segundos")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Scraping completado exitosamente:")
            print(f"  - Success: {data.get('success')}")
            print(f"  - Códigos CPV: {data.get('codigos_cpv')}")
            print(f"  - Total licitaciones: {data.get('total_licitaciones')}")
            print(f"  - Total páginas: {data.get('total_paginas')}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*80)
    print("API DE LICITACIONES - SUITE DE PRUEBAS CPV")
    print("="*80)
    print(f"URL Base: {BASE_URL}")
    print("\nAsegúrate de que el servidor esté corriendo:")
    print("  python main.py")
    print("\nPresiona Enter para continuar...")
    input()
    
    resultados = []
    
    # Test 1: Endpoint raíz
    resultados.append(("Endpoint raíz", test_root()))
    
    # Test 2: CPV por defecto
    print("\n¿Ejecutar test con CPV por defecto? (tardará ~60 seg) [s/N]: ", end="")
    if input().lower() == 's':
        resultados.append(("CPV por defecto", test_licitaciones_default()))
    
    # Test 3: Solo software
    print("\n¿Ejecutar test solo con software? (tardará ~60 seg) [s/N]: ", end="")
    if input().lower() == 's':
        resultados.append(("Solo Software", test_licitaciones_software()))
    
    # Test 4: CPV personalizados
    print("\n¿Ejecutar test con CPV personalizados? (tardará ~60 seg) [s/N]: ", end="")
    if input().lower() == 's':
        resultados.append(("CPV personalizados", test_licitaciones_custom()))
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE RESULTADOS")
    print("="*80)
    
    for nombre, resultado in resultados:
        simbolo = "✓" if resultado else "✗"
        print(f"{simbolo} {nombre}")
    
    exitosos = sum(1 for _, r in resultados if r)
    print(f"\nTests exitosos: {exitosos}/{len(resultados)}")
    print("="*80)


if __name__ == "__main__":
    main()
