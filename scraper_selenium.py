"""
Scraper usando Selenium para contrataciondelestado.es
Necesario porque la página usa JavaScript y formularios dinámicos
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import pandas as pd
import json
import os
import uuid
from logger import setup_logger
from config import get_output_file

logger = setup_logger(__name__)

class LicitacionesScraperSelenium:
    """Scraper usando Selenium para manejar JavaScript"""
    
    def __init__(self, headless=True, cpv_codes=None, fecha_desde=None, fecha_hasta=None):
        self.headless = headless
        self.driver = None
        self.licitaciones = []
        self.cpv_codes = cpv_codes  # Lista de códigos CPV a buscar (opcional)
        self.fecha_desde = fecha_desde  # Fecha desde en formato DD-MM-YYYY (opcional)
        self.fecha_hasta = fecha_hasta  # Fecha hasta en formato DD-MM-YYYY (opcional)
        
        # Crear carpeta única para esta ejecución
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        self.output_folder = f"datos_licitaciones/{timestamp}_{unique_id}"
        os.makedirs(self.output_folder, exist_ok=True)
        logger.info(f"Carpeta de salida: {self.output_folder}")
        
    def _setup_driver(self):
        """Configura el driver de Chrome con webdriver-manager"""
        try:
            logger.info("Configurando navegador Chrome...")
            
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Usar webdriver-manager para instalar automáticamente el driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(120)  # Aumentar timeout a 120 segundos
            logger.info("✓ Navegador configurado correctamente")
            
        except Exception as e:
            logger.error(f"Error configurando navegador: {str(e)}")
            logger.error("Instala Chrome si no lo tienes: https://www.google.com/chrome/")
            raise
    
    def scrape_licitaciones(self):
        """Realiza el scraping usando Selenium"""
        try:
            if not self.driver:
                self._setup_driver()
            
            logger.info("Accediendo al formulario de búsqueda...")
            url = "https://contrataciondelestado.es/wps/portal/plataforma/buscadores/busqueda"
            
            try:
                self.driver.get(url)
            except Exception as e:
                logger.warning(f"Timeout inicial, reintentando... ({e})")
                time.sleep(5)
                self.driver.get(url)
            
            # Esperar a que la página cargue
            logger.info("Esperando carga de la página...")
            time.sleep(8)
            
            # Tomar captura para debugging
            screenshot_path = os.path.join(self.output_folder, 'screenshot_formulario.png')
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"✓ Captura guardada: {screenshot_path}")
            
            # Buscar iframes (el formulario puede estar dentro de uno)
            logger.info("\nBuscando iframes...")
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            logger.info(f"Iframes encontrados: {len(iframes)}")
            
            for i, iframe in enumerate(iframes):
                src = iframe.get_attribute("src")
                name = iframe.get_attribute("name")
                logger.info(f"  {i+1}. name={name}, src={src[:80] if src else 'N/A'}")
            
            # Buscar el botón/enlace de "Bids" (Licitaciones)
            logger.info("\nBuscando enlace de 'Bids' (Licitaciones)...")
            try:
                # ID del enlace de licitaciones
                link_id = "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:linkFormularioBusqueda"
                enlace_licitaciones = self.driver.find_element(By.ID, link_id)
                
                logger.info(f"✓ Enlace encontrado: {enlace_licitaciones.text}")
                logger.info("Haciendo click en 'Bids'...")
                
                enlace_licitaciones.click()
                time.sleep(5)  # Esperar a que cargue el formulario
                
                logger.info("✓ Click realizado, formulario de búsqueda cargado")
                
                # Tomar captura del formulario
                screenshot_path = os.path.join(self.output_folder, 'screenshot_formulario_busqueda.png')
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"✓ Captura guardada: {screenshot_path}")
                
                # Guardar HTML del formulario de búsqueda
                html_path = os.path.join(self.output_folder, 'formulario_busqueda_selenium.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                logger.info(f"✓ HTML del formulario guardado: {html_path}")
                
                # Buscar campos del formulario de búsqueda
                logger.info("\n" + "="*80)
                logger.info("ANALIZANDO FORMULARIO DE BÚSQUEDA")
                logger.info("="*80)
                
                # Buscar inputs visibles
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                logger.info(f"\nInputs encontrados: {len(inputs)}")
                
                campos_visibles = []
                for inp in inputs:
                    try:
                        if inp.is_displayed():  # Solo campos visibles
                            input_type = inp.get_attribute("type")
                            name = inp.get_attribute("name")
                            placeholder = inp.get_attribute("placeholder")
                            id_attr = inp.get_attribute("id")
                            value = inp.get_attribute("value")
                            
                            if input_type not in ['hidden']:
                                logger.info(f"  ✓ type={input_type}, name={name}, placeholder={placeholder}")
                                campos_visibles.append({
                                    'type': input_type,
                                    'name': name,
                                    'placeholder': placeholder,
                                    'id': id_attr,
                                    'value': value
                                })
                    except:
                        pass
                
                # Buscar selects visibles
                selects = self.driver.find_elements(By.TAG_NAME, "select")
                logger.info(f"\nSelects encontrados: {len(selects)}")
                
                for sel in selects:
                    try:
                        if sel.is_displayed():
                            name = sel.get_attribute("name")
                            id_attr = sel.get_attribute("id")
                            logger.info(f"  ✓ name={name}, id={id_attr}")
                            
                            # Ver opciones
                            options = sel.find_elements(By.TAG_NAME, "option")
                            if len(options) > 0 and len(options) <= 10:
                                logger.info(f"    Opciones:")
                                for opt in options[:5]:
                                    logger.info(f"      - {opt.text}")
                    except:
                        pass
                
                # Buscar botones visibles
                botones = self.driver.find_elements(By.TAG_NAME, "button")
                logger.info(f"\nBotones encontrados: {len(botones)}")
                
                for btn in botones:
                    try:
                        if btn.is_displayed():
                            texto = btn.text.strip()
                            btn_type = btn.get_attribute("type")
                            if texto:
                                logger.info(f"  ✓ '{texto}' (type={btn_type})")
                    except:
                        pass
                
                # Guardar campos encontrados
                if campos_visibles:
                    json_path = os.path.join(self.output_folder, 'campos_formulario_busqueda.json')
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(campos_visibles, f, indent=2, ensure_ascii=False)
                    logger.info(f"\n✓ Campos del formulario guardados: {json_path}")
                
                # ===================================================================
                # PASO 3: LLENAR EL FORMULARIO
                # ===================================================================
                logger.info("\n" + "="*80)
                logger.info("LLENANDO FORMULARIO DE BÚSQUEDA")
                logger.info("="*80)
                
                # Obtener fechas (usar las proporcionadas o las de ayer por defecto)
                from datetime import datetime, timedelta
                from selenium.webdriver.support.ui import Select
                ayer = datetime.now() - timedelta(days=1)
                
                # Si no se proporcionan fechas, usar ayer
                if self.fecha_desde:
                    fecha_desde = self.fecha_desde
                else:
                    fecha_desde = ayer.strftime("%d-%m-%Y")
                
                if self.fecha_hasta:
                    fecha_hasta = self.fecha_hasta
                else:
                    fecha_hasta = ayer.strftime("%d-%m-%Y")
                
                logger.info(f"\nBuscando licitaciones publicadas entre: {fecha_desde} y {fecha_hasta}")
                if self.cpv_codes:
                    logger.info(f"Filtros: Estado=Publicada, CPV={', '.join(self.cpv_codes)}")
                else:
                    logger.info("Filtros: Estado=Publicada (sin filtro CPV)")
                
                # PRIMERO: Agregar los códigos CPV (solo si se proporcionaron)
                if self.cpv_codes:
                    logger.info("\n--- Agregando códigos CPV ---")
                    for idx, cpv_code in enumerate(self.cpv_codes, 1):
                        try:
                            logger.info(f"\nAgregando CPV {cpv_code} ({idx}/{len(self.cpv_codes)})...")
                            campo_cpv = self.driver.find_element(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:cpvMultiple:codigoCpv")
                            campo_cpv.clear()
                            campo_cpv.send_keys(cpv_code)
                            
                            # Click en botón "Add"
                            boton_add_cpv = self.driver.find_element(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:cpvMultiplebuttonAnyadirMultiple")
                            boton_add_cpv.click()
                            logger.info(f"✓ Click en 'Add' para CPV {cpv_code}")
                            
                            # Esperar a que recargue la página
                            time.sleep(3)
                            logger.info(f"✓ CPV {cpv_code} agregado")
                        except Exception as e:
                            logger.error(f"Error al agregar CPV {cpv_code}: {e}")
                    
                    logger.info(f"✓ Todos los CPV agregados correctamente ({len(self.cpv_codes)} códigos)")
                else:
                    logger.info("\n⚠ No se especificaron códigos CPV - buscando todas las licitaciones")
                
                # SEGUNDO: Llenar el resto de campos del formulario
                # Llenar campo de fecha desde (fecha publicación desde)
                try:
                    campo_fecha_desde = self.driver.find_element(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:textMinFecAnuncioMAQ2")
                    campo_fecha_desde.clear()
                    campo_fecha_desde.send_keys(fecha_desde)
                    logger.info(f"✓ Fecha desde: {fecha_desde}")
                except Exception as e:
                    logger.error(f"Error al llenar fecha desde: {e}")
                
                # Llenar campo de fecha hasta (fecha publicación hasta)
                try:
                    campo_fecha_hasta = self.driver.find_element(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:textMaxFecAnuncioMAQ")
                    campo_fecha_hasta.clear()
                    campo_fecha_hasta.send_keys(fecha_hasta)
                    logger.info(f"✓ Fecha hasta: {fecha_hasta}")
                except Exception as e:
                    logger.error(f"Error al llenar fecha hasta: {e}")
                
                # Seleccionar Estado: Publicada
                try:
                    select_estado = Select(self.driver.find_element(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:estadoLici"))
                    select_estado.select_by_value("PUB")
                    logger.info("✓ Estado: Publicada")
                except Exception as e:
                    logger.error(f"Error al seleccionar estado: {e}")
                
                # Captura antes de buscar
                screenshot_path = os.path.join(self.output_folder, "screenshot_antes_busqueda.png")
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"✓ Captura guardada: {screenshot_path}")
                
                # Hacer click en el botón de búsqueda
                try:
                    boton_buscar = self.driver.find_element(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:button1")
                    logger.info("\nRealizando búsqueda...")
                    boton_buscar.click()
                    
                    # Esperar resultados
                    time.sleep(5)
                    
                    # ===================================================================
                    # PASO 4: EXTRAER RESULTADOS CON PAGINACIÓN
                    # ===================================================================
                    logger.info("\n" + "="*80)
                    logger.info("EXTRAYENDO RESULTADOS")
                    logger.info("=" * 80)
                    
                    # Lista para almacenar todas las licitaciones de todas las páginas
                    todas_licitaciones = []
                    pagina_actual = 1
                    
                    while True:
                        logger.info(f"\n--- Procesando página {pagina_actual} ---")
                        
                        # Captura de la página actual
                        screenshot_path = os.path.join(self.output_folder, f'screenshot_resultados_pagina_{pagina_actual}.png')
                        self.driver.save_screenshot(screenshot_path)
                        logger.info(f"✓ Captura guardada: {screenshot_path}")
                        
                        # Guardar HTML de la página actual
                        html_path = os.path.join(self.output_folder, f'resultados_pagina_{pagina_actual}.html')
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(self.driver.page_source)
                        logger.info(f"✓ HTML guardado: {html_path}")
                        
                        # Buscar tabla o lista de resultados
                        tablas = self.driver.find_elements(By.TAG_NAME, "table")
                        logger.info(f"Tablas encontradas: {len(tablas)}")
                        
                        # Buscar filas en todas las tablas
                        licitaciones_pagina = []
                        for idx, tabla in enumerate(tablas):
                            filas = tabla.find_elements(By.TAG_NAME, "tr")
                            
                            # Si la tabla tiene filas, intentar extraer datos
                            if len(filas) > 1:  # Más de 1 fila (encabezado + datos)
                                for fila_idx, fila in enumerate(filas[1:], 1):  # Saltar encabezado
                                    celdas = fila.find_elements(By.TAG_NAME, "td")
                                    
                                    # Verificar que tenga 6 columnas (formato esperado)
                                    if len(celdas) == 6:
                                        try:
                                            # Extraer datos estructurados
                                            expediente_celda = celdas[0].text.strip()
                                            tipo_contrato = celdas[1].text.strip()
                                            estado = celdas[2].text.strip()
                                            importe = celdas[3].text.strip()
                                            fecha = celdas[4].text.strip()
                                            organismo = celdas[5].text.strip()
                                            
                                            # Separar expediente y descripción
                                            lineas_exp = expediente_celda.split('\n', 1)
                                            expediente = lineas_exp[0] if lineas_exp else ""
                                            descripcion = lineas_exp[1] if len(lineas_exp) > 1 else ""
                                            
                                            # Buscar el enlace del expediente (el que termina en %3D%3D)
                                            try:
                                                # Buscar el enlace con target="_blank" que es el correcto
                                                enlaces = celdas[0].find_elements(By.CSS_SELECTOR, "a[target='_blank']")
                                                if enlaces:
                                                    enlace_detalle = enlaces[0].get_attribute("href")
                                                else:
                                                    # Fallback: buscar cualquier enlace con href
                                                    enlace_elem = celdas[0].find_element(By.TAG_NAME, "a")
                                                    enlace_detalle = enlace_elem.get_attribute("href") if enlace_elem.get_attribute("href") else ""
                                            except:
                                                enlace_detalle = ""
                                            
                                            # Separar tipo y subtipo
                                            lineas_tipo = tipo_contrato.split('\n', 1)
                                            tipo = lineas_tipo[0] if lineas_tipo else ""
                                            subtipo = lineas_tipo[1] if len(lineas_tipo) > 1 else ""
                                            
                                            # Solo guardar si tiene datos válidos (no es la fila de paginación)
                                            if expediente and not expediente.startswith("Página"):
                                                licitacion = {
                                                    'expediente': expediente,
                                                    'descripcion': descripcion,
                                                    'tipo': tipo,
                                                    'subtipo': subtipo,
                                                    'estado': estado,
                                                    'importe': importe,
                                                    'fecha': fecha,
                                                    'organismo': organismo,
                                                    'enlace': enlace_detalle
                                                }
                                                licitaciones_pagina.append(licitacion)
                                        except Exception as e:
                                            logger.error(f"Error al procesar fila {fila_idx} de tabla {idx+1}: {e}")
                        
                        # Agregar licitaciones de esta página al total
                        todas_licitaciones.extend(licitaciones_pagina)
                        logger.info(f"✓ Licitaciones en página {pagina_actual}: {len(licitaciones_pagina)}")
                        logger.info(f"✓ Total acumulado: {len(todas_licitaciones)}")
                        
                        # Buscar el botón "Next >>" para ir a la siguiente página
                        # El botón es un input type="submit" con id específico
                        try:
                            logger.info(f"\nBuscando botón 'Next >>' (input type=submit)...")
                            boton_next = self.driver.find_element(By.ID, "viewns_Z7_AVEQAI930OBRD02JPMTPG21004_:form1:footerSiguiente")
                            
                            if boton_next and boton_next.is_displayed() and boton_next.is_enabled():
                                logger.info(f"✓ Botón 'Next >>' encontrado y disponible")
                                logger.info(f"→ Haciendo clic para ir a página {pagina_actual + 1}...")
                                
                                # Scroll al botón
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", boton_next)
                                time.sleep(0.5)
                                
                                boton_next.click()
                                time.sleep(4)  # Esperar a que cargue la siguiente página
                                pagina_actual += 1
                            else:
                                logger.info("\n✓ Botón 'Next' no disponible. Última página alcanzada.")
                                break
                                
                        except NoSuchElementException:
                            logger.info("\n✓ Botón 'Next' no encontrado. Última página alcanzada.")
                            break
                        except Exception as e:
                            logger.warning(f"Error al buscar/hacer clic en botón 'Next': {e}")
                            logger.info("✓ Asumiendo que es la última página.")
                            break
                    
                    logger.info(f"\n✓ TOTAL de licitaciones extraídas: {len(todas_licitaciones)} (de {pagina_actual} página(s))")
                    
                    # Guardar resultados
                    if todas_licitaciones:
                        # Guardar JSON
                        json_path = os.path.join(self.output_folder, 'licitaciones_extraidas.json')
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(todas_licitaciones, f, ensure_ascii=False, indent=2)
                        logger.info(f"✓ Resultados guardados: {json_path}")
                        
                        # Guardar CSV
                        import pandas as pd
                        df = pd.DataFrame(todas_licitaciones)
                        csv_filename = os.path.join(self.output_folder, f'licitaciones_{hoy.strftime("%Y%m%d")}.csv')
                        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                        logger.info(f"✓ Resultados guardados: {csv_filename}")
                        
                        # Mostrar primeras 5 licitaciones
                        logger.info("\nPrimeras licitaciones encontradas:")
                        for i, lic in enumerate(todas_licitaciones[:5], 1):
                            logger.info(f"\n  Licitación {i}:")
                            logger.info(f"    Expediente: {lic['expediente']}")
                            logger.info(f"    Descripción: {lic['descripcion'][:80]}...")
                            logger.info(f"    Tipo: {lic['tipo']} - {lic['subtipo']}")
                            logger.info(f"    Estado: {lic['estado']}")
                            logger.info(f"    Importe: {lic['importe']}")
                            logger.info(f"    Fecha: {lic['fecha']}")
                            logger.info(f"    Organismo: {lic['organismo'][:60]}...")
                    else:
                        logger.info("⚠ No se encontraron licitaciones en las tablas")
                        
                except Exception as e:
                    logger.error(f"Error al buscar o extraer resultados: {e}")
                    import traceback
                    traceback.print_exc()
                
                return True
                
            except NoSuchElementException:
                logger.error("✗ No se encontró el enlace de 'Bids'")
                return False
            
            # Código original para análisis general (se ejecuta si no se encuentra el enlace)
            
            # Buscar el enlace de "Búsqueda guiada" o "Nueva búsqueda"
            logger.info("\nBuscando enlaces de búsqueda...")
            enlaces = self.driver.find_elements(By.TAG_NAME, "a")
            enlaces_busqueda = []
            
            for enlace in enlaces:
                texto = enlace.text.strip()
                href = enlace.get_attribute("href")
                
                if any(palabra in texto.lower() for palabra in ['búsqueda', 'busqueda', 'guiada', 'nueva']):
                    logger.info(f"  ✓ '{texto}' -> {href}")
                    enlaces_busqueda.append((texto, href, enlace))
            
            # Intentar hacer click en "Búsqueda guiada" si existe
            if enlaces_busqueda:
                logger.info(f"\nIntentando acceder a: {enlaces_busqueda[0][0]}")
                try:
                    enlaces_busqueda[0][2].click()
                    logger.info("✓ Click realizado, esperando nueva página...")
                    time.sleep(5)
                    
                    # Tomar otra captura
                    self.driver.save_screenshot('screenshot_busqueda_guiada.png')
                    logger.info("✓ Captura guardada: screenshot_busqueda_guiada.png")
                    
                except Exception as e:
                    logger.warning(f"No se pudo hacer click: {str(e)}")
            
            # Buscar campos del formulario
            logger.info("\nBuscando campos del formulario...")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            logger.info(f"Inputs encontrados: {len(inputs)}")
            
            campos_importantes = []
            for inp in inputs[:20]:  # Solo primeros 20 para no saturar
                input_type = inp.get_attribute("type")
                name = inp.get_attribute("name")
                placeholder = inp.get_attribute("placeholder")
                id_attr = inp.get_attribute("id")
                
                # Solo mostrar campos relevantes (no hidden)
                if input_type not in ['hidden', 'submit']:
                    logger.info(f"  - type={input_type}, name={name}, placeholder={placeholder}, id={id_attr}")
                    campos_importantes.append({
                        'type': input_type,
                        'name': name,
                        'placeholder': placeholder,
                        'id': id_attr
                    })
            
            # Buscar select (desplegables)
            logger.info("\nBuscando campos select (desplegables)...")
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            logger.info(f"Selects encontrados: {len(selects)}")
            
            for sel in selects[:10]:
                name = sel.get_attribute("name")
                id_attr = sel.get_attribute("id")
                logger.info(f"  - name={name}, id={id_attr}")
            
            # Buscar botones
            logger.info("\nBuscando botones...")
            botones = self.driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"Botones encontrados: {len(botones)}")
            
            for btn in botones[:15]:
                texto = btn.text.strip()
                btn_type = btn.get_attribute("type")
                if texto or btn_type == "submit":
                    logger.info(f"  - '{texto}' (type={btn_type})")
            
            # Guardar HTML completo
            with open('pagina_selenium.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info("\n✓ HTML completo guardado: pagina_selenium.html")
            
            # Guardar datos de campos encontrados
            if campos_importantes:
                with open('campos_encontrados_selenium.json', 'w', encoding='utf-8') as f:
                    json.dump(campos_importantes, f, indent=2, ensure_ascii=False)
                logger.info("✓ Campos guardados: campos_encontrados_selenium.json")
            
            logger.info("\n" + "="*80)
            logger.info("RESUMEN DEL ANÁLISIS")
            logger.info("="*80)
            logger.info(f"Iframes: {len(iframes)}")
            logger.info(f"Enlaces de búsqueda: {len(enlaces_busqueda)}")
            logger.info(f"Campos de formulario: {len(campos_importantes)}")
            logger.info(f"Botones: {len(botones)}")
            logger.info("\nArchivos generados:")
            logger.info("  - screenshot_formulario.png")
            if enlaces_busqueda:
                logger.info("  - screenshot_busqueda_guiada.png")
            logger.info("  - pagina_selenium.html")
            logger.info("  - campos_encontrados_selenium.json")
            logger.info("\nRevisa estos archivos para entender la estructura.")
            
            return True
                
        except Exception as e:
            logger.error(f"Error en scrape_licitaciones: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if self.driver:
                logger.info("\nCerrando navegador...")
                self.driver.quit()
    
    def close(self):
        """Cierra el navegador"""
        if self.driver:
            self.driver.quit()


def ejecutar_scraping(cpv_codes=None, fecha_desde=None, fecha_hasta=None):
    """
    Función wrapper para ejecutar el scraping desde la API
    
    Args:
        cpv_codes: Lista de códigos CPV a filtrar (opcional)
                   Si es None, no filtra por CPV
        fecha_desde: Fecha desde en formato DD-MM-YYYY (opcional)
                     Si es None, usa la fecha de ayer
        fecha_hasta: Fecha hasta en formato DD-MM-YYYY (opcional)
                     Si es None, usa la fecha de ayer
    
    Returns:
        dict: Diccionario con los resultados del scraping
            {
                'success': bool,
                'total_licitaciones': int,
                'licitaciones': list,
                'output_folder': str,
                'fecha_desde': str,
                'fecha_hasta': str,
                'error': str (solo si success=False)
            }
    """
    logger.info("=" * 80)
    logger.info("EJECUTANDO SCRAPING VIA API")
    logger.info("=" * 80)
    
    from datetime import timedelta
    
    try:
        scraper = LicitacionesScraperSelenium(
            headless=True, 
            cpv_codes=cpv_codes,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        
        if scraper.scrape_licitaciones():
            logger.info("✓ Scraping completado exitosamente")
            
            # Leer los resultados del archivo JSON generado
            json_path = os.path.join(scraper.output_folder, 'licitaciones_extraidas.json')
            licitaciones = []
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    licitaciones = json.load(f)
            
            ayer = datetime.now() - timedelta(days=1)
            return {
                'success': True,
                'total_licitaciones': len(licitaciones),
                'licitaciones': licitaciones,
                'output_folder': scraper.output_folder,
                'cpv_codes': cpv_codes,
                'fecha_desde': fecha_desde if fecha_desde else ayer.strftime("%d-%m-%Y"),
                'fecha_hasta': fecha_hasta if fecha_hasta else ayer.strftime("%d-%m-%Y")
            }
        else:
            logger.error("✗ Error en el scraping")
            return {
                'success': False,
                'error': 'Error durante el proceso de scraping',
                'total_licitaciones': 0,
                'licitaciones': []
            }
            
    except Exception as e:
        logger.error(f"Error al ejecutar scraping: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'total_licitaciones': 0,
            'licitaciones': []
        }


def main():
    """Ejecuta el scraper con Selenium"""
    logger.info("=" * 80)
    logger.info("SCRAPER CON SELENIUM - LICITACIONES")
    logger.info("=" * 80)
    
    try:
        # Ejemplo: sin códigos CPV
        scraper = LicitacionesScraperSelenium(headless=True)
        
        if scraper.scrape_licitaciones():
            logger.info("✓ Análisis completado")
            logger.info("\nRevisa los archivos generados para más detalles.")
        else:
            logger.error("✗ Error en análisis")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
