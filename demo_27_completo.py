#!/usr/bin/env python3
"""
DEMO: Extractor de las 27 oportunidades COMPLETAS del segmento 43
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
import re
from datetime import datetime

print("="*80)
print(" EXTRACTOR COMPLETO: LAS 27 OPORTUNIDADES DEL SEGMENTO 43")
print("="*80)

# Cargar configuración
with open('config_empresa.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

empresa = config['empresa']
print(f"\n🏢 Empresa: {empresa['nombre']}")

print("\n🔍 Accediendo al SEACE para obtener TODAS las 27 oportunidades...")

# Configurar navegador
options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

try:
    # Acceder al segmento 43
    url = "https://prod4.seace.gob.pe/openegocio/#/lista/43"
    driver.get(url)
    print("⏳ Esperando carga completa de Angular...")
    time.sleep(15)

    todas_las_oportunidades = []
    textos_unicos = set()

    print("\n📄 Extrayendo página por página...")

    for pagina in range(1, 4):  # Máximo 3 páginas (10+10+7 = 27)
        print(f"\n   Página {pagina}:")

        # Obtener texto de la página actual
        body = driver.find_element(By.TAG_NAME, "body")
        texto_pagina = body.text

        # Extraer oportunidades del texto
        bloques = re.split(r'(?=Entidad:\n)', texto_pagina)

        oportunidades_pagina = 0
        for bloque in bloques:
            if 'Nomenclatura:\n' in bloque and len(bloque) > 100:
                # Extraer nomenclatura como identificador único
                match = re.search(r'Nomenclatura:\n([^\n]+)', bloque)
                if match:
                    nomenclatura = match.group(1)

                    # Solo agregar si no está duplicado
                    if nomenclatura not in textos_unicos:
                        textos_unicos.add(nomenclatura)

                        # Extraer todos los datos
                        datos = {'nomenclatura': nomenclatura}

                        # Entidad
                        match = re.search(r'Entidad:\n([^\n]+)', bloque)
                        if match:
                            datos['entidad'] = match.group(1)

                        # Descripción procedimiento
                        match = re.search(r'Descripción procedimiento:\n([^\n]+)', bloque)
                        if match:
                            datos['descripcion'] = match.group(1)

                        # Descripción item
                        match = re.search(r'Descripción ítem:\n([^\n]+)', bloque)
                        if match:
                            datos['descripcion_item'] = match.group(1)

                        # Fecha
                        match = re.search(r'Fecha Fin[^\n]*:\n([^\n]+)', bloque)
                        if match:
                            datos['fecha_fin'] = match.group(1)

                        # Valor
                        match = re.search(r'VR/[^\n]*:\n([^\n]+)', bloque)
                        if match:
                            datos['valor'] = match.group(1)

                        todas_las_oportunidades.append(datos)
                        oportunidades_pagina += 1

        print(f"      ✓ {oportunidades_pagina} oportunidades extraídas")

        # Si ya tenemos 27, salir
        if len(todas_las_oportunidades) >= 27:
            break

        # Buscar botón de siguiente página
        if pagina < 3:
            try:
                # Intentar hacer clic en "Siguiente" o flecha derecha
                siguiente_encontrado = False

                # Buscar por diferentes selectores
                selectores_siguiente = [
                    "//button[contains(@aria-label, 'Next')]",
                    "//button[contains(@aria-label, 'Siguiente')]",
                    "//button[contains(., '>')]",
                    "//mat-icon[contains(., 'navigate_next')]",
                    "//button[@class='mat-paginator-navigation-next']",
                    "//button[contains(@class, 'next')]"
                ]

                for selector in selectores_siguiente:
                    try:
                        boton = driver.find_element(By.XPATH, selector)
                        if boton.is_enabled():
                            driver.execute_script("arguments[0].scrollIntoView(true);", boton)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", boton)
                            print(f"      → Navegando a página {pagina + 1}...")
                            time.sleep(5)
                            siguiente_encontrado = True
                            break
                    except:
                        continue

                if not siguiente_encontrado:
                    # Método alternativo: Hacer scroll hasta el final
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)

                    # Verificar si aparecieron más elementos
                    body_nuevo = driver.find_element(By.TAG_NAME, "body")
                    if body_nuevo.text != texto_pagina:
                        print(f"      → Más contenido cargado con scroll...")

            except Exception as e:
                print(f"      No hay más páginas disponibles")
                break

finally:
    driver.quit()

# Mostrar resultados
print("\n" + "="*80)
print(f" ✅ TOTAL DE OPORTUNIDADES EXTRAÍDAS: {len(todas_las_oportunidades)}")
print("="*80)

# Analizar compatibilidad con la empresa
print("\n🤖 ANALIZANDO COMPATIBILIDAD CON TU EMPRESA...")
print("-"*80)

oportunidades_evaluadas = []

for op in todas_las_oportunidades:
    score = 0
    razones = []

    # Combinar todo el texto para análisis
    texto_completo = f"{op.get('descripcion', '')} {op.get('descripcion_item', '')} {op.get('entidad', '')}".lower()

    # Evaluar palabras clave positivas
    palabras_encontradas = []
    for palabra in empresa['palabras_clave_positivas']:
        if palabra.lower() in texto_completo:
            palabras_encontradas.append(palabra)

    if palabras_encontradas:
        score += min(50, len(palabras_encontradas) * 8)
        razones.append(f"✅ Keywords: {', '.join(palabras_encontradas[:5])}")

    # Evaluar palabras negativas
    for palabra in empresa['palabras_clave_negativas']:
        if palabra.lower() in texto_completo:
            score -= 30
            razones.append(f"⚠️ Contiene: {palabra}")
            break

    # Bonus por entidad objetivo
    entidad = op.get('entidad', '').lower()
    for target in empresa['entidades_objetivo']:
        if target.lower() in entidad:
            score += 25
            razones.append(f"✅ Entidad objetivo")
            break

    # Evaluar valor si está disponible
    valor = op.get('valor', '')
    if valor and valor != '---':
        if 'Soles' in valor or 'PEN' in valor:
            # Extraer número
            numeros = re.findall(r'[\d,]+\.?\d*', valor)
            if numeros:
                try:
                    monto = float(numeros[0].replace(',', ''))
                    if empresa['montos_preferidos']['minimo'] <= monto <= empresa['montos_preferidos']['maximo']:
                        score += 15
                        razones.append(f"✅ Monto en rango: S/. {monto:,.0f}")
                    op['monto_numerico'] = monto
                except:
                    pass

    # Evaluar urgencia
    fecha = op.get('fecha_fin', '')
    if fecha:
        try:
            # Parsear fecha DD/MM/YYYY
            fecha_limite = datetime.strptime(fecha.split()[0], '%d/%m/%Y')
            dias_restantes = (fecha_limite - datetime.now()).days
            op['dias_restantes'] = dias_restantes

            if dias_restantes > 7:
                score += 10
                razones.append(f"✅ {dias_restantes} días disponibles")
            elif dias_restantes > 3:
                razones.append(f"⚠️ Solo {dias_restantes} días")
            else:
                score -= 10
                razones.append(f"❌ Muy urgente: {dias_restantes} días")
        except:
            pass

    # Guardar evaluación
    op['score'] = max(0, min(100, score))
    op['razones'] = razones
    oportunidades_evaluadas.append(op)

# Ordenar por score
oportunidades_evaluadas.sort(key=lambda x: x['score'], reverse=True)

# Mostrar las 27 oportunidades con su evaluación
print("\n📊 LAS 27 OPORTUNIDADES DEL SEGMENTO 43 - ORDENADAS POR COMPATIBILIDAD:")
print("="*80)

# Categorizar
altamente_compatibles = [op for op in oportunidades_evaluadas if op['score'] >= 70]
compatibles = [op for op in oportunidades_evaluadas if 50 <= op['score'] < 70]
poco_compatibles = [op for op in oportunidades_evaluadas if op['score'] < 50]

if altamente_compatibles:
    print(f"\n🌟 ALTAMENTE COMPATIBLES ({len(altamente_compatibles)}):")
    print("-"*80)
    for i, op in enumerate(altamente_compatibles, 1):
        print(f"\n{i}. [{op['score']}%] {op['nomenclatura']}")
        print(f"   {op.get('entidad', 'N/A')}")
        print(f"   {op.get('descripcion', 'N/A')[:80]}...")
        if 'monto_numerico' in op:
            print(f"   💰 S/. {op['monto_numerico']:,.0f}")
        if 'dias_restantes' in op:
            print(f"   ⏰ {op['dias_restantes']} días restantes")
        for razon in op['razones'][:3]:
            print(f"   {razon}")

if compatibles:
    print(f"\n✅ COMPATIBLES ({len(compatibles)}):")
    print("-"*80)
    for i, op in enumerate(compatibles[:5], 1):
        print(f"{i}. [{op['score']}%] {op['nomenclatura']} - {op.get('entidad', 'N/A')[:40]}")

if poco_compatibles:
    print(f"\n⚠️ POCO COMPATIBLES ({len(poco_compatibles)}):")
    print("-"*80)
    for i, op in enumerate(poco_compatibles[:5], 1):
        print(f"{i}. [{op['score']}%] {op['nomenclatura']}")

# Resumen final
print("\n" + "="*80)
print(" 📈 RESUMEN EJECUTIVO")
print("="*80)
print(f"""
Total de oportunidades en segmento 43: {len(todas_las_oportunidades)}
  🌟 Altamente compatibles (>70%): {len(altamente_compatibles)}
  ✅ Compatibles (50-70%): {len(compatibles)}
  ⚠️ Poco compatibles (<50%): {len(poco_compatibles)}

RECOMENDACIÓN:
  Enfocarse en las {len(altamente_compatibles)} oportunidades altamente compatibles
  Revisar las {len(compatibles)} compatibles según capacidad disponible

📧 Sistema configurado para alertar a: {config['notificaciones']['email']}
""")

# Guardar resultados
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"analisis_27_oportunidades_{timestamp}.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump({
        'fecha_analisis': datetime.now().isoformat(),
        'total_oportunidades': len(todas_las_oportunidades),
        'altamente_compatibles': len(altamente_compatibles),
        'compatibles': len(compatibles),
        'oportunidades': oportunidades_evaluadas
    }, f, ensure_ascii=False, indent=2)

print(f"💾 Análisis completo guardado en: {filename}")
print("="*80)