"""
Script para verificar la instalación de Chrome y ChromeDriver
"""

import subprocess
import sys
import os
from pathlib import Path


def check_chrome():
    """Verifica si Chrome está instalado"""
    print("\n" + "="*80)
    print("VERIFICANDO GOOGLE CHROME")
    print("="*80)
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✓ Chrome encontrado: {path}")
            try:
                # Intentar obtener la versión
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout:
                    print(f"  Versión: {result.stdout.strip()}")
            except:
                pass
            return True
    
    print("✗ Chrome NO encontrado")
    print("\nDescarga Chrome desde: https://www.google.com/chrome/")
    return False


def check_chromedriver_in_path():
    """Verifica si chromedriver está en el PATH"""
    print("\n" + "="*80)
    print("VERIFICANDO CHROMEDRIVER EN PATH")
    print("="*80)
    
    try:
        result = subprocess.run(
            ["chromedriver", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ ChromeDriver encontrado en PATH")
            print(f"  Versión: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("✗ ChromeDriver NO está en el PATH")
    except Exception as e:
        print(f"✗ Error al verificar ChromeDriver: {e}")
    
    return False


def check_webdriver_manager_cache():
    """Verifica el caché de webdriver-manager"""
    print("\n" + "="*80)
    print("VERIFICANDO CACHÉ DE WEBDRIVER-MANAGER")
    print("="*80)
    
    cache_paths = [
        Path.home() / ".wdm" / "drivers" / "chromedriver",
        Path(os.path.expandvars(r"%USERPROFILE%\.wdm\drivers\chromedriver")),
    ]
    
    found = False
    for cache_path in cache_paths:
        if cache_path.exists():
            print(f"✓ Caché encontrado: {cache_path}")
            # Listar versiones en caché
            for version_dir in cache_path.iterdir():
                if version_dir.is_dir():
                    print(f"  - Versión: {version_dir.name}")
                    found = True
    
    if not found:
        print("✗ No se encontró caché de webdriver-manager")
    
    return found


def test_selenium():
    """Intenta inicializar Selenium"""
    print("\n" + "="*80)
    print("PROBANDO SELENIUM")
    print("="*80)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("Intentando iniciar Chrome con Selenium...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Intentar sin service primero
        try:
            driver = webdriver.Chrome(options=chrome_options)
            print("✓ Selenium funciona con ChromeDriver del sistema")
            driver.quit()
            return True
        except Exception as e:
            print(f"✗ No se pudo usar ChromeDriver del sistema: {str(e)[:100]}")
            
            # Intentar con webdriver-manager
            print("\nIntentando con webdriver-manager...")
            try:
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✓ Selenium funciona con webdriver-manager")
                driver.quit()
                return True
            except Exception as e2:
                print(f"✗ Error con webdriver-manager: {str(e2)[:100]}")
                return False
                
    except ImportError:
        print("✗ Selenium no está instalado")
        print("  Instala con: pip install selenium")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)[:200]}")
        return False


def show_solutions():
    """Muestra soluciones para problemas comunes"""
    print("\n" + "="*80)
    print("SOLUCIONES")
    print("="*80)
    print("""
Si ChromeDriver no funciona, tienes 3 opciones:

OPCIÓN 1: Instalar ChromeDriver manualmente
  1. Descarga ChromeDriver de: https://chromedriver.chromium.org/downloads
  2. Descomprime el archivo chromedriver.exe
  3. Muévelo a una carpeta en tu PATH o agrega su ubicación al PATH
  
OPCIÓN 2: Usar webdriver-manager con conexión a internet
  - El script automáticamente descargará ChromeDriver si hay conexión

OPCIÓN 3: Copiar ChromeDriver al proyecto
  1. Descarga ChromeDriver
  2. Cópialo a la carpeta del proyecto
  3. Modifica scraper_selenium.py para usar la ruta local

NOTA: La versión de ChromeDriver debe coincidir con tu versión de Chrome
""")


def main():
    print("="*80)
    print("DIAGNÓSTICO DE CHROMEDRIVER")
    print("="*80)
    
    results = {
        "chrome": check_chrome(),
        "chromedriver": check_chromedriver_in_path(),
        "cache": check_webdriver_manager_cache(),
        "selenium": test_selenium()
    }
    
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    
    for key, value in results.items():
        symbol = "✓" if value else "✗"
        print(f"{symbol} {key.upper()}")
    
    if all(results.values()):
        print("\n✓ ¡Todo está configurado correctamente!")
    else:
        show_solutions()
    
    print("="*80)


if __name__ == "__main__":
    main()
