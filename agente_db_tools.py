"""
Herramientas de base de datos para el agente IA
Permite al agente consultar y modificar la configuración del usuario
"""

from database_mysql import (
    obtener_usuario_por_numero,
    obtener_segmentos_usuario,
    obtener_configuracion_usuario,
    obtener_empresa_usuario,
    configurar_segmentos_usuario,
    actualizar_empresa_usuario,
    actualizar_configuracion_usuario
)
import json
import os

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
            catalogo = json.load(f)

        return {
            "total_segmentos": len(catalogo),
            "segmentos": catalogo
        }
    except Exception as e:
        return {"error": f"No se pudo cargar el catálogo: {str(e)}"}

def buscar_segmentos_por_palabra(palabra_clave):
    """
    Busca segmentos SEACE que contengan una palabra clave

    Args:
        palabra_clave: Palabra a buscar (ej: "programación", "salud", "construcción")

    Returns:
        dict con segmentos que coinciden
    """
    try:
        catalogo_result = obtener_catalogo_segmentos()
        if "error" in catalogo_result:
            return catalogo_result

        catalogo = catalogo_result["segmentos"]
        palabra_lower = palabra_clave.lower()

        resultados = {}
        for codigo, descripcion in catalogo.items():
            if palabra_lower in descripcion.lower():
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

    empresa = obtener_empresa_usuario(usuario['id'])
    segmentos = obtener_segmentos_usuario(usuario['id'])
    configuracion = obtener_configuracion_usuario(usuario['id'])

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
    return {
        "segmentos": segmentos,
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

    config = obtener_configuracion_usuario(usuario['id'])
    return config

def modificar_segmentos(numero_telefono, segmentos_nuevos):
    """
    Modifica los segmentos SEACE del usuario

    Args:
        numero_telefono: Número de WhatsApp
        segmentos_nuevos: Lista de segmentos (ej: ["43", "45", "52"])

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

        exito = configurar_segmentos_usuario(usuario['id'], segmentos_nuevos)
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

# Diccionario de funciones disponibles para el agente
HERRAMIENTAS_DB = {
    "obtener_catalogo_segmentos": obtener_catalogo_segmentos,
    "buscar_segmentos_por_palabra": buscar_segmentos_por_palabra,
    "obtener_perfil_completo": obtener_perfil_completo,
    "consultar_segmentos_usuario": consultar_segmentos_usuario,
    "consultar_empresa_usuario": consultar_empresa_usuario,
    "consultar_configuracion_alertas": consultar_configuracion_alertas,
    "modificar_segmentos": modificar_segmentos,
    "modificar_empresa": modificar_empresa,
    "modificar_configuracion_alertas": modificar_configuracion_alertas
}
