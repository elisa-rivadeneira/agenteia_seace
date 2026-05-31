#!/usr/bin/env python3
"""
Extractor completo SEACE - Obtiene TODOS los procesos del segmento 43
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time
from datetime import datetime
import re

class SEACECompleteExtractor:
    def __init__(self, headless=False):
        self.options = Options()
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--window-size=1920,1080')

        if headless:
            self.options.add_argument('--headless=new')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.options)
        self.wait = WebDriverWait(self.driver, 20)
        print("✅ Navegador inicializado")

    def extraer_todos_segmento_43(self):
        """Extrae TODOS los procesos del segmento 43"""
        url = "https://prod4.seace.gob.pe/openegocio/#/lista/43"
        print(f"\n🔍 Accediendo a: {url}")

        self.driver.get(url)
        print("⏳ Esperando carga completa...")
        time.sleep(10)

        todos_procesos = []
        pagina = 1

        while True:
            print(f"\n📄 Procesando página {pagina}...")

            # Extraer procesos de la página actual
            procesos_pagina = self.extraer_procesos_pagina_actual()
            todos_procesos.extend(procesos_pagina)

            print(f"  ✓ {len(procesos_pagina)} procesos extraídos")

            # Buscar botón de siguiente página
            if not self.ir_siguiente_pagina():
                print("  ✓ Última página alcanzada")
                break

            pagina += 1
            time.sleep(3)  # Esperar carga de nueva página

            if pagina > 5:  # Límite de seguridad
                print("  ⚠️ Límite de páginas alcanzado")
                break

        return todos_procesos

    def extraer_procesos_pagina_actual(self):
        """Extrae y parsea los procesos de la página actual"""
        procesos = []

        try:
            # Buscar filas de la tabla
            filas = self.driver.find_elements(By.CSS_SELECTOR, "mat-row, tr[role='row'], tbody tr")

            for i, fila in enumerate(filas, 1):
                texto = fila.text.strip()
                if texto and len(texto) > 50:  # Filtrar filas vacías
                    proceso = self.parsear_proceso(texto, i)
                    if proceso:
                        procesos.append(proceso)

        except Exception as e:
            print(f"  Error extrayendo procesos: {e}")

            # Método alternativo: buscar por divs con contenido
            try:
                divs = self.driver.find_elements(By.CSS_SELECTOR, "div.mat-row, div.proceso-item")
                for i, div in enumerate(divs, 1):
                    texto = div.text.strip()
                    if texto:
                        proceso = self.parsear_proceso(texto, i)
                        if proceso:
                            procesos.append(proceso)
            except:
                pass

        return procesos

    def parsear_proceso(self, texto, numero):
        """Parsea el texto de un proceso para extraer campos"""
        proceso = {
            "numero": numero,
            "texto_completo": texto,
            "segmento": "43"
        }

        # Extraer campos usando regex
        patrones = {
            "entidad": r"Entidad:\s*([^\n]+)",
            "nomenclatura": r"Nomenclatura:\s*([^\n]+)",
            "objeto": r"Objeto:\s*([^\n]+)",
            "descripcion_procedimiento": r"Descripción procedimiento:\s*([^\n]+)",
            "descripcion_item": r"Descripción ítem:\s*([^\n]+)",
            "nro_item": r"Nro ítem:\s*([^\n]+)",
            "valor": r"VR/ VE/ Cuantía[^\n]*:\s*([^\n]+)",
            "fecha_fin": r"Fecha Fin[^\n]*:\s*([^\n]+)"
        }

        for campo, patron in patrones.items():
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                proceso[campo] = match.group(1).strip()

        # Limpiar valor monetario
        if "valor" in proceso:
            valor = proceso["valor"]
            if valor != "---":
                # Extraer números y moneda
                numeros = re.findall(r"[\d,]+\.?\d*", valor)
                if numeros:
                    proceso["valor_numerico"] = float(numeros[0].replace(",", ""))
                    if "Soles" in valor or "PEN" in valor or "S/" in valor:
                        proceso["moneda"] = "PEN"
                    elif "$" in valor or "USD" in valor:
                        proceso["moneda"] = "USD"

        return proceso if "nomenclatura" in proceso else None

    def ir_siguiente_pagina(self):
        """Intenta ir a la siguiente página"""
        try:
            # Buscar botones de paginación
            botones = [
                "button[aria-label*='Next']",
                "button[aria-label*='Siguiente']",
                ".mat-paginator-navigation-next",
                "button.next-page",
                "[aria-label*='página siguiente']"
            ]

            for selector in botones:
                try:
                    boton = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if boton.is_enabled():
                        self.driver.execute_script("arguments[0].click();", boton)
                        print("  → Siguiente página")
                        return True
                except:
                    continue

            # Método alternativo: buscar por texto
            elementos = self.driver.find_elements(By.XPATH, "//*[contains(text(), '>') or contains(@aria-label, 'Next')]")
            for elem in elementos:
                try:
                    if elem.is_enabled():
                        elem.click()
                        print("  → Siguiente página (método alternativo)")
                        return True
                except:
                    continue

        except Exception as e:
            print(f"  No hay más páginas: {e}")

        return False

    def generar_reporte(self, procesos):
        """Genera un reporte detallado de los procesos"""
        print("\n" + "="*70)
        print(" REPORTE FINAL - SEGMENTO 43")
        print("="*70)

        print(f"\n📊 RESUMEN:")
        print(f"  Total de procesos encontrados: {len(procesos)}")

        # Análisis por entidad
        entidades = {}
        for p in procesos:
            entidad = p.get("entidad", "Sin entidad")
            entidades[entidad] = entidades.get(entidad, 0) + 1

        print(f"\n🏢 TOP ENTIDADES:")
        for entidad, count in sorted(entidades.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {entidad}: {count} proceso(s)")

        # Análisis por tipo de objeto
        objetos = {}
        for p in procesos:
            objeto = p.get("objeto", "Sin especificar")
            objetos[objeto] = objetos.get(objeto, 0) + 1

        print(f"\n📦 TIPO DE OBJETO:")
        for obj, count in objetos.items():
            print(f"  - {obj}: {count}")

        # Procesos con valor
        con_valor = [p for p in procesos if p.get("valor_numerico")]
        if con_valor:
            valores = [p["valor_numerico"] for p in con_valor]
            print(f"\n💰 VALORES:")
            print(f"  - Procesos con valor definido: {len(con_valor)}")
            print(f"  - Valor total: S/. {sum(valores):,.2f}")
            print(f"  - Valor promedio: S/. {sum(valores)/len(valores):,.2f}")
            print(f"  - Valor máximo: S/. {max(valores):,.2f}")

        print("\n📋 LISTA COMPLETA DE PROCESOS:")
        for i, p in enumerate(procesos, 1):
            print(f"\n{i}. {p.get('nomenclatura', 'Sin nomenclatura')}")
            print(f"   Entidad: {p.get('entidad', 'N/A')}")
            print(f"   Descripción: {p.get('descripcion_procedimiento', 'N/A')[:80]}...")
            if p.get('valor_numerico'):
                print(f"   Valor: {p.get('moneda', 'PEN')} {p['valor_numerico']:,.2f}")

        # Guardar en JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"seace_segmento_43_completo_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "fecha_extraccion": datetime.now().isoformat(),
                "segmento": "43",
                "total_procesos": len(procesos),
                "resumen": {
                    "entidades": len(entidades),
                    "con_valor": len(con_valor),
                    "valor_total": sum([p["valor_numerico"] for p in con_valor]) if con_valor else 0
                },
                "procesos": procesos
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Datos completos guardados en: {filename}")

    def cerrar(self):
        """Cierra el navegador"""
        self.driver.quit()
        print("🔒 Navegador cerrado")

def main():
    print("="*70)
    print(" EXTRACTOR COMPLETO SEACE - SEGMENTO 43")
    print(" Telecomunicaciones, radiodifusión y tecnología de la información")
    print("="*70)

    extractor = SEACECompleteExtractor(headless=False)

    try:
        procesos = extractor.extraer_todos_segmento_43()
        extractor.generar_reporte(procesos)

    except Exception as e:
        print(f"\n❌ Error: {e}")

    finally:
        extractor.cerrar()

if __name__ == "__main__":
    main()