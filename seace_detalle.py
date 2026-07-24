#!/usr/bin/env python3
"""
Obtiene el detalle completo de una oportunidad SEACE
Incluyendo los items del procedimiento
"""
import requests
import json

def obtener_detalle_oportunidad(id_procedimiento):
    """
    Obtiene el detalle completo de una oportunidad SEACE

    Args:
        id_procedimiento (str): ID del procedimiento en SEACE

    Returns:
        dict: Diccionario con la información detallada o None si hay error
    """
    url = f"https://prod4.seace.gob.pe:8086/api/oportunidades/fichaProceso/idProceso/{id_procedimiento}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0',
        'Accept': 'application/json, text/plain, */*',
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return None

        data = response.json()

        # Extraer información relevante
        detalle = {
            "nomenclatura": data.get('nomenclatura', ''),
            "descripcion_objeto": data.get('descripcionObjeto', ''),
            "valor_referencial": data.get('valorReferencial', '---'),
            "tipo_objeto": data.get('tipoObjeto', ''),
            "modalidad_seleccion": data.get('modalidadSeleccion', ''),
            "items": []
        }

        # Extraer items del procedimiento
        lista_items = data.get('listaItems', [])
        for item in lista_items:
            item_info = {
                "nro_item": item.get('nroItem', ''),
                "descripcion": item.get('descripcion', ''),
                "descripcion_cubso": item.get('descripcionCubso', ''),
                "cantidad": item.get('cantidad', ''),
                "unidad_medida": item.get('unidadMedia', ''),
                "valor_referencial_total": item.get('valorReferencialTotal', '---'),
                "moneda": item.get('moneda', ''),
                "mype": item.get('mype', ''),
                "sistema_contratacion": item.get('sistemaContratacion', ''),
                "ubicacion": f"{item.get('distrito', '')}, {item.get('provincia', '')}, {item.get('departamento', '')}"
            }
            detalle["items"].append(item_info)

        return detalle

    except Exception as e:
        print(f"❌ Error obteniendo detalle: {e}")
        return None


if __name__ == "__main__":
    # Prueba
    id_test = "1231409"
    print(f"\n🔍 Obteniendo detalle del procedimiento {id_test}...\n")

    detalle = obtener_detalle_oportunidad(id_test)

    if detalle:
        print("=" * 80)
        print(f"Nomenclatura: {detalle['nomenclatura']}")
        print(f"Descripción: {detalle['descripcion_objeto'][:100]}...")
        print(f"Valor referencial: {detalle['valor_referencial']}")
        print(f"\nItems del procedimiento ({len(detalle['items'])}):")
        print("=" * 80)

        for item in detalle['items']:
            print(f"\nItem {item['nro_item']}: {item['descripcion']}")
            print(f"  Cantidad: {item['cantidad']} {item['unidad_medida']}")
            print(f"  CUBSO: {item['descripcion_cubso']}")
            print(f"  Valor: {item['valor_referencial_total']} {item['moneda']}")
            print(f"  Sistema: {item['sistema_contratacion']}")
    else:
        print("❌ No se pudo obtener el detalle")
