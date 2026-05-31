#!/usr/bin/env python3
"""
Extractor COMPLETO para SEACE - Navega entre todas las páginas disponibles
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json
import time
from datetime import datetime

def extraer_todas_las_oportunidades():
    print("="*80)
    print(" EXTRACTOR COMPLETO SEACE - TODAS LAS PÁGINAS")
    print("="*80)
    print(f"\nFecha/Hora: {datetime.now()}")

    # Cargar configuración para análisis posterior
    try:
        with open('config_empresa.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        empresa = config['empresa']
        print(f"🏢 Empresa: {empresa['nombre']}")
    except:
        print("⚠️ No se pudo cargar config_empresa.json")
        config = None

    # Configurar navegador
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 30)

    todas_las_oportunidades = []
    nomenclaturas_vistas = set()  # Para evitar duplicados

    try:
        # Acceder al segmento 43
        url = "https://prod4.seace.gob.pe/openegocio/#/lista/43"
        print(f"\n🌐 Accediendo a: {url}")
        driver.get(url)

        print("⏳ Esperando carga inicial completa...")
        time.sleep(15)

        # Verificar cuántas oportunidades hay en total
        try:
            texto_body = driver.find_element(By.TAG_NAME, "body").text
            if "Se encontraron" in texto_body:
                import re
                match = re.search(r'Se encontraron (\d+) oportunidades', texto_body)
                if match:
                    total_esperado = int(match.group(1))
                    print(f"📊 Total de oportunidades esperadas: {total_esperado}")
                else:
                    total_esperado = 0
        except:
            total_esperado = 0

        pagina_actual = 1
        sin_mas_paginas = False

        while not sin_mas_paginas:
            print(f"\n📄 Procesando página {pagina_actual}...")

            try:
                # Esperar a que las filas se carguen
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "mat-row, .mat-row")))
                time.sleep(2)  # Dar tiempo para que se cargue completamente

                # Obtener todas las filas de la página actual
                filas = driver.find_elements(By.CSS_SELECTOR, "mat-row, .mat-row")
                print(f"  ✓ Encontradas {len(filas)} filas en página {pagina_actual}")

                oportunidades_pagina = 0
                for i, fila in enumerate(filas, 1):
                    try:
                        # Obtener todas las celdas de la fila
                        celdas = fila.find_elements(By.CSS_SELECTOR, "mat-cell, .mat-cell")

                        if len(celdas) >= 8:
                            nomenclatura = celdas[2].text.strip()

                            # Verificar si ya procesamos esta oportunidad
                            if nomenclatura and nomenclatura != "Nomenclatura" and nomenclatura not in nomenclaturas_vistas:
                                oportunidad = {
                                    "numero": len(todas_las_oportunidades) + 1,
                                    "entidad": celdas[0].text.strip(),
                                    "fecha_fin": celdas[1].text.strip(),
                                    "nomenclatura": nomenclatura,
                                    "objeto": celdas[3].text.strip(),
                                    "descripcion_procedimiento": celdas[4].text.strip(),
                                    "descripcion_item": celdas[5].text.strip(),
                                    "nro_item": celdas[6].text.strip() if len(celdas) > 6 else "1",
                                    "valor": celdas[7].text.strip() if len(celdas) > 7 else "---",
                                    "pagina": pagina_actual,
                                    "fecha_extraccion": datetime.now().isoformat()
                                }

                                nomenclaturas_vistas.add(nomenclatura)
                                todas_las_oportunidades.append(oportunidad)
                                oportunidades_pagina += 1
                                print(f"    {oportunidad['numero']}. {oportunidad['entidad'][:40]}... - {nomenclatura}")

                    except Exception as e:
                        print(f"    ⚠️ Error procesando fila {i}: {str(e)[:50]}")

                print(f"  📊 {oportunidades_pagina} oportunidades nuevas capturadas en página {pagina_actual}")

                # Intentar navegar a la siguiente página
                print(f"\n🔍 Buscando botón de siguiente página...")

                siguiente_encontrado = False

                # Estrategia 1: Buscar botón de siguiente en el paginador
                try:
                    # Primero hacer scroll hasta el paginador
                    paginador = driver.find_element(By.TAG_NAME, "mat-paginator")
                    driver.execute_script("arguments[0].scrollIntoView(true);", paginador)
                    time.sleep(1)

                    # Buscar botón siguiente
                    botones_siguiente = [
                        "button[aria-label*='Next']",
                        "button[aria-label*='next']",
                        "button[aria-label*='Siguiente']",
                        "button[aria-label*='siguiente']",
                        ".mat-paginator-navigation-next"
                    ]

                    for selector in botones_siguiente:
                        try:
                            btn = driver.find_element(By.CSS_SELECTOR, selector)
                            if btn and btn.is_enabled() and "disabled" not in btn.get_attribute("class"):
                                print(f"  → Navegando a página {pagina_actual + 1}...")
                                driver.execute_script("arguments[0].click();", btn)
                                time.sleep(5)  # Esperar que cargue la nueva página
                                siguiente_encontrado = True
                                pagina_actual += 1
                                break
                        except:
                            continue

                except Exception as e:
                    print(f"  ⚠️ Error buscando paginador: {str(e)[:50]}")

                # Estrategia 2: Si no encontramos botón o está deshabilitado
                if not siguiente_encontrado:
                    # Verificar si hay números de página directos
                    try:
                        paginas = driver.find_elements(By.CSS_SELECTOR, "button.mat-paginator-page, a.page-link")
                        pagina_siguiente = None

                        for p in paginas:
                            texto = p.text.strip()
                            if texto.isdigit() and int(texto) == pagina_actual + 1:
                                pagina_siguiente = p
                                break

                        if pagina_siguiente:
                            driver.execute_script("arguments[0].click();", pagina_siguiente)
                            time.sleep(5)
                            siguiente_encontrado = True
                            pagina_actual += 1
                            print(f"  → Navegando a página {pagina_actual} mediante número directo...")
                    except:
                        pass

                if not siguiente_encontrado:
                    print("  ✓ No hay más páginas disponibles o se alcanzó el final")
                    sin_mas_paginas = True

                # Verificar si ya tenemos todas las oportunidades esperadas
                if total_esperado > 0 and len(todas_las_oportunidades) >= total_esperado:
                    print(f"\n✅ Se han capturado todas las {total_esperado} oportunidades esperadas")
                    sin_mas_paginas = True

                # Límite de seguridad
                if pagina_actual > 10:  # Máximo 10 páginas para evitar bucles infinitos
                    print("\n⚠️ Se alcanzó el límite máximo de páginas (10)")
                    sin_mas_paginas = True

            except TimeoutException:
                print(f"  ⚠️ Timeout esperando elementos en página {pagina_actual}")
                sin_mas_paginas = True
            except Exception as e:
                print(f"  ❌ Error en página {pagina_actual}: {str(e)}")
                sin_mas_paginas = True

    except Exception as e:
        print(f"\n❌ Error durante la extracción: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()

    # Analizar compatibilidad si tenemos configuración
    if config and todas_las_oportunidades:
        print("\n🤖 Analizando compatibilidad con tu empresa...")
        palabras_positivas = empresa.get('palabras_clave_positivas', [])
        palabras_negativas = empresa.get('palabras_clave_negativas', [])

        for op in todas_las_oportunidades:
            texto_completo = f"{op['descripcion_procedimiento']} {op['descripcion_item']} {op['entidad']}".lower()

            # Calcular score básico
            score = 0
            razones = []

            # Puntos positivos
            for palabra in palabras_positivas:
                if palabra.lower() in texto_completo:
                    score += 5
                    razones.append(f"+{palabra}")

            # Puntos negativos
            for palabra in palabras_negativas:
                if palabra.lower() in texto_completo:
                    score -= 10
                    razones.append(f"-{palabra}")

            # Normalizar score
            score = max(0, min(100, score))

            op['score_compatibilidad'] = score
            op['razones'] = razones[:5]  # Primeras 5 razones

    # Ordenar por compatibilidad
    todas_las_oportunidades.sort(key=lambda x: x.get('score_compatibilidad', 0), reverse=True)

    # Guardar resultados
    resultado = {
        "fecha_extraccion": datetime.now().isoformat(),
        "segmento": "43",
        "url": url,
        "total_oportunidades": len(todas_las_oportunidades),
        "total_paginas_procesadas": pagina_actual,
        "oportunidades_esperadas": total_esperado,
        "oportunidades": todas_las_oportunidades
    }

    filename = f"seace_todas_oportunidades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Datos guardados en: {filename}")

    # Resumen detallado
    print("\n" + "="*80)
    print(" RESUMEN COMPLETO DE EXTRACCIÓN")
    print("="*80)
    print(f"Total de oportunidades encontradas: {len(todas_las_oportunidades)}")
    print(f"Total de páginas procesadas: {pagina_actual}")

    if total_esperado > 0:
        porcentaje = (len(todas_las_oportunidades) / total_esperado) * 100
        print(f"Completitud: {porcentaje:.1f}% ({len(todas_las_oportunidades)}/{total_esperado})")

    if config and todas_las_oportunidades:
        altamente_compatibles = [op for op in todas_las_oportunidades if op.get('score_compatibilidad', 0) >= 70]
        compatibles = [op for op in todas_las_oportunidades if 50 <= op.get('score_compatibilidad', 0) < 70]

        print(f"\n📊 Análisis de compatibilidad:")
        print(f"  🌟 Altamente compatibles (≥70%): {len(altamente_compatibles)}")
        print(f"  ✅ Compatibles (50-69%): {len(compatibles)}")
        print(f"  ⚠️ Baja compatibilidad (<50%): {len(todas_las_oportunidades) - len(altamente_compatibles) - len(compatibles)}")

        if altamente_compatibles:
            print(f"\n🎯 TOP 5 Oportunidades más compatibles:")
            for i, op in enumerate(altamente_compatibles[:5], 1):
                print(f"\n  {i}. {op['entidad']}")
                print(f"     Nomenclatura: {op['nomenclatura']}")
                print(f"     Score: {op['score_compatibilidad']}%")
                print(f"     Fecha límite: {op['fecha_fin']}")
                print(f"     Descripción: {op['descripcion_procedimiento'][:80]}...")

    return resultado

if __name__ == "__main__":
    resultado = extraer_todas_las_oportunidades()
    print(f"\n✅ Proceso completado exitosamente")