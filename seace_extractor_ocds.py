#!/usr/bin/env python3
"""
Extractor SEACE usando API OCDS
Consulta directamente el portal de Contrataciones Abiertas de OSCE
"""

import requests
import json
from datetime import datetime, timedelta
import time
import zipfile
from io import BytesIO

def crear_resultado_vacio():
    """Crea un resultado vacío en caso de error"""
    return {
        "fecha_extraccion": datetime.now().isoformat(),
        "fuente": "OCDS API OECE (Error)",
        "segmento": "43",
        "total_oportunidades": 0,
        "oportunidades": []
    }

def extraer_oportunidades_ocds():
    """
    Extrae oportunidades usando el portal OCDS de OECE
    Descarga archivo JSON del mes actual
    """
    print("="*80)
    print(" EXTRACTOR SEACE - API OCDS OECE")
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

    print("\n🌐 Consultando API OCDS OECE...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'es-PE,es;q=0.9'
    }

    base_url = "https://contratacionesabiertas.oece.gob.pe"

    # Paso 1: Obtener lista de archivos disponibles
    print(f"\n📂 Obteniendo lista de archivos disponibles...")

    try:
        response = requests.get(
            f"{base_url}/api/v1/files?format=json",
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Error obteniendo lista: {response.status_code}")
            return crear_resultado_vacio()

        files_data = response.json()
        results = files_data.get('results', [])

        if not results:
            print("❌ No hay archivos disponibles")
            return crear_resultado_vacio()

        # Obtener archivo más reciente (primer resultado)
        latest = results[0]
        print(f"✅ Archivo más reciente: {latest['id']}")
        print(f"   Fuente: {latest['source']}")
        print(f"   Mes: {latest['monthName']} {latest['year']}")
        print(f"   Actualizado: {latest['timestamp']}")

        # Paso 2: Descargar archivo JSON
        json_url = latest['files']['json']
        print(f"\n📥 Descargando archivo JSON...")
        print(f"   URL: {json_url}")

        response = requests.get(
            json_url,
            headers=headers,
            timeout=300,  # 5 minutos para descargas grandes
            stream=True
        )

        if response.status_code != 200:
            print(f"❌ Error descargando: {response.status_code}")
            return crear_resultado_vacio()

        print(f"✅ Descarga exitosa ({len(response.content)} bytes)")

        # Paso 3: Descomprimir ZIP
        print(f"\n📦 Descomprimiendo archivo ZIP...")

        with zipfile.ZipFile(BytesIO(response.content)) as z:
            # Listar archivos en el ZIP
            files_in_zip = z.namelist()
            print(f"   Archivos en ZIP: {files_in_zip}")

            # Buscar el archivo JSON principal
            json_file = None
            for fname in files_in_zip:
                if fname.endswith('.json') and 'record' in fname.lower():
                    json_file = fname
                    break

            if not json_file:
                # Tomar el primer JSON
                json_file = [f for f in files_in_zip if f.endswith('.json')][0]

            print(f"   Leyendo: {json_file}")

            # Leer JSON
            with z.open(json_file) as f:
                data = json.load(f)

        # El archivo es un record package o release package
        if 'records' in data:
            records = data['records']
            print(f"📦 Records encontrados: {len(records)}")
            oportunidades = procesar_records(records, empresa)
        elif 'releases' in data:
            releases = data['releases']
            print(f"📦 Releases encontrados: {len(releases)}")
            oportunidades = procesar_releases(releases, empresa)
        else:
            print(f"⚠️ Formato no reconocido. Keys: {list(data.keys())[:10]}")
            return crear_resultado_vacio()

    except Exception as e:
        print(f"❌ Error en extracción: {e}")
        import traceback
        traceback.print_exc()
        return crear_resultado_vacio()

    # Crear resultado final
    resultado = {
        "fecha_extraccion": datetime.now().isoformat(),
        "fuente": "OCDS API - contratacionesabiertas.osce.gob.pe",
        "segmento": "43",
        "total_oportunidades": len(oportunidades),
        "oportunidades": oportunidades
    }

    # Guardar
    filename = f"seace_todas_oportunidades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Resultado guardado: {filename}")
    print(f"📊 Total oportunidades: {len(oportunidades)}")

    if oportunidades and config:
        altamente_compatibles = [op for op in oportunidades if op.get('score_compatibilidad', 0) >= 70]
        print(f"🌟 Altamente compatibles (≥70%): {len(altamente_compatibles)}")

    return resultado

def procesar_releases(releases, empresa):
    """
    Procesa releases del formato OCDS
    """
    oportunidades = []

    for idx, release in enumerate(releases):
        try:
            # Extraer información básica del release
            tender = release.get('tender', {})
            buyer = release.get('buyer', {})

            # Filtrar por segmento 43 si tiene clasificación CPV o similar
            items = tender.get('items', [])
            es_segmento_43 = False

            for item in items:
                clasificacion = item.get('classification', {})
                # Verificar si es tecnología (segmento 43)
                if any(keyword in str(clasificacion).lower() for keyword in ['software', 'hardware', 'tecnolog', 'informatic', 'compute']):
                    es_segmento_43 = True
                    break

            if not es_segmento_43:
                continue  # Saltar si no es tecnología

            # Crear oportunidad
            oportunidad = {
                "numero": len(oportunidades) + 1,
                "id_ocds": release.get('ocid', ''),
                "titulo": tender.get('title', 'Sin título'),
                "descripcion": tender.get('description', ''),
                "entidad": buyer.get('name', 'N/A'),
                "valor_estimado": tender.get('value', {}).get('amount', 0),
                "moneda": tender.get('value', {}).get('currency', 'PEN'),
                "fecha_publicacion": release.get('date', ''),
                "fecha_cierre": tender.get('tenderPeriod', {}).get('endDate', ''),
                "items": items,
                "fecha_extraccion": datetime.now().isoformat()
            }

            # Calcular score de compatibilidad
            if empresa:
                texto_completo = f"{oportunidad['titulo']} {oportunidad['descripcion']}".lower()
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

        except Exception as e:
            print(f"  ⚠️ Error procesando release {idx}: {str(e)[:50]}")
            continue

    # Ordenar por score
    oportunidades.sort(key=lambda x: x.get('score_compatibilidad', 0), reverse=True)

    return oportunidades

def procesar_records(records, empresa):
    """
    Procesa records del formato OCDS
    Records contienen releases compilados
    """
    oportunidades = []

    for record in records:
        # Un record puede tener múltiples releases
        # Usar el compiledRelease que es el estado actual
        release = record.get('compiledRelease', record.get('releases', [{}])[0] if record.get('releases') else {})

        # Procesar como release individual
        ops = procesar_releases([release], empresa)
        oportunidades.extend(ops)

    return oportunidades

if __name__ == "__main__":
    resultado = extraer_oportunidades_ocds()
    print("\n✅ Proceso completado")
