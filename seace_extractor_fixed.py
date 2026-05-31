#!/usr/bin/env python3
"""
Extractor CORREGIDO para SEACE - Captura las oportunidades usando mat-table
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time
from datetime import datetime

def extraer_oportunidades_seace():
    print("="*80)
    print(" EXTRACTOR SEACE - SEGMENTO 43 (TECNOLOGÍA)")
    print("="*80)
    print(f"\nFecha/Hora: {datetime.now()}")

    # Configurar navegador
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 30)

    oportunidades = []

    try:
        # Acceder al segmento 43
        url = "https://prod4.seace.gob.pe/openegocio/#/lista/43"
        print(f"\n🌐 Accediendo a: {url}")
        driver.get(url)

        print("⏳ Esperando carga completa...")
        time.sleep(15)

        # Buscar las filas de la tabla mat-table
        print("\n🔍 Buscando oportunidades en mat-table...")

        # Esperar a que aparezcan las filas
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "mat-row, .mat-row")))

        # Obtener todas las filas
        filas = driver.find_elements(By.CSS_SELECTOR, "mat-row, .mat-row")
        print(f"✓ Encontradas {len(filas)} filas en la tabla")

        for i, fila in enumerate(filas, 1):
            try:
                # Obtener todas las celdas de la fila
                celdas = fila.find_elements(By.CSS_SELECTOR, "mat-cell, .mat-cell")

                if len(celdas) >= 8:  # Asegurar que hay suficientes columnas
                    oportunidad = {
                        "numero": i,
                        "entidad": celdas[0].text.strip(),
                        "fecha_fin": celdas[1].text.strip(),
                        "nomenclatura": celdas[2].text.strip(),
                        "objeto": celdas[3].text.strip(),
                        "descripcion_procedimiento": celdas[4].text.strip(),
                        "descripcion_item": celdas[5].text.strip(),
                        "nro_item": celdas[6].text.strip() if len(celdas) > 6 else "1",
                        "valor": celdas[7].text.strip() if len(celdas) > 7 else "---",
                        "fecha_extraccion": datetime.now().isoformat()
                    }

                    # Filtrar filas vacías o de encabezado
                    if oportunidad["entidad"] and oportunidad["entidad"] != "Entidad":
                        oportunidades.append(oportunidad)
                        print(f"  {i}. {oportunidad['entidad'][:50]}... - {oportunidad['nomenclatura']}")

            except Exception as e:
                print(f"  ⚠️ Error procesando fila {i}: {str(e)[:50]}")

        # Verificar si hay paginación y más páginas
        try:
            paginador = driver.find_element(By.TAG_NAME, "mat-paginator")
            if paginador:
                print("\n📄 Verificando paginación...")

                # Buscar botón siguiente
                try:
                    btn_siguiente = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Next'], button[aria-label*='Siguiente']")
                    if btn_siguiente and btn_siguiente.is_enabled():
                        print("  → Hay más páginas disponibles (no procesadas en esta versión)")
                except:
                    print("  → No hay más páginas")
        except:
            pass

    except Exception as e:
        print(f"\n❌ Error durante la extracción: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()

    # Guardar resultados
    resultado = {
        "fecha_extraccion": datetime.now().isoformat(),
        "segmento": "43",
        "url": url,
        "total_oportunidades": len(oportunidades),
        "oportunidades": oportunidades
    }

    filename = f"seace_oportunidades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Datos guardados en: {filename}")

    # Resumen
    print("\n" + "="*80)
    print(" RESUMEN DE EXTRACCIÓN")
    print("="*80)
    print(f"Total de oportunidades encontradas: {len(oportunidades)}")

    if oportunidades:
        print("\n📊 Primeras 5 oportunidades:")
        for op in oportunidades[:5]:
            print(f"\n  • {op['entidad']}")
            print(f"    Nomenclatura: {op['nomenclatura']}")
            print(f"    Descripción: {op['descripcion_procedimiento'][:80]}...")
            print(f"    Fecha límite: {op['fecha_fin']}")

    return resultado

if __name__ == "__main__":
    resultado = extraer_oportunidades_seace()
    print(f"\n✅ Extracción completada: {resultado['total_oportunidades']} oportunidades")