"""
Herramientas de base de datos para el agente IA
Permite al agente consultar y modificar la configuración del usuario
"""

# Banner de versión para verificar que el código esté actualizado
print("🔧 AGENTE_DB_TOOLS.PY - VERSION 2026-08-11 10:00 - Fix consultar_configuracion_alertas")

from database_mysql import (
    obtener_usuario_por_numero,
    obtener_segmentos_usuario,
    obtener_configuracion_usuario_por_id,
    obtener_empresa_usuario_por_id,
    configurar_segmentos_usuario_por_id,
    actualizar_empresa_usuario,
    actualizar_configuracion_usuario,
    obtener_nombre_segmento
)
import json
import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Cliente OpenAI para embeddings
_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            _openai_client = OpenAI(api_key=api_key)
    return _openai_client

def obtener_catalogo_segmentos():
    """
    Obtiene el catálogo completo de segmentos SEACE

    Returns:
        dict con todos los segmentos disponibles
    """
    try:
        # Intentar cargar desde static/segmentos_seace.json
        ruta = 'static/segmentos_seace.json'
        if not os.path.exists(ruta):
            ruta = '/app/static/segmentos_seace.json'

        with open(ruta, 'r', encoding='utf-8') as f:
            catalogo_array = json.load(f)

        # Convertir array a dict para facilitar búsqueda
        catalogo_dict = {seg['codigo']: seg['nombre'] for seg in catalogo_array}

        return {
            "total_segmentos": len(catalogo_dict),
            "segmentos": catalogo_dict
        }
    except Exception as e:
        return {"error": f"No se pudo cargar el catálogo: {str(e)}"}

def buscar_segmento_por_codigo(codigo):
    """
    Busca un segmento SEACE específico por su código

    Args:
        codigo: Código del segmento (ej: "43", "77", "86")

    Returns:
        dict con información del segmento
    """
    try:
        catalogo_result = obtener_catalogo_segmentos()
        if "error" in catalogo_result:
            return catalogo_result

        catalogo = catalogo_result["segmentos"]
        codigo_str = str(codigo)

        if codigo_str in catalogo:
            return {
                "encontrado": True,
                "codigo": codigo_str,
                "nombre": catalogo[codigo_str]
            }
        else:
            return {
                "encontrado": False,
                "codigo": codigo_str,
                "mensaje": f"No se encontró el segmento {codigo_str}"
            }
    except Exception as e:
        return {"error": f"Error en búsqueda: {str(e)}"}

def buscar_segmentos_semanticamente(consulta_usuario, top_k=5):
    """
    Búsqueda semántica de segmentos usando embeddings de OpenAI
    Tolera errores de escritura y entiende sinónimos

    Si OpenAI no está disponible, hace fallback a búsqueda literal por palabra

    Args:
        consulta_usuario: Consulta en lenguaje natural (ej: "capacitaciones", "capcitaciones", "educar")
        top_k: Número máximo de resultados más similares (default: 5)

    Returns:
        dict con segmentos más similares y sus scores de similitud
    """
    try:
        client = get_openai_client()
        if not client:
            # Fallback a búsqueda literal si OpenAI no disponible
            print("⚠️ OpenAI no disponible, usando búsqueda literal como fallback")
            return buscar_segmentos_por_palabra(consulta_usuario)

        # Cargar catálogo
        catalogo_result = obtener_catalogo_segmentos()
        if "error" in catalogo_result:
            return catalogo_result

        catalogo = catalogo_result["segmentos"]

        # Generar embedding de la consulta
        consulta_embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=consulta_usuario
        )
        consulta_embedding = np.array(consulta_embedding_response.data[0].embedding)

        # Generar embeddings de todos los segmentos
        textos_segmentos = [f"{codigo}: {nombre}" for codigo, nombre in catalogo.items()]

        segmentos_embeddings_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=textos_segmentos
        )

        # Calcular similitud coseno
        resultados = []
        for i, (codigo, nombre) in enumerate(catalogo.items()):
            segmento_embedding = np.array(segmentos_embeddings_response.data[i].embedding)

            # Similitud coseno
            similitud = np.dot(consulta_embedding, segmento_embedding) / (
                np.linalg.norm(consulta_embedding) * np.linalg.norm(segmento_embedding)
            )

            resultados.append({
                "codigo": codigo,
                "nombre": nombre,
                "similitud": float(similitud)
            })

        # Ordenar por similitud descendente
        resultados.sort(key=lambda x: x["similitud"], reverse=True)

        # Tomar top_k más relevantes (similitud > 0.35 para capturar errores de escritura y sinónimos)
        resultados_filtrados = [r for r in resultados[:top_k] if r["similitud"] > 0.35]

        # Si no encuentra nada con similitud semántica, hacer fallback a búsqueda literal
        if not resultados_filtrados:
            print("⚠️ Similitud muy baja, intentando búsqueda literal como fallback")
            return buscar_segmentos_por_palabra(consulta_usuario)

        return {
            "consulta": consulta_usuario,
            "total_encontrados": len(resultados_filtrados),
            "segmentos_encontrados": {
                r["codigo"]: f"{r['nombre']} (similitud: {r['similitud']:.2%})"
                for r in resultados_filtrados
            }
        }

    except Exception as e:
        # Fallback a búsqueda literal si hay error
        print(f"⚠️ Error en búsqueda semántica: {e}, usando búsqueda literal como fallback")
        return buscar_segmentos_por_palabra(consulta_usuario)

def buscar_segmentos_por_palabra(palabra_clave):
    """
    Busca segmentos SEACE que contengan una palabra clave

    Args:
        palabra_clave: Palabra a buscar (ej: "programación", "salud", "construcción")

    Returns:
        dict con segmentos que coinciden
    """
    try:
        import unicodedata

        def normalizar_texto(texto):
            """Normaliza texto removiendo acentos y convirtiendo a minúsculas"""
            texto = texto.lower()
            # Remover acentos
            texto = unicodedata.normalize('NFD', texto)
            texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
            return texto

        def singularizar(palabra):
            """Intenta convertir plural a singular (español básico)"""
            if len(palabra) > 3 and palabra.endswith('es'):
                return palabra[:-2]
            elif len(palabra) > 2 and palabra.endswith('s'):
                return palabra[:-1]
            return palabra

        catalogo_result = obtener_catalogo_segmentos()
        if "error" in catalogo_result:
            return catalogo_result

        catalogo = catalogo_result["segmentos"]
        palabra_normalizada = normalizar_texto(palabra_clave)
        palabra_singular = singularizar(palabra_normalizada)

        resultados = {}
        for codigo, descripcion in catalogo.items():
            descripcion_normalizada = normalizar_texto(descripcion)
            # Buscar tanto el plural como el singular
            if (palabra_normalizada in descripcion_normalizada or
                palabra_singular in descripcion_normalizada):
                resultados[codigo] = descripcion

        return {
            "palabra_buscada": palabra_clave,
            "total_encontrados": len(resultados),
            "segmentos_encontrados": resultados
        }
    except Exception as e:
        return {"error": f"Error en búsqueda: {str(e)}"}

def obtener_perfil_completo(numero_telefono):
    """
    Obtiene toda la información del usuario: datos básicos, empresa, segmentos y configuración

    Args:
        numero_telefono: Número de WhatsApp (ej: "51967717179")

    Returns:
        dict con toda la información del usuario
    """
    # Normalizar número
    if numero_telefono.startswith('+'):
        numero_telefono = numero_telefono[1:]
    if '@' in numero_telefono:
        numero_telefono = numero_telefono.split('@')[0]

    usuario = obtener_usuario_por_numero(numero_telefono)
    if not usuario:
        return {
            "error": "Usuario no encontrado",
            "registrado": False,
            "numero": numero_telefono
        }

    empresa = obtener_empresa_usuario_por_id(usuario['id'])
    segmentos = obtener_segmentos_usuario(usuario['id'])
    configuracion = obtener_configuracion_usuario_por_id(usuario['id'])

    return {
        "registrado": True,
        "usuario": {
            "nombre": usuario.get('nombre'),
            "email": usuario.get('email'),
            "activo": usuario.get('activo', True),
            "numero": numero_telefono
        },
        "empresa": empresa,
        "segmentos": segmentos,
        "configuracion": configuracion
    }

def consultar_segmentos_usuario(numero_telefono):
    """
    Consulta los segmentos SEACE configurados para el usuario

    Args:
        numero_telefono: Número de WhatsApp

    Returns:
        dict con lista de segmentos activos
    """
    if numero_telefono.startswith('+'):
        numero_telefono = numero_telefono[1:]
    if '@' in numero_telefono:
        numero_telefono = numero_telefono.split('@')[0]

    usuario = obtener_usuario_por_numero(numero_telefono)
    if not usuario:
        return {"error": "Usuario no encontrado"}

    segmentos = obtener_segmentos_usuario(usuario['id'])

    # Agregar nombres de segmentos
    segmentos_con_nombres = []
    for codigo in segmentos:
        segmentos_con_nombres.append({
            "codigo": codigo,
            "nombre": obtener_nombre_segmento(codigo)
        })

    return {
        "segmentos": segmentos,  # Solo códigos para retrocompatibilidad
        "segmentos_detalle": segmentos_con_nombres,  # Códigos con nombres
        "total": len(segmentos)
    }

def consultar_empresa_usuario(numero_telefono):
    """
    Consulta la información de empresa del usuario

    Args:
        numero_telefono: Número de WhatsApp

    Returns:
        dict con datos de la empresa
    """
    if numero_telefono.startswith('+'):
        numero_telefono = numero_telefono[1:]
    if '@' in numero_telefono:
        numero_telefono = numero_telefono.split('@')[0]

    usuario = obtener_usuario_por_numero(numero_telefono)
    if not usuario:
        return {"error": "Usuario no encontrado"}

    empresa = obtener_empresa_usuario(usuario['id'])
    return empresa

def consultar_configuracion_alertas(numero_telefono):
    """
    Consulta la configuración de alertas del usuario

    Args:
        numero_telefono: Número de WhatsApp

    Returns:
        dict con configuración de alertas
    """
    if numero_telefono.startswith('+'):
        numero_telefono = numero_telefono[1:]
    if '@' in numero_telefono:
        numero_telefono = numero_telefono.split('@')[0]

    usuario = obtener_usuario_por_numero(numero_telefono)
    if not usuario:
        return {"error": "Usuario no encontrado"}

    config = obtener_configuracion_usuario_por_id(usuario['id'])
    return config if config else {"error": "Configuración no encontrada"}

def agregar_segmentos(numero_telefono, segmentos_a_agregar):
    """
    AGREGA segmentos a los que ya tiene el usuario (NO reemplaza)

    Args:
        numero_telefono: Número de WhatsApp
        segmentos_a_agregar: Lista de segmentos a agregar (ej: ["86", "90"])

    Returns:
        dict con resultado de la operación
    """
    if numero_telefono.startswith('+'):
        numero_telefono = numero_telefono[1:]
    if '@' in numero_telefono:
        numero_telefono = numero_telefono.split('@')[0]

    usuario = obtener_usuario_por_numero(numero_telefono)
    if not usuario:
        return {"error": "Usuario no encontrado", "exito": False}

    try:
        # Convertir a lista si viene como string
        if isinstance(segmentos_a_agregar, str):
            segmentos_a_agregar = [s.strip() for s in segmentos_a_agregar.split(',')]

        # Obtener segmentos actuales
        segmentos_actuales = obtener_segmentos_usuario(usuario['id'])

        # Agregar nuevos segmentos sin duplicar
        segmentos_finales = list(set(segmentos_actuales + segmentos_a_agregar))

        # Actualizar en BD
        exito = configurar_segmentos_usuario_por_id(usuario['id'], segmentos_finales)

        return {
            "exito": exito,
            "segmentos_anteriores": segmentos_actuales,
            "segmentos_agregados": segmentos_a_agregar,
            "segmentos_finales": segmentos_finales,
            "mensaje": f"Segmentos agregados correctamente. Ahora tienes {len(segmentos_finales)} segmentos activos." if exito else "Error al agregar segmentos"
        }
    except Exception as e:
        return {"error": str(e), "exito": False}

