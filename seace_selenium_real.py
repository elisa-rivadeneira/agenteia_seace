#!/usr/bin/env python3
"""
Extractor real de datos SEACE con Selenium
Obtiene los 26 procesos del segmento 43
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
from datetime import datetime

class SEACESeleniumExtractor:
    def __init__(self, headless=True):
        """Inicializa Selenium con Chrome"""
        self.options = Options()

        # Configuración del navegador
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)

        if headless:
            self.options.add_argument('--headless=new')

        # User agent real
        self.options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.set_window_size(1920, 1080)
            self.wait = WebDriverWait(self.driver, 20)
            print("✅ Navegador inicializado correctamente")
        except Exception as e:
            print(f"❌ Error inicializando navegador: {e}")
            print("\n⚠️  Asegúrate de tener Chrome y ChromeDriver instalados:")
            print("    sudo apt-get install chromium-browser chromium-chromedriver")
            raise

    def extraer_segmento_43(self):
        """Extrae los procesos del segmento 43"""
        url = "https://prod4.seace.gob.pe/openegocio/#/lista/43"

        print(f"\n🔍 Accediendo a: {url}")
        print("⏳ Esperando carga de la aplicación Angular...")

        try:
            # Navegar a la URL
            self.driver.get(url)

            # Esperar un poco más para que Angular cargue completamente
            time.sleep(8)

            # Intentar diferentes selectores para encontrar los datos
            procesos = self._extraer_por_tabla()

            if not procesos:
                procesos = self._extraer_por_cards()

            if not procesos:
                procesos = self._extraer_por_divs()

            if not procesos:
                # Capturar screenshot para debug
                self.driver.save_screenshot("seace_debug.png")
                print("📸 Screenshot guardado como 'seace_debug.png' para debug")

                # Intentar obtener cualquier texto de la página
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                if "43" in body_text or "telecomunicaciones" in body_text.lower():
                    print("✓ La página contiene datos del segmento 43")
                    print(f"  Texto encontrado: {body_text[:500]}...")
                else:
                    print("✗ No se encontraron datos del segmento 43")

            return procesos

        except TimeoutException:
            print("⏱️ Timeout esperando la carga de elementos")
            return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def _extraer_por_tabla(self):
        """Intenta extraer datos de una tabla HTML"""
        print("  🔍 Buscando tabla de datos...")

        try:
            # Buscar tabla con diferentes selectores
            selectores_tabla = [
                "table",
                "mat-table",
                "[role='table']",
                ".table",
                "#tablaProcesos",
                "table.mat-table"
            ]

            for selector in selectores_tabla:
                try:
                    tabla = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if tabla:
                        print(f"    ✓ Tabla encontrada con selector: {selector}")
                        return self._parsear_tabla(tabla)
                except:
                    continue

        except Exception as e:
            print(f"    ✗ No se encontró tabla: {e}")

        return []

    def _extraer_por_cards(self):
        """Intenta extraer datos de cards/tarjetas"""
        print("  🔍 Buscando cards de datos...")

        try:
            # Buscar cards con diferentes selectores
            selectores_cards = [
                "mat-card",
                ".card",
                ".proceso-card",
                "[class*='card']",
                "div.card-body"
            ]

            for selector in selectores_cards:
                cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if cards:
                    print(f"    ✓ {len(cards)} cards encontradas con selector: {selector}")
                    return self._parsear_cards(cards)

        except Exception:
            pass

        return []

    def _extraer_por_divs(self):
        """Intenta extraer datos de divs con patrones específicos"""
        print("  🔍 Buscando divs con datos...")

        procesos = []

        try:
            # Buscar elementos que contengan información típica de procesos
            elementos = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'LP-') or contains(text(), 'CP-') or contains(text(), 'AS-') or contains(text(), 'AMC-')]")

            if elementos:
                print(f"    ✓ {len(elementos)} elementos con nomenclatura encontrados")

                for elem in elementos[:10]:  # Primeros 10
                    try:
                        # Obtener el elemento padre para contexto
                        padre = elem.find_element(By.XPATH, "..")
                        texto = padre.text

                        if len(texto) > 20:  # Filtrar textos muy cortos
                            proceso = self._parsear_texto_proceso(texto)
                            if proceso:
                                procesos.append(proceso)
                    except:
                        continue

        except Exception as e:
            print(f"    ✗ Error buscando divs: {e}")

        return procesos

    def _parsear_tabla(self, tabla):
        """Parsea una tabla HTML para extraer procesos"""
        procesos = []

        try:
            # Buscar filas
            filas = tabla.find_elements(By.CSS_SELECTOR, "tr, mat-row, [role='row']")
            print(f"      Filas encontradas: {len(filas)}")

            for i, fila in enumerate(filas[1:26], 1):  # Saltar header, máx 26 filas
                try:
                    celdas = fila.find_elements(By.CSS_SELECTOR, "td, mat-cell, [role='cell']")

                    if len(celdas) >= 3:
                        proceso = {
                            "numero": i,
                            "entidad": celdas[0].text.strip() if len(celdas) > 0 else "",
                            "nomenclatura": celdas[1].text.strip() if len(celdas) > 1 else "",
                            "objeto": celdas[2].text.strip() if len(celdas) > 2 else "",
                            "valor": celdas[3].text.strip() if len(celdas) > 3 else "",
                            "moneda": celdas[4].text.strip() if len(celdas) > 4 else "",
                            "fecha": celdas[5].text.strip() if len(celdas) > 5 else "",
                            "segmento": "43"
                        }

                        # Filtrar procesos vacíos
                        if proceso["nomenclatura"] or proceso["objeto"]:
                            procesos.append(proceso)

                except Exception:
                    continue

        except Exception as e:
            print(f"      Error parseando tabla: {e}")

        return procesos

    def _parsear_cards(self, cards):
        """Parsea cards/tarjetas para extraer procesos"""
        procesos = []

        for i, card in enumerate(cards[:26], 1):  # Máx 26
            try:
                texto = card.text
                proceso = self._parsear_texto_proceso(texto)
                if proceso:
                    proceso["numero"] = i
                    procesos.append(proceso)
            except:
                continue

        return procesos

    def _parsear_texto_proceso(self, texto):
        """Parsea texto libre para extraer información del proceso"""
        lineas = texto.strip().split('\n')

        if len(lineas) < 2:
            return None

        proceso = {
            "texto_completo": texto[:500],
            "segmento": "43"
        }

        # Buscar patrones comunes
        for linea in lineas:
            linea = linea.strip()

            # Nomenclatura
            if any(x in linea for x in ['LP-', 'CP-', 'AS-', 'AMC-', 'SIE-', 'SBE-']):
                proceso["nomenclatura"] = linea

            # Valor monetario
            elif 'S/' in linea or 'PEN' in linea or '$' in linea:
                proceso["valor"] = linea

            # Fecha
            elif '2024' in linea or '2025' in linea or '/' in linea:
                proceso["fecha"] = linea

        return proceso if "nomenclatura" in proceso else None

    def guardar_resultados(self, procesos):
        """Guarda los resultados en JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"seace_segmento_43_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "fecha_extraccion": datetime.now().isoformat(),
                "segmento": "43",
                "total_procesos": len(procesos),
                "procesos": procesos
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Resultados guardados en: {filename}")
        return filename

    def cerrar(self):
        """Cierra el navegador"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("🔒 Navegador cerrado")

def main():
    print("="*70)
    print(" EXTRACTOR SEACE - SEGMENTO 43 (Telecomunicaciones y TI)")
    print("="*70)

    extractor = None

    try:
        # Inicializar extractor (headless=False para ver el navegador)
        extractor = SEACESeleniumExtractor(headless=False)

        # Extraer datos del segmento 43
        procesos = extractor.extraer_segmento_43()

        if procesos:
            print(f"\n✅ ÉXITO: {len(procesos)} procesos encontrados")
            print("\n📋 PRIMEROS 5 PROCESOS:")
            print("-"*70)

            for i, proceso in enumerate(procesos[:5], 1):
                print(f"\n{i}. Proceso #{proceso.get('numero', i)}")
                for key, value in proceso.items():
                    if value and key != "numero":
                        print(f"   {key}: {str(value)[:100]}")

            # Guardar todos los resultados
            extractor.guardar_resultados(procesos)

        else:
            print("\n⚠️ No se pudieron extraer procesos")
            print("\nPosibles causas:")
            print("  1. La página requiere autenticación")
            print("  2. La estructura HTML cambió")
            print("  3. El sitio detectó el bot")
            print("  4. Problemas de conectividad")

            print("\n💡 Recomendaciones:")
            print("  - Verifica el screenshot 'seace_debug.png'")
            print("  - Prueba con headless=False para ver qué sucede")
            print("  - Considera usar una sesión autenticada")

    except Exception as e:
        print(f"\n❌ Error fatal: {e}")

    finally:
        if extractor:
            extractor.cerrar()
        print("\n" + "="*70)

if __name__ == "__main__":
    main()