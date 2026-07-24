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

    print("\n🌐 Descargando datos desde portal SEACE...")

    # URLs posibles para descargar datos
    # Pentaho usa estos patrones para exportar datos
    urls_descarga = [
        # CDA (Community Data Access) - formato JSON/CSV
        "https://bi.seace.gob.pe/pentaho/plugin/cda/api/doQuery?path=/public/portal/convocatorias.cda&dataAccessId=query&outputType=json",
        # Endpoint alternativo
        "https://bi.seace.gob.pe/pentaho/content/reporting-application/reportviewer/report.html?solution=public&path=portal&name=convocatorias.prpt&output-target=table/excel;page-mode=page",
    ]

    datos = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-PE,es;q=0.9'
    }

    # Intentar descargar desde URLs conocidas
    for url in urls_descarga:
        try:
            print(f"🔄 Intentando: {url[:80]}...")
            response = requests.get(url, headers=headers, timeout=60, allow_redirects=True)

            print(f"   📊 Status: {response.status_code}")

            if response.status_code == 200:
                print(f"   ✅ Descarga exitosa ({len(response.content)} bytes)")

                # Intentar parsear según el tipo de contenido
                content_type = response.headers.get('Content-Type', '')

                if 'json' in content_type or url.endswith('json'):
                    try:
                        datos = response.json()
                        print(f"   📦 JSON parseado: {len(str(datos))} caracteres")
                        break
                    except:
                        print(f"   ⚠️ No es JSON válido")

                elif 'excel' in content_type or 'spreadsheet' in content_type:
                    try:
                        df = pd.read_excel(BytesIO(response.content))
                        print(f"   📊 Excel parseado: {len(df)} filas, {len(df.columns)} columnas")
                        datos = df
                        break
                    except Exception as e:
                        print(f"   ⚠️ Error parseando Excel: {e}")

                else:
                    # Intentar como CSV
                    try:
                        df = pd.read_csv(BytesIO(response.content))
                        print(f"   📊 CSV parseado: {len(df)} filas")
                        datos = df
                        break
                    except:
                        print(f"   ⚠️ No se pudo parsear como CSV")
            else:
                print(f"   ❌ Error {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            continue

    if datos is None:
        print("\n⚠️ No se pudo descargar automáticamente desde ninguna URL")
        print("📋 Opciones:")
        print("  1. Descarga manualmente desde: https://bi.seace.gob.pe/pentaho/api/repos/:public:portal:datosabiertosconvocatorias.html/content?userid=public&password=key")
        print("  2. Guarda el archivo como 'seace_convocatorias.xlsx' en el directorio del proyecto")
        print("  3. Ejecuta este script de nuevo")

    # Si se descargaron datos, procesarlos
    if datos is not None and isinstance(datos, pd.DataFrame):
        print(f"\n✅ Datos descargados: {len(datos)} registros")
        return procesar_dataframe(datos, config, empresa)
    else:
        # No se pudieron descargar datos
        resultado = {
            "fecha_extraccion": datetime.now().isoformat(),
            "fuente": "SEACE Datos Abiertos (Error de descarga)",
            "segmento": "43",
            "total_oportunidades": 0,
            "oportunidades": [],
            "error": "No se pudo descargar datos automáticamente. Ver logs para detalles."
        }

        filename = f"seace_datos_abiertos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Archivo de error guardado: {filename}")
        return resultado

def procesar_dataframe(df, config=None, empresa=None):
    """
    Procesa DataFrame de SEACE y genera archivo de oportunidades
    """
    print("\n🔄 Procesando datos...")
    print(f"📋 Columnas encontradas: {list(df.columns)[:10]}...")

    # Filtrar por segmento 43 si existe la columna
    if 'CODIGO_SEGMENTO' in df.columns:
        df_filtrado = df[df['CODIGO_SEGMENTO'] == 43]
        print(f"🎯 Oportunidades en segmento 43: {len(df_filtrado)}")
    elif 'CodigoSegmento' in df.columns:
        df_filtrado = df[df['CodigoSegmento'] == 43]
        print(f"🎯 Oportunidades en segmento 43: {len(df_filtrado)}")
    else:
        print("⚠️ No se encontró columna de segmento, usando todos los datos")
        df_filtrado = df

    # Convertir a lista de oportunidades
    oportunidades = []
    for idx, row in df_filtrado.iterrows():
        oportunidad = {
            "numero": idx + 1,
            "datos_raw": {k: str(v) if pd.notna(v) else "" for k, v in row.to_dict().items()},
            "fecha_extraccion": datetime.now().isoformat()
        }

        # Calcular score de compatibilidad
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
        else:
            oportunidad['score_compatibilidad'] = 0

        oportunidades.append(oportunidad)

    # Ordenar por compatibilidad
    oportunidades.sort(key=lambda x: x.get('score_compatibilidad', 0), reverse=True)

    # Guardar resultado
    resultado = {
        "fecha_extraccion": datetime.now().isoformat(),
        "fuente": "SEACE Datos Abiertos",
        "segmento": "43",
        "total_oportunidades": len(oportunidades),
        "oportunidades": oportunidades
    }

    filename = f"seace_todas_oportunidades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Resultados guardados: {filename}")
    print(f"📊 Total oportunidades: {len(oportunidades)}")

    if config:
        altamente_compatibles = [op for op in oportunidades if op.get('score_compatibilidad', 0) >= 70]
        print(f"🌟 Altamente compatibles (≥70%): {len(altamente_compatibles)}")

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
    # Cargar configuración
    try:
        with open('config_empresa.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        empresa = config['empresa']
    except:
        config = None
        empresa = {}

    # Intentar procesar archivo manual primero
    df = procesar_archivo_manual()

    if df is not None:
        print("\n✅ Datos cargados desde archivo local")
        resultado = procesar_dataframe(df, config, empresa)
    else:
        # Intentar descargar automáticamente
        resultado = descargar_convocatorias_seace()

    print("\n✅ Proceso completado")