def modificar_segmentos(numero_telefono, segmentos_nuevos):
    """
    REEMPLAZA todos los segmentos del usuario (borra los anteriores)
    Si quieres agregar sin borrar, usa agregar_segmentos()

    Args:
        numero_telefono: Número de WhatsApp
        segmentos_nuevos: Lista completa de segmentos (ej: ["43", "45", "52"])

    Returns:
        dict con resultado de la operación
    """
    if numero_telefono.startswith('+'):
        numero_telefono = numero_telefono[1:]
    if '@' in numero_telefono:
        numero_telefono = numero_telefono.split('@')[0]

    usuario = obtener_usuario_por_numero(numero_telefono)
    if not usuario:
        return {"error": "Usuario no encontrado", "exito": False}

    try:
        # Convertir a lista si viene como string
        if isinstance(segmentos_nuevos, str):
            segmentos_nuevos = [s.strip() for s in segmentos_nuevos.split(',')]

        exito = configurar_segmentos_usuario_por_id(usuario['id'], segmentos_nuevos)
        return {
            "exito": exito,
            "segmentos_actualizados": segmentos_nuevos,
            "mensaje": "Segmentos actualizados correctamente" if exito else "Error al actualizar segmentos"
        }
    except Exception as e:
        return {"error": str(e), "exito": False}

def modificar_empresa(numero_telefono, nombre_empresa=None, palabras_clave=None):
    """
    Modifica la información de empresa del usuario

    Args:
        numero_telefono: Número de WhatsApp
        nombre_empresa: Nombre de la empresa (opcional)
        palabras_clave: Dict con palabras_positivas y palabras_negativas (opcional)

    Returns:
        dict con resultado de la operación
    """
    if numero_telefono.startswith('+'):
        numero_telefono = numero_telefono[1:]
    if '@' in numero_telefono:
        numero_telefono = numero_telefono.split('@')[0]

    usuario = obtener_usuario_por_numero(numero_telefono)
    if not usuario:
        return {"error": "Usuario no encontrado", "exito": False}

    try:
        exito = actualizar_empresa_usuario(
            usuario['id'],
            nombre_empresa=nombre_empresa,
            palabras_clave=palabras_clave
        )
        return {
            "exito": exito,
            "mensaje": "Empresa actualizada correctamente" if exito else "Error al actualizar empresa"
        }
    except Exception as e:
        return {"error": str(e), "exito": False}

def modificar_configuracion_alertas(numero_telefono, **kwargs):
    """
    Modifica la configuración de alertas del usuario

    Args:
        numero_telefono: Número de WhatsApp
        **kwargs: Parámetros de configuración (alertas_realtime_activas, horarios_alertas, etc.)

    Returns:
        dict con resultado de la operación
    """
    if numero_telefono.startswith('+'):
        numero_telefono = numero_telefono[1:]
    if '@' in numero_telefono:
        numero_telefono = numero_telefono.split('@')[0]

    usuario = obtener_usuario_por_numero(numero_telefono)
    if not usuario:
        return {"error": "Usuario no encontrado", "exito": False}

    try:
        exito = actualizar_configuracion_usuario(usuario['id'], **kwargs)
        return {
            "exito": exito,
            "configuracion_actualizada": kwargs,
            "mensaje": "Configuración actualizada correctamente" if exito else "Error al actualizar configuración"
        }
    except Exception as e:
        return {"error": str(e), "exito": False}

def extraer_oportunidades_seace(segmento, numero_telefono=None):
    """
    Extrae oportunidades de SEACE para un segmento específico

    Args:
        segmento: Código del segmento (ej: "43", "81", "86")
        numero_telefono: Número del usuario (opcional, para verificar permisos)

    Returns:
        dict con las oportunidades encontradas
    """
    try:
        # Verificar que el usuario tenga el segmento configurado
        if numero_telefono:
            if numero_telefono.startswith('+'):
                numero_telefono = numero_telefono[1:]
            if '@' in numero_telefono:
                numero_telefono = numero_telefono.split('@')[0]

            print(f"🔍 [extraer_oportunidades_seace] Número normalizado: {numero_telefono}")

            # Obtener usuario de MySQL primero
            usuario = obtener_usuario_por_numero(numero_telefono)
            print(f"🔍 [extraer_oportunidades_seace] Usuario obtenido: {usuario}")

            if not usuario:
                return {
                    "exito": False,
                    "error": "Usuario no encontrado. Registra tu número primero.",
                    "segmentos_usuario": []
                }

            # Obtener segmentos del usuario (database_mysql requiere usuario_id)
            segmentos_usuario = obtener_segmentos_usuario(usuario['id'])

            print(f"🔍 [extraer_oportunidades_seace] Segmentos obtenidos de MySQL: {segmentos_usuario}")
            print(f"🔍 [extraer_oportunidades_seace] Segmento solicitado: {segmento}")
            print(f"🔍 [extraer_oportunidades_seace] Segmento en lista? {segmento in segmentos_usuario}")

            if segmento not in segmentos_usuario:
                print(f"❌ [extraer_oportunidades_seace] Segmento {segmento} NO encontrado en {segmentos_usuario}")
                return {
                    "exito": False,
                    "error": f"El segmento {segmento} no está en tu configuración",
                    "segmentos_usuario": segmentos_usuario
                }

            print(f"✅ [extraer_oportunidades_seace] Segmento {segmento} verificado correctamente")

        # Importar y ejecutar el extractor
        from seace_extractor_realtime import extraer_oportunidades_realtime

        print(f"🔍 Extrayendo oportunidades del segmento {segmento}...")
        resultado = extraer_oportunidades_realtime(segmento)

        oportunidades = resultado.get('oportunidades', [])

        return {
            "exito": True,
            "segmento": segmento,
            "total_oportunidades": len(oportunidades),
            "oportunidades": oportunidades[:10],  # Solo las top 10 para no saturar
            "mensaje": f"✅ Encontradas {len(oportunidades)} oportunidades en el segmento {segmento}"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "exito": False,
            "error": f"Error al extraer oportunidades: {str(e)}"
        }

# Diccionario de funciones disponibles para el agente
HERRAMIENTAS_DB = {
    "obtener_catalogo_segmentos": obtener_catalogo_segmentos,
    "buscar_segmento_por_codigo": buscar_segmento_por_codigo,
    "buscar_segmentos_por_palabra": buscar_segmentos_por_palabra,
    "buscar_segmentos_semanticamente": buscar_segmentos_semanticamente,
    "obtener_perfil_completo": obtener_perfil_completo,
    "consultar_segmentos_usuario": consultar_segmentos_usuario,
    "consultar_empresa_usuario": consultar_empresa_usuario,
    "consultar_configuracion_alertas": consultar_configuracion_alertas,
    "agregar_segmentos": agregar_segmentos,
    "modificar_segmentos": modificar_segmentos,
    "modificar_empresa": modificar_empresa,
    "modificar_configuracion_alertas": modificar_configuracion_alertas,
    "extraer_oportunidades_seace": extraer_oportunidades_seace
}
