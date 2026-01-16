"""
Script alternativo para usar ChromeDriver desde caché local
sin necesidad de conexión a internet
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
from pathlib import Path
import glob


def find_chromedriver_in_cache():
    """Busca ChromeDriver en el caché de webdriver-manager"""
    cache_base = Path.home() / ".wdm" / "drivers" / "chromedriver"
    
    if not cache_base.exists():
        return None
    
    # Buscar chromedriver.exe en todas las subcarpetas
    pattern = str(cache_base / "**" / "chromedriver.exe")
    drivers = glob.glob(pattern, recursive=True)
    
    if drivers:
        # Retornar el más reciente
        return max(drivers, key=os.path.getmtime)
    
    return None


def setup_chrome_offline():
    """Configura Chrome usando ChromeDriver del caché"""
    print("Buscando ChromeDriver en caché local...")
    
    driver_path = find_chromedriver_in_cache()
    
    if not driver_path:
        print("✗ No se encontró ChromeDriver en caché")
        print(f"✗ Ruta buscada: {Path.home() / '.wdm' / 'drivers' / 'chromedriver'}")
        return None
    
    print(f"✓ ChromeDriver encontrado: {driver_path}")
    
    # Configurar opciones
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Crear servicio con la ruta del caché
    service = Service(executable_path=driver_path)
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✓ Chrome iniciado correctamente desde caché")
        return driver
    except Exception as e:
        print(f"✗ Error al iniciar Chrome: {e}")
        return None


if __name__ == "__main__":
    print("="*80)
    print("PRUEBA DE CHROMEDRIVER DESDE CACHÉ")
    print("="*80)
    
    driver = setup_chrome_offline()
    
    if driver:
        print("\n✓ Prueba exitosa!")
        print("Navegando a google.com...")
        driver.get("https://www.google.com")
        print(f"Título: {driver.title}")
        driver.quit()
        print("✓ Driver cerrado correctamente")
    else:
        print("\n✗ No se pudo iniciar el driver")
        print("\nSOLUCIÓN:")
        print("Ejecuta el scraper con conexión a internet una vez para descargar el driver")
    
    print("="*80)
