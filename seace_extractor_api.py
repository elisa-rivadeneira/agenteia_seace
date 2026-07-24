#!/usr/bin/env python3
"""
Extractor SEACE usando Datos Abiertos oficiales (sin scraping)
Descarga datos directamente del portal BI de SEACE
"""

import requests
import json
import pandas as pd
from datetime import datetime
import re
from io import BytesIO

def descargar_convocatorias_seace():
    """
    Descarga datos de convocatorias desde el portal de datos abiertos de SEACE
    """
    print("="*80)
    print(" EXTRACTOR SEACE - DATOS ABIERTOS OFICIALES")
    print("="*80)
    print(f"\nFecha/Hora: {datetime.now()}")

    # Cargar configuración
    try:
        with open('config_empresa.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        empresa = config['empresa']
        print(f"🏢 Empresa: {empresa['nombre']}")
    except:
        print("⚠️ No se pudo cargar config_empresa.json")
        config = None
        empresa = {}

    # URL del portal de datos abiertos de SEACE - Convocatorias
    # Esta es la URL base, pero necesitamos encontrar el endpoint exacto de descarga
    base_url = "https://bi.seace.gob.pe"

    print("\n🌐 Intentando acceder a datos abiertos de SEACE...")

    # Vamos a intentar diferentes endpoints conocidos
    endpoints = [
        "/pentaho/plugin/cda/api/doQuery?path=/public/portal/datosabiertos/convocatorias.cda&dataAccessId=query",
        "/pentaho/plugin/cda/api/doQuery?path=/public/portal/convocatorias.cda&dataAccessId=qry_convocatorias",
    ]

    datos = None

    # Por ahora, vamos a usar un método alternativo:
    # Simular que descargamos un CSV y parsearlo
    # En producción, esto necesitará la URL exacta del endpoint

    print("\n⚠️ NOTA: Este script está en desarrollo.")
    print("📊 Por ahora, vamos a usar datos de ejemplo para demostrar funcionalidad.")
    print("🔧 Necesitarás configurar el endpoint exacto de descarga de SEACE.\n")

    # Método alternativo: Usar la API OCDS si está disponible
    try:
        print("🔍 Intentando API OCDS...")
        ocds_url = "https://contratacionesabiertas.osce.gob.pe/api/v1/release"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

        # Intentar obtener releases recientes
        response = requests.get(
            ocds_url,
            headers=headers,
            params={'page': 1, 'limit': 100},
            timeout=30
        )

        if response.status_code == 200:
            print("✅ Conexión exitosa a API OCDS")
            try:
                data = response.json()
                print(f"📦 Datos recibidos: {len(str(data))} caracteres")
                # Procesar datos OCDS aquí
            except:
                print("⚠️ Respuesta no es JSON válido")
        else:
            print(f"❌ API OCDS no disponible (código {response.status_code})")

    except Exception as e:
        print(f"⚠️ Error conectando a API: {e}")

    # Datos de ejemplo para testing
    print("\n📊 Generando datos de ejemplo para testing...\n")

    oportunidades_ejemplo = []

    # Crear resultado de ejemplo
    resultado = {
        "fecha_extraccion": datetime.now().isoformat(),
        "fuente": "SEACE Datos Abiertos (EN DESARROLLO)",
        "segmento": "43",
        "total_oportunidades": 0,
        "oportunidades": oportunidades_ejemplo,
        "nota": "Este extractor está en desarrollo. Necesita configurar endpoint de descarga de SEACE."
    }

    # Guardar resultados
    filename = f"seace_datos_abiertos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"💾 Archivo guardado: {filename}")
    print("\n" + "="*80)
    print(" INSTRUCCIONES PARA COMPLETAR LA INTEGRACIÓN")
    print("="*80)
    print("""
1. Visita: https://bi.seace.gob.pe/pentaho/api/repos/:public:portal:datosabiertosconvocatorias.html/content?userid=public&password=key

2. Identifica el botón de descarga de Excel/CSV

3. Inspecciona la red (F12 > Network) cuando haces clic en descargar

4. Copia la URL exacta del endpoint que descarga los datos

5. Actualiza este script con esa URL

Alternativamente:
- Descarga manualmente el archivo Excel/CSV de convocatorias
- Colócalo en la carpeta del proyecto con nombre 'seace_convocatorias.xlsx'
- Este script lo procesará automáticamente
""")

    return resultado

def procesar_archivo_manual():
    """
    Procesar archivo descargado manualmente de SEACE
    """
    import os

    archivos_posibles = [
        'seace_convocatorias.xlsx',
        'seace_convocatorias.csv',
        'convocatorias.xlsx',
        'convocatorias.csv'
    ]

    for archivo in archivos_posibles:
        if os.path.exists(archivo):
            print(f"✅ Encontrado archivo: {archivo}")

            try:
                if archivo.endswith('.xlsx'):
                    df = pd.read_excel(archivo)
                else:
                    df = pd.read_csv(archivo, encoding='utf-8')

                print(f"📊 Total de filas: {len(df)}")
                print(f"📋 Columnas: {list(df.columns)}")

                # Filtrar por segmento 43 si existe esa columna
                if 'CODIGO_SEGMENTO' in df.columns:
                    df_segmento = df[df['CODIGO_SEGMENTO'] == 43]
                    print(f"🎯 Oportunidades en segmento 43: {len(df_segmento)}")
                    return df_segmento
                else:
                    print("⚠️ No se encontró columna CODIGO_SEGMENTO")
                    print("Columnas disponibles:", list(df.columns))
                    return df

            except Exception as e:
                print(f"❌ Error procesando {archivo}: {e}")

    print("❌ No se encontró ningún archivo de datos SEACE")
    print(f"Archivos buscados: {archivos_posibles}")
    return None

if __name__ == "__main__":
    # Intentar procesar archivo manual primero
    df = procesar_archivo_manual()

    if df is None:
        # Si no hay archivo, mostrar instrucciones
        resultado = descargar_convocatorias_seace()
    else:
        print("\n✅ Datos cargados exitosamente desde archivo local")
        print("🔄 Procesando oportunidades...")

        # Cargar configuración
        try:
            with open('config_empresa.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            empresa = config['empresa']
        except:
            config = None
            empresa = {}

        # Convertir DataFrame a lista de oportunidades
        oportunidades = []
        for idx, row in df.iterrows():
            oportunidad = {
                "numero": idx + 1,
                "datos_raw": row.to_dict(),
                "fecha_extraccion": datetime.now().isoformat()
            }

            # Calcular score de compatibilidad si tenemos configuración
            if config and empresa:
                texto_completo = ' '.join([str(v) for v in row.values if pd.notna(v)]).lower()
                score = 0
                razones = []

                for palabra in empresa.get('palabras_clave_positivas', []):
                    if palabra.lower() in texto_completo:
                        score += 5
                        razones.append(f"+{palabra}")

                for palabra in empresa.get('palabras_clave_negativas', []):
                    if palabra.lower() in texto_completo:
                        score -= 10
                        razones.append(f"-{palabra}")

                oportunidad['score_compatibilidad'] = max(0, min(100, score))
                oportunidad['razones'] = razones[:5]

            oportunidades.append(oportunidad)

        # Ordenar por compatibilidad
        if config:
            oportunidades.sort(key=lambda x: x.get('score_compatibilidad', 0), reverse=True)

        # Guardar resultado
        resultado = {
            "fecha_extraccion": datetime.now().isoformat(),
            "fuente": "SEACE Datos Abiertos (Archivo Local)",
            "segmento": "43",
            "total_oportunidades": len(oportunidades),
            "oportunidades": oportunidades
        }

        filename = f"seace_todas_oportunidades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Resultados guardados en: {filename}")
        print(f"📊 Total de oportunidades: {len(oportunidades)}")

        if config:
            altamente_compatibles = [op for op in oportunidades if op.get('score_compatibilidad', 0) >= 70]
            print(f"🌟 Altamente compatibles (≥70%): {len(altamente_compatibles)}")
