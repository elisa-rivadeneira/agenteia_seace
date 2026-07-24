#!/usr/bin/env python3
"""
Extractor SEACE - API TIEMPO REAL
Usa el endpoint oficial de SEACE que NO está bloqueado
"""

import requests
import json
from datetime import datetime

def extraer_oportunidades_realtime():
    """
    Extrae oportunidades EN TIEMPO REAL desde el API oficial de SEACE
    """
    print("="*80)
    print(" EXTRACTOR SEACE - TIEMPO REAL (API OFICIAL)")
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

    print("\n🌐 Consultando API oficial de SEACE...")

    # API oficial de SEACE para segmento 43 (Tecnologías)
    url = "https://prod4.seace.gob.pe:8086/api/oportunidades/listaProcesosCubso/codigoSegmento/43"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://prod4.seace.gob.pe/openegocio/'
    }

    try:
        print(f"📡 Conectando a: {url}")

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return crear_resultado_vacio()

        # Parsear JSON
        data = response.json()
        print(f"✅ Datos recibidos: {len(data)} oportunidades")

        # Procesar oportunidades
        oportunidades = []

        for idx, item in enumerate(data):
            nomenclatura = item.get('nomenclatura', '')
            oportunidad = {
                "numero": idx + 1,
                "nomenclatura": nomenclatura,
                "entidad": item.get('detEntidad', ''),
                "tipo_proceso": item.get('detTipoProceso', ''),
                "modalidad": item.get('detModalidadSeleccion', ''),
                "num_proceso": item.get('numProceso', ''),
                "anho": item.get('anhoProceso', ''),
                "objeto": item.get('detObjeto', ''),
                "descripcion_item": item.get('detItem', ''),
                "sintesis": item.get('sintesisProceso', ''),
                "valor_referencial": item.get('valorReferencialItem', '---'),
                "moneda": item.get('detMonedaItem', ''),
                "cantidad": item.get('cantItem', ''),
                "unidad_medida": item.get('detUnidadMedida', ''),
                "fecha_convocatoria": item.get('fechaConvocatoria', ''),
                "fecha_inicio": item.get('fechaInicio', ''),
                "fecha_fin": item.get('fechaFin', ''),
                "fecha_presentacion": item.get('fechaPresentacionPropuestas', ''),
                "ubigeo": item.get('ubigeo', ''),
                "version_seace": item.get('versionSeace', ''),
                "cubso_codigo": item.get('codCubso', ''),
                "cubso_descripcion": item.get('detCubso', ''),
                "url_seace": f"https://prod4.seace.gob.pe/openegocio/#/busqueda-por-item?numeroProcesoItem={nomenclatura}" if nomenclatura else "",
                "fecha_extraccion": datetime.now().isoformat()
            }

            # Calcular score de compatibilidad
            if config and empresa:
                texto_completo = f"{oportunidad['descripcion_item']} {oportunidad['sintesis']} {oportunidad['entidad']} {oportunidad['cubso_descripcion']}".lower()
                score = 0
                razones = []

                # Palabras positivas
                for palabra in empresa.get('palabras_clave_positivas', []):
                    if palabra.lower() in texto_completo:
                        score += 5
                        razones.append(f"+{palabra}")

                # Palabras negativas
                for palabra in empresa.get('palabras_clave_negativas', []):
                    if palabra.lower() in texto_completo:
                        score -= 10
                        razones.append(f"-{palabra}")

                oportunidad['score_compatibilidad'] = max(0, min(100, score))
                oportunidad['razones'] = razones[:5]
            else:
                oportunidad['score_compatibilidad'] = 0
                oportunidad['razones'] = []

            oportunidades.append(oportunidad)

        # Ordenar por score
        oportunidades.sort(key=lambda x: x.get('score_compatibilidad', 0), reverse=True)

        # Crear resultado
        resultado = {
            "fecha_extraccion": datetime.now().isoformat(),
            "fuente": "SEACE API Tiempo Real",
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

        if config:
            altamente_compatibles = [op for op in oportunidades if op.get('score_compatibilidad', 0) >= 70]
            compatibles = [op for op in oportunidades if 50 <= op.get('score_compatibilidad', 0) < 70]

            print(f"\n🎯 ANÁLISIS DE COMPATIBILIDAD:")
            print(f"  🌟 Altamente compatibles (≥70%): {len(altamente_compatibles)}")
            print(f"  ✅ Compatibles (50-69%): {len(compatibles)}")
            print(f"  ⚠️ Baja compatibilidad (<50%): {len(oportunidades) - len(altamente_compatibles) - len(compatibles)}")

            if altamente_compatibles:
                print(f"\n🏆 TOP 3 MÁS COMPATIBLES:")
                for i, op in enumerate(altamente_compatibles[:3], 1):
                    print(f"  {i}. {op['entidad'][:40]}...")
                    print(f"     Score: {op['score_compatibilidad']}% | {op['nomenclatura']}")
                    print(f"     Cierra: {op['fecha_fin']}")

        return resultado

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return crear_resultado_vacio()

def crear_resultado_vacio():
    """Crea resultado vacío en caso de error"""
    resultado = {
        "fecha_extraccion": datetime.now().isoformat(),
        "fuente": "SEACE API Tiempo Real (Error)",
        "segmento": "43",
        "total_oportunidades": 0,
        "oportunidades": []
    }

    filename = f"seace_todas_oportunidades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado

if __name__ == "__main__":
    resultado = extraer_oportunidades_realtime()
    print("\n✅ Proceso completado")
