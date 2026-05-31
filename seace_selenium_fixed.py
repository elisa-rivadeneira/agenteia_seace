#!/usr/bin/env python3
"""
Extractor SEACE con webdriver-manager para compatibilidad automática
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from datetime import datetime

print("Instalando ChromeDriver compatible automáticamente...")

class SEACEExtractor:
    def __init__(self, headless=True):
        """Inicializa con ChromeDriver compatible automáticamente"""
        self.options = Options()
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')

        if headless:
            self.options.add_argument('--headless=new')

        # Instalar y usar ChromeDriver compatible automáticamente
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            self.wait = WebDriverWait(self.driver, 20)
            print("✅ Navegador inicializado con ChromeDriver compatible")
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

    def obtener_segmento_43(self):
        """Obtiene los datos del segmento 43"""
        url = "https://prod4.seace.gob.pe/openegocio/#/lista/43"
        print(f"\n🔍 Accediendo a: {url}")

        try:
            self.driver.get(url)
            print("⏳ Esperando carga de Angular (10 segundos)...")
            time.sleep(10)

            # Capturar todo el HTML para análisis
            page_source = self.driver.page_source
            with open("seace_page_source.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("📄 HTML guardado en 'seace_page_source.html'")

            # Intentar obtener el texto visible
            body = self.driver.find_element(By.TAG_NAME, "body")
            texto_visible = body.text

            # Guardar screenshot
            self.driver.save_screenshot("seace_segmento_43.png")
            print("📸 Screenshot guardado: 'seace_segmento_43.png'")

            # Análisis del contenido
            print("\n📊 ANÁLISIS DEL CONTENIDO:")
            print(f"  - Longitud del HTML: {len(page_source)} caracteres")
            print(f"  - Longitud del texto visible: {len(texto_visible)} caracteres")

            # Buscar indicadores del segmento 43
            if "43" in texto_visible:
                print("  ✓ Segmento 43 detectado en la página")

            if "telecomunicaciones" in texto_visible.lower():
                print("  ✓ Palabra 'telecomunicaciones' encontrada")

            # Buscar elementos de tabla o lista
            elementos = {
                "tablas": len(self.driver.find_elements(By.TAG_NAME, "table")),
                "mat-tables": len(self.driver.find_elements(By.TAG_NAME, "mat-table")),
                "divs": len(self.driver.find_elements(By.TAG_NAME, "div")),
                "mat-cards": len(self.driver.find_elements(By.TAG_NAME, "mat-card"))
            }

            print("\n📋 ELEMENTOS ENCONTRADOS:")
            for elem, count in elementos.items():
                if count > 0:
                    print(f"  - {elem}: {count}")

            # Extraer datos si hay tabla
            if elementos["tablas"] > 0 or elementos["mat-tables"] > 0:
                return self.extraer_datos_tabla()
            else:
                print("\n⚠️ No se encontraron tablas. Extrayendo texto completo...")
                return self.extraer_texto_estructurado(texto_visible)

        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def extraer_datos_tabla(self):
        """Extrae datos de cualquier tabla encontrada"""
        procesos = []

        try:
            # Buscar cualquier tabla
            tablas = self.driver.find_elements(By.CSS_SELECTOR, "table, mat-table, [role='table']")

            for tabla in tablas:
                filas = tabla.find_elements(By.CSS_SELECTOR, "tr, mat-row, [role='row']")
                print(f"\n  Procesando tabla con {len(filas)} filas...")

                for i, fila in enumerate(filas[1:27], 1):  # Max 26 filas
                    texto_fila = fila.text.strip()
                    if texto_fila:
                        procesos.append({
                            "numero": i,
                            "contenido": texto_fila,
                            "segmento": "43"
                        })

        except Exception as e:
            print(f"  Error extrayendo tabla: {e}")

        return procesos

    def extraer_texto_estructurado(self, texto):
        """Extrae y estructura el texto visible"""
        lineas = [l.strip() for l in texto.split('\n') if l.strip()]
        procesos = []
        proceso_actual = {}

        for linea in lineas:
            # Detectar nomenclatura de proceso
            if any(x in linea for x in ['LP-', 'CP-', 'AS-', 'AMC-', 'SIE-']):
                if proceso_actual:
                    procesos.append(proceso_actual)
                proceso_actual = {"nomenclatura": linea, "segmento": "43"}

            # Agregar información al proceso actual
            elif proceso_actual:
                if "S/" in linea or "$" in linea:
                    proceso_actual["valor"] = linea
                elif len(linea) > 20:
                    proceso_actual["descripcion"] = proceso_actual.get("descripcion", "") + " " + linea

        # Agregar último proceso
        if proceso_actual:
            procesos.append(proceso_actual)

        return procesos

    def guardar_y_mostrar_resultados(self, procesos):
        """Guarda y muestra los resultados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"segmento_43_{timestamp}.json"

        resultado = {
            "fecha_extraccion": datetime.now().isoformat(),
            "segmento": "43",
            "url": "https://prod4.seace.gob.pe/openegocio/#/lista/43",
            "total_procesos": len(procesos),
            "procesos": procesos
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Datos guardados en: {filename}")

        if procesos:
            print(f"\n✅ {len(procesos)} elementos encontrados")
            print("\nPrimeros 3 elementos:")
            for p in procesos[:3]:
                print(f"  - {json.dumps(p, ensure_ascii=False)[:150]}...")
        else:
            print("\n⚠️ No se encontraron procesos estructurados")

    def cerrar(self):
        """Cierra el navegador"""
        self.driver.quit()
        print("🔒 Navegador cerrado")

def main():
    print("="*70)
    print(" EXTRACTOR SEACE SEGMENTO 43 - CON DRIVER AUTOMÁTICO")
    print("="*70)

    try:
        # headless=False para ver qué pasa
        extractor = SEACEExtractor(headless=False)
        procesos = extractor.obtener_segmento_43()
        extractor.guardar_y_mostrar_resultados(procesos)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nSoluciones:")
        print("1. Instalar Google Chrome: sudo apt-get install google-chrome-stable")
        print("2. O usar Chromium: sudo apt-get install chromium-browser")
        print("3. Verificar conexión a internet")

    finally:
        try:
            extractor.cerrar()
        except:
            pass

if __name__ == "__main__":
    main()