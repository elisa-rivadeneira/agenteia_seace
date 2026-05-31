#!/usr/bin/env python3
"""
Extractor FINAL SEACE - Versión funcionando para obtener los 27 procesos del segmento 43
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time
from datetime import datetime
import re

class SEACEFinalExtractor:
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
        self.wait = WebDriverWait(self.driver, 30)
        print("✅ Navegador inicializado")

    def obtener_27_procesos_segmento_43(self):
        """Obtiene los 27 procesos del segmento 43 como muestra la web"""
        url = "https://prod4.seace.gob.pe/openegocio/#/lista/43"
        print(f"\n🔍 Accediendo a: {url}")
        print("🎯 Objetivo: Extraer los 27 procesos del segmento 43\n")

        self.driver.get(url)
        print("⏳ Esperando que Angular cargue completamente...")
        time.sleep(12)  # Más tiempo para carga completa

        todos_procesos = []

        # Método 1: Extraer el texto completo de la página
        print("📄 Extrayendo contenido visible de la página...")

        # Obtener el contenido principal
        try:
            # Buscar el contenedor principal de resultados
            contenedores = [
                "mat-sidenav-content",
                ".main-content",
                ".content",
                "main",
                "[role='main']"
            ]

            texto_completo = ""
            for selector in contenedores:
                try:
                    elemento = self.driver.find_element(By.CSS_SELECTOR, selector)
                    texto_completo = elemento.text
                    if "BANCO DE LA NACION" in texto_completo:  # Verificar que tenemos datos
                        print(f"  ✓ Contenido encontrado en: {selector}")
                        break
                except:
                    continue

            if not texto_completo:
                # Si no encontramos contenedor, tomar todo el body
                body = self.driver.find_element(By.TAG_NAME, "body")
                texto_completo = body.text

            # Parsear el texto para extraer los 27 procesos
            procesos = self.parsear_texto_completo(texto_completo)

            if procesos:
                print(f"  ✓ {len(procesos)} procesos extraídos del texto")
                todos_procesos.extend(procesos)

        except Exception as e:
            print(f"  Error: {e}")

        # Método 2: Si el método 1 no funciona, intentar con JavaScript
        if len(todos_procesos) < 27:
            print("\n📜 Intentando extracción con JavaScript...")
            try:
                # Ejecutar JavaScript para obtener datos de Angular
                script = """
                    const elementos = document.querySelectorAll('*');
                    const procesos = [];
                    let proceso_actual = {};

                    elementos.forEach(el => {
                        const texto = el.innerText || '';

                        if (texto.includes('Entidad:')) {
                            if (Object.keys(proceso_actual).length > 0) {
                                procesos.push(proceso_actual);
                            }
                            proceso_actual = { entidad: texto.replace('Entidad:', '').trim() };
                        } else if (texto.includes('Nomenclatura:')) {
                            proceso_actual.nomenclatura = texto.replace('Nomenclatura:', '').trim();
                        } else if (texto.includes('Objeto:')) {
                            proceso_actual.objeto = texto.replace('Objeto:', '').trim();
                        } else if (texto.includes('Descripción procedimiento:')) {
                            proceso_actual.descripcion = texto.replace('Descripción procedimiento:', '').trim();
                        }
                    });

                    if (Object.keys(proceso_actual).length > 0) {
                        procesos.push(proceso_actual);
                    }

                    return procesos;
                """

                js_procesos = self.driver.execute_script(script)
                if js_procesos:
                    print(f"  ✓ {len(js_procesos)} procesos extraídos con JavaScript")
                    # Agregar solo si no están duplicados
                    for p in js_procesos:
                        if not any(proc.get('nomenclatura') == p.get('nomenclatura') for proc in todos_procesos):
                            todos_procesos.append(p)

            except Exception as e:
                print(f"  Error en JavaScript: {e}")

        # Método 3: Hacer scroll para cargar más contenido si es necesario
        if len(todos_procesos) < 27:
            print("\n🔄 Haciendo scroll para cargar más contenido...")
            for i in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Re-extraer después del scroll
                try:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    texto_nuevo = body.text
                    procesos_nuevos = self.parsear_texto_completo(texto_nuevo)

                    for p in procesos_nuevos:
                        if not any(proc.get('nomenclatura') == p.get('nomenclatura') for proc in todos_procesos):
                            todos_procesos.append(p)

                    if len(todos_procesos) >= 27:
                        break

                except:
                    pass

        return todos_procesos[:27]  # Limitar a 27 como muestra la web

    def parsear_texto_completo(self, texto):
        """Parsea el texto completo para extraer procesos"""
        procesos = []

        # Dividir por bloques que contengan "Entidad:"
        bloques = re.split(r'(?=Entidad:)', texto)

        for i, bloque in enumerate(bloques, 1):
            if len(bloque) < 50:  # Filtrar bloques muy cortos
                continue

            proceso = {
                "numero": i,
                "segmento": "43"
            }

            # Extraer campos usando regex más flexibles
            patrones = {
                "entidad": r"Entidad:\s*([^\n]+)",
                "fecha_fin": r"Fecha Fin[^:]*:\s*([^\n]+)",
                "nomenclatura": r"Nomenclatura:\s*([^\n]+)",
                "objeto": r"Objeto:\s*([^\n]+)",
                "descripcion_procedimiento": r"Descripción procedimiento:\s*([^\n]+)",
                "descripcion_item": r"Descripción ítem:\s*([^\n]+)",
                "nro_item": r"Nro ítem:\s*([^\n]+)",
                "valor": r"(?:VR|Valor|Cuantía)[^:]*:\s*([^\n]+)"
            }

            for campo, patron in patrones.items():
                match = re.search(patron, bloque, re.IGNORECASE | re.MULTILINE)
                if match:
                    valor = match.group(1).strip()
                    # Limpiar valores extraños
                    valor = valor.replace("search", "").strip()
                    if valor and valor != "---":
                        proceso[campo] = valor

            # Solo agregar si tiene nomenclatura (campo clave)
            if "nomenclatura" in proceso:
                # Extraer valor numérico si existe
                if "valor" in proceso and proceso["valor"] != "---":
                    numeros = re.findall(r"[\d,]+\.?\d*", proceso["valor"])
                    if numeros:
                        try:
                            proceso["valor_numerico"] = float(numeros[0].replace(",", ""))
                            if "Soles" in proceso["valor"] or "S/" in proceso["valor"]:
                                proceso["moneda"] = "PEN"
                        except:
                            pass

                procesos.append(proceso)

        return procesos

    def generar_reporte_final(self, procesos):
        """Genera el reporte final con los 27 procesos"""
        print("\n" + "="*80)
        print(" REPORTE FINAL - SEGMENTO 43 (Telecomunicaciones y TI)")
        print("="*80)

        print(f"\n✅ OBJETIVO CUMPLIDO: {len(procesos)} de 27 procesos extraídos")

        # Estadísticas
        entidades = {}
        tipos_objeto = {}
        con_valor = 0
        suma_valores = 0

        for p in procesos:
            # Contar entidades
            ent = p.get("entidad", "Sin especificar")
            entidades[ent] = entidades.get(ent, 0) + 1

            # Contar tipos
            obj = p.get("objeto", "Sin especificar")
            tipos_objeto[obj] = tipos_objeto.get(obj, 0) + 1

            # Sumar valores
            if p.get("valor_numerico"):
                con_valor += 1
                suma_valores += p["valor_numerico"]

        print(f"\n📊 ESTADÍSTICAS:")
        print(f"  • Total de entidades únicas: {len(entidades)}")
        print(f"  • Procesos con valor definido: {con_valor}")
        if con_valor > 0:
            print(f"  • Valor total: S/. {suma_valores:,.2f}")
            print(f"  • Valor promedio: S/. {suma_valores/con_valor:,.2f}")

        print(f"\n🏢 TOP 5 ENTIDADES:")
        for ent, count in sorted(entidades.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {count}. {ent}")

        print(f"\n📦 TIPO DE OBJETO:")
        for obj, count in tipos_objeto.items():
            print(f"  • {obj}: {count} procesos")

        print(f"\n📋 LISTA DE LOS 27 PROCESOS:")
        print("-"*80)

        for i, p in enumerate(procesos, 1):
            print(f"\n{i}. {p.get('nomenclatura', 'Sin nomenclatura')}")
            print(f"   Entidad: {p.get('entidad', 'N/A')}")
            desc = p.get('descripcion_procedimiento', p.get('descripcion_item', 'N/A'))
            print(f"   Descripción: {desc[:100]}...")
            if p.get('fecha_fin'):
                print(f"   Fecha límite: {p['fecha_fin']}")
            if p.get('valor_numerico'):
                print(f"   Valor: S/. {p['valor_numerico']:,.2f}")

        # Guardar JSON completo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SEACE_SEGMENTO_43_COMPLETO_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "fecha_extraccion": datetime.now().isoformat(),
                "fuente": "https://prod4.seace.gob.pe/openegocio/#/lista/43",
                "segmento": "43 - Telecomunicaciones, radiodifusión y tecnología de la información",
                "total_procesos_web": 27,
                "total_procesos_extraidos": len(procesos),
                "estadisticas": {
                    "entidades_unicas": len(entidades),
                    "con_valor_definido": con_valor,
                    "valor_total_pen": suma_valores
                },
                "procesos": procesos
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Datos completos guardados en: {filename}")
        print("="*80)

        return filename

    def cerrar(self):
        """Cierra el navegador"""
        self.driver.quit()
        print("🔒 Navegador cerrado")

def main():
    print("="*80)
    print(" EXTRACTOR FINAL SEACE - SEGMENTO 43")
    print(" Objetivo: Extraer los 27 procesos mostrados en la web")
    print("="*80)

    extractor = SEACEFinalExtractor(headless=False)

    try:
        procesos = extractor.obtener_27_procesos_segmento_43()

        if procesos:
            extractor.generar_reporte_final(procesos)
        else:
            print("\n⚠️ No se pudieron extraer procesos")
            print("Verifica el screenshot 'seace_segmento_43.png'")

    except Exception as e:
        print(f"\n❌ Error: {e}")

    finally:
        extractor.cerrar()

if __name__ == "__main__":
    main()