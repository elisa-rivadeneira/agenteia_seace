#!/usr/bin/env python3
"""
DEMO del Agente IA - Versión rápida para mostrar funcionalidad
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time
import re
from datetime import datetime

print("="*80)
print(" DEMO: AGENTE IA INTELIGENTE SEACE - SEGMENTO 43")
print("="*80)

# Cargar configuración
with open('config_empresa.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

empresa = config['empresa']
print(f"\n🏢 Empresa: {empresa['nombre']}")
print(f"📋 Monitoreando con {len(empresa['palabras_clave_positivas'])} palabras clave")
print(f"💰 Rango ideal: S/. {empresa['montos_preferidos']['ideal_minimo']:,} - {empresa['montos_preferidos']['ideal_maximo']:,}")

print("\n🔍 Accediendo al SEACE...")

# Configurar navegador
options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Acceder al segmento 43
url = "https://prod4.seace.gob.pe/openegocio/#/lista/43"
driver.get(url)
print("⏳ Esperando carga de Angular...")
time.sleep(12)

# Obtener el texto de la página
body = driver.find_element(By.TAG_NAME, "body")
texto_completo = body.text

driver.quit()

# Buscar oportunidades en el texto
print("\n📊 ANALIZANDO OPORTUNIDADES...")
print("-"*80)

# Extraer bloques de oportunidades
bloques = re.split(r'(?=Entidad:\n)', texto_completo)

oportunidades_encontradas = []
for bloque in bloques:
    if len(bloque) > 100 and 'Nomenclatura:' in bloque:
        # Extraer datos
        datos = {}

        # Nomenclatura
        match = re.search(r'Nomenclatura:\n([^\n]+)', bloque)
        if match:
            datos['nomenclatura'] = match.group(1)

        # Entidad
        match = re.search(r'Entidad:\n([^\n]+)', bloque)
        if match:
            datos['entidad'] = match.group(1)

        # Descripción
        match = re.search(r'Descripción procedimiento:\n([^\n]+)', bloque)
        if match:
            datos['descripcion'] = match.group(1)

        # Fecha
        match = re.search(r'Fecha Fin[^\n]*:\n([^\n]+)', bloque)
        if match:
            datos['fecha_fin'] = match.group(1)

        if 'nomenclatura' in datos:
            oportunidades_encontradas.append(datos)

print(f"\n✅ {len(oportunidades_encontradas)} oportunidades encontradas en el segmento 43")

# Analizar compatibilidad con la empresa
print("\n🤖 EVALUANDO COMPATIBILIDAD CON TU EMPRESA...")
print("-"*80)

oportunidades_relevantes = []

for i, op in enumerate(oportunidades_encontradas[:10], 1):  # Analizar las primeras 10
    score = 0
    razones = []

    texto_op = f"{op.get('descripcion', '')} {op.get('entidad', '')}".lower()

    # Contar palabras clave positivas
    palabras_encontradas = []
    for palabra in empresa['palabras_clave_positivas']:
        if palabra.lower() in texto_op:
            palabras_encontradas.append(palabra)

    if palabras_encontradas:
        score += len(palabras_encontradas) * 10
        razones.append(f"✅ Palabras clave: {', '.join(palabras_encontradas[:5])}")

    # Verificar palabras negativas
    tiene_negativas = False
    for palabra in empresa['palabras_clave_negativas']:
        if palabra.lower() in texto_op:
            tiene_negativas = True
            score -= 30
            razones.append(f"⚠️ Contiene: {palabra}")
            break

    # Bonus por tipo de entidad
    for entidad_objetivo in empresa['entidades_objetivo']:
        if entidad_objetivo.lower() in op.get('entidad', '').lower():
            score += 20
            razones.append(f"✅ Entidad objetivo: {entidad_objetivo}")
            break

    # Guardar si es relevante
    if score > 50:
        oportunidades_relevantes.append({
            'oportunidad': op,
            'score': min(100, score),
            'razones': razones
        })

# Mostrar resultados
print(f"\n🎯 OPORTUNIDADES RELEVANTES PARA TU EMPRESA:")
print("="*80)

if oportunidades_relevantes:
    # Ordenar por score
    oportunidades_relevantes.sort(key=lambda x: x['score'], reverse=True)

    for i, item in enumerate(oportunidades_relevantes[:5], 1):
        op = item['oportunidad']
        print(f"\n{i}. {op.get('nomenclatura', 'Sin código')}")
        print(f"   Entidad: {op.get('entidad', 'N/A')}")
        print(f"   Descripción: {op.get('descripcion', 'N/A')[:80]}...")
        print(f"   Fecha límite: {op.get('fecha_fin', 'N/A')}")
        print(f"   \n   📊 COMPATIBILIDAD: {item['score']}%")
        for razon in item['razones']:
            print(f"   {razon}")
        print("-"*80)

    print(f"\n💡 RECOMENDACIÓN:")
    print(f"   Se encontraron {len(oportunidades_relevantes)} oportunidades compatibles")
    print(f"   Las de mayor puntaje (>80%) requieren ACCIÓN INMEDIATA")

else:
    print("\n⚠️ No se encontraron oportunidades altamente compatibles en este momento")
    print("   El agente seguirá monitoreando cada 30 minutos")

print("\n📧 Las alertas se enviarían a: " + config['notificaciones']['email'])
print("\n✅ DEMO COMPLETADA - El agente completo monitorea 24/7")
print("="*80)