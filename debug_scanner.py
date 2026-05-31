#!/usr/bin/env python3
"""
Debug Scanner - Verifica qué está capturando el navegador del SEACE
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime

print("="*80)
print(" DEBUG SCANNER - VERIFICACIÓN DEL SEACE")
print("="*80)
print(f"\nFecha/Hora: {datetime.now()}")

# Configurar navegador
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
# NO usar headless para poder ver qué pasa
# options.add_argument('--headless=new')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)

try:
    # Acceder al segmento 43
    url = "https://prod4.seace.gob.pe/openegocio/#/lista/43"
    print(f"\n🌐 Accediendo a: {url}")
    driver.get(url)

    print("⏳ Esperando carga de Angular (15 segundos)...")
    time.sleep(15)

    # Guardar screenshot
    driver.save_screenshot("debug_seace_screenshot.png")
    print("📸 Screenshot guardado: debug_seace_screenshot.png")

    # Obtener todo el HTML
    html = driver.page_source
    with open('debug_seace_source.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("📄 HTML guardado: debug_seace_source.html")

    # Obtener texto visible
    body = driver.find_element(By.TAG_NAME, "body")
    texto_visible = body.text

    print(f"\n📊 Longitud del texto capturado: {len(texto_visible)} caracteres")

    # Buscar indicadores de oportunidades
    indicadores = [
        "Entidad:",
        "Nomenclatura:",
        "Descripción procedimiento:",
        "Fecha Fin",
        "VR/ VE/",
        "mat-row",
        "datatable",
        "No se encontraron",
        "Sin resultados",
        "0 resultados"
    ]

    print("\n🔍 Buscando indicadores en el contenido:")
    for indicador in indicadores:
        count = texto_visible.count(indicador)
        if count > 0:
            print(f"  ✓ '{indicador}' encontrado {count} veces")
        else:
            print(f"  ✗ '{indicador}' NO encontrado")

    # Mostrar primeros 500 caracteres del texto
    print("\n📝 Primeros 500 caracteres del texto visible:")
    print("-" * 50)
    print(texto_visible[:500])
    print("-" * 50)

    # Buscar elementos específicos con diferentes estrategias
    print("\n🔎 Buscando elementos del DOM:")

    estrategias = [
        ("mat-row", By.TAG_NAME),
        ("mat-table", By.TAG_NAME),
        ("table", By.TAG_NAME),
        ("[role='row']", By.CSS_SELECTOR),
        (".datatable-row", By.CSS_SELECTOR),
        (".mat-row", By.CSS_SELECTOR),
        ("//div[contains(@class, 'row')]", By.XPATH),
        ("//tr", By.XPATH)
    ]

    for selector, by_type in estrategias:
        try:
            elementos = driver.find_elements(by_type, selector)
            if elementos:
                print(f"  ✓ Encontrados {len(elementos)} elementos con '{selector}'")
                # Mostrar el texto del primer elemento
                if len(elementos) > 0 and elementos[0].text:
                    print(f"    Ejemplo: {elementos[0].text[:100]}...")
        except Exception as e:
            print(f"  ✗ Error buscando '{selector}': {str(e)[:50]}")

    # Verificar si hay paginación
    print("\n📄 Verificando paginación:")
    paginadores = [
        "mat-paginator",
        ".paginator",
        "[aria-label*='page']",
        "button[aria-label*='Next']"
    ]

    for selector in paginadores:
        try:
            if selector.startswith(".") or selector.startswith("["):
                elementos = driver.find_elements(By.CSS_SELECTOR, selector)
            else:
                elementos = driver.find_elements(By.TAG_NAME, selector)
            if elementos:
                print(f"  ✓ Paginador encontrado: '{selector}'")
        except:
            pass

    # Intentar hacer scroll para cargar más contenido
    print("\n📜 Intentando scroll para cargar más contenido...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    body_despues = driver.find_element(By.TAG_NAME, "body")
    texto_despues = body_despues.text

    if len(texto_despues) > len(texto_visible):
        print(f"  ✓ Nuevo contenido cargado: {len(texto_despues) - len(texto_visible)} caracteres adicionales")
    else:
        print("  ℹ️ No se cargó contenido adicional con scroll")

    # Contar bloques de oportunidades manualmente
    print("\n📊 Análisis manual del texto:")
    bloques_entidad = texto_visible.split("Entidad:")
    print(f"  Bloques que empiezan con 'Entidad:': {len(bloques_entidad) - 1}")

    bloques_nomenclatura = texto_visible.split("Nomenclatura:")
    print(f"  Bloques con 'Nomenclatura:': {len(bloques_nomenclatura) - 1}")

    # Guardar el texto completo para análisis
    with open('debug_texto_completo.txt', 'w', encoding='utf-8') as f:
        f.write(texto_despues if len(texto_despues) > len(texto_visible) else texto_visible)
    print("\n💾 Texto completo guardado en: debug_texto_completo.txt")

except Exception as e:
    print(f"\n❌ Error durante el debug: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    print("\n🔚 Cerrando navegador en 5 segundos...")
    time.sleep(5)
    driver.quit()
    print("✅ Debug completado")