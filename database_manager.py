#!/usr/bin/env python3
"""
Gestor de Base de Datos JSON para el sistema SEACE
Maneja usuarios y alertas de forma independiente
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from config_paths import get_data_path

USUARIOS_DB_FILE = get_data_path('usuarios.json')
ALERTAS_DB_FILE = get_data_path('alertas.json')

# ===== GESTIÓN DE USUARIOS =====

def inicializar_usuarios_db():
    """Crea la base de datos de usuarios si no existe"""
    if not USUARIOS_DB_FILE.exists():
        db = {
            "usuarios": [],
            "ultima_actualizacion": datetime.now().isoformat()
        }
        with open(USUARIOS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"✅ Creada BD de usuarios: {USUARIOS_DB_FILE}")

def cargar_usuarios() -> List[Dict]:
    """Carga todos los usuarios"""
    inicializar_usuarios_db()
    try:
        with open(USUARIOS_DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('usuarios', [])
    except:
        return []

def guardar_usuarios(usuarios: List[Dict]) -> bool:
    """Guarda la lista de usuarios"""
    try:
        data = {
            "usuarios": usuarios,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        with open(USUARIOS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando usuarios: {e}")
        return False

def agregar_usuario(numero: str, nombre: str, email: str = "", segmentos: List[str] = None) -> bool:
    """Agrega un nuevo usuario"""
    usuarios = cargar_usuarios()

    # Verificar si ya existe
    for u in usuarios:
        if u['numero'] == numero:
            return False

    nuevo_usuario = {
        "id": len(usuarios) + 1,
        "numero": numero,
        "nombre": nombre,
        "email": email,
        "segmentos": segmentos or ["43"],
        "score_minimo": 30,
        "max_oportunidades": 5,
        "horarios_alerta": ["10:00", "19:00"],
        "palabras_clave_custom": [],
        "activo": True,
        "fecha_creacion": datetime.now().isoformat(),
        "configurado": False
    }

    usuarios.append(nuevo_usuario)
    return guardar_usuarios(usuarios)

def obtener_usuario(numero: str) -> Optional[Dict]:
    """Obtiene un usuario por número"""
    usuarios = cargar_usuarios()
    for u in usuarios:
        if u['numero'] == numero:
            return u
    return None

def actualizar_usuario(numero: str, datos: Dict) -> bool:
    """Actualiza datos de un usuario"""
    try:
        print(f"📝 Actualizando usuario {numero} con datos: {datos}")
        usuarios = cargar_usuarios()
        print(f"📋 Total usuarios cargados: {len(usuarios)}")

        for u in usuarios:
            if u['numero'] == numero:
                print(f"✅ Usuario encontrado, actualizando...")
                u.update(datos)
                u['ultima_modificacion'] = datetime.now().isoformat()
                resultado = guardar_usuarios(usuarios)
                print(f"💾 Guardado: {resultado}")
                return resultado

        print(f"⚠️ Usuario {numero} no encontrado en la lista")
        return False
    except Exception as e:
        print(f"❌ Error en actualizar_usuario: {e}")
        import traceback
        traceback.print_exc()
        return False

def eliminar_usuario(numero: str) -> bool:
    """Elimina un usuario"""
    usuarios = cargar_usuarios()
    usuarios = [u for u in usuarios if u['numero'] != numero]
    return guardar_usuarios(usuarios)

def obtener_usuarios_activos() -> List[Dict]:
    """Obtiene solo usuarios activos"""
    usuarios = cargar_usuarios()
    return [u for u in usuarios if u.get('activo', False)]

def configurar_segmentos_usuario(numero: str, segmentos: List[str]) -> bool:
    """Configura los segmentos de interés de un usuario"""
    try:
        print(f"📝 Configurando segmentos para {numero}: {segmentos}")
        resultado = actualizar_usuario(numero, {
            'segmentos': segmentos,
            'configurado': True
        })
        print(f"✅ Resultado configuración: {resultado}")
        return resultado
    except Exception as e:
        print(f"❌ Error en configurar_segmentos_usuario: {e}")
        import traceback
        traceback.print_exc()
        return False

def obtener_segmentos_usuario(numero: str) -> List[str]:
    """Obtiene los segmentos configurados de un usuario"""
    usuario = obtener_usuario(numero)
    if usuario:
        return usuario.get('segmentos', ['43'])
    return ['43']

def agregar_segmento_usuario(numero: str, segmento: str) -> bool:
    """Agrega un segmento a la configuración del usuario"""
    usuario = obtener_usuario(numero)
    if not usuario:
        return False

    segmentos = usuario.get('segmentos', [])
    if segmento not in segmentos:
        segmentos.append(segmento)
        return configurar_segmentos_usuario(numero, segmentos)
    return True

def remover_segmento_usuario(numero: str, segmento: str) -> bool:
    """Remueve un segmento de la configuración del usuario"""
    usuario = obtener_usuario(numero)
    if not usuario:
        return False

    segmentos = usuario.get('segmentos', [])
    if segmento in segmentos and len(segmentos) > 1:  # Mantener al menos 1
        segmentos.remove(segmento)
        return configurar_segmentos_usuario(numero, segmentos)
    return False

# Catálogo de segmentos SEACE
SEGMENTOS_SEACE = {
    "43": "Tecnologías de la Información",
    "80": "Servicios profesionales y consultoría",
    "81": "Investigación y desarrollo",
    "72": "Arquitectura e ingeniería",
    "42": "Equipos médicos y laboratorio",
    "44": "Equipos de oficina y computación",
    "45": "Equipos de telecomunicaciones",
    "76": "Servicios de limpieza",
    "77": "Servicios de seguridad",
    "78": "Servicios de mantenimiento"
}

def obtener_catalogo_segmentos() -> Dict[str, str]:
    """Retorna el catálogo completo de segmentos SEACE"""
    return SEGMENTOS_SEACE

def obtener_nombre_segmento(codigo: str) -> str:
    """Obtiene el nombre de un segmento por su código"""
    return SEGMENTOS_SEACE.get(codigo, f"Segmento {codigo}")

# ===== GESTIÓN DE ALERTAS =====

def inicializar_alertas_db():
    """Crea la base de datos de alertas si no existe"""
    if not ALERTAS_DB_FILE.exists():
        db = {
            "alertas": [],
            "ultima_actualizacion": datetime.now().isoformat()
        }
        with open(ALERTAS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"✅ Creada BD de alertas: {ALERTAS_DB_FILE}")

def cargar_alertas() -> List[Dict]:
    """Carga todas las alertas"""
    inicializar_alertas_db()
    try:
        with open(ALERTAS_DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('alertas', [])
    except:
        return []

def guardar_alertas(alertas: List[Dict]) -> bool:
    """Guarda la lista de alertas"""
    try:
        data = {
            "alertas": alertas,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        with open(ALERTAS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando alertas: {e}")
        return False

def crear_alerta(nombre: str, segmento: str, horarios: List[str],
                 dias_semana: List[int], usuarios: List[str],
                 score_minimo: int = 30, max_oportunidades: int = 5) -> bool:
    """
    Crea una nueva alerta

    Args:
        nombre: Nombre descriptivo de la alerta
        segmento: Código del segmento SEACE (ej: "43")
        horarios: Lista de horarios en formato HH:MM (ej: ["10:00", "19:00"])
        dias_semana: Lista de días (0=Lunes, 6=Domingo) (ej: [0,1,2,3,4] para L-V)
        usuarios: Lista de números de teléfono de usuarios
        score_minimo: Score mínimo de compatibilidad
        max_oportunidades: Máximo de oportunidades a enviar
    """
    alertas = cargar_alertas()

    nueva_alerta = {
        "id": len(alertas) + 1,
        "nombre": nombre,
        "segmento": segmento,
        "horarios": horarios,
        "dias_semana": dias_semana,
        "usuarios": usuarios,
        "configuracion": {
            "score_minimo": score_minimo,
            "max_oportunidades": max_oportunidades
        },
        "activo": True,
        "fecha_creacion": datetime.now().isoformat(),
        "ultima_ejecucion": None
    }

    alertas.append(nueva_alerta)
    return guardar_alertas(alertas)

def obtener_alerta(alerta_id: int) -> Optional[Dict]:
    """Obtiene una alerta por ID"""
    alertas = cargar_alertas()
    for a in alertas:
        if a['id'] == alerta_id:
            return a
    return None

def actualizar_alerta(alerta_id: int, datos: Dict) -> bool:
    """Actualiza una alerta"""
    alertas = cargar_alertas()

    for a in alertas:
        if a['id'] == alerta_id:
            a.update(datos)
            a['ultima_modificacion'] = datetime.now().isoformat()
            return guardar_alertas(alertas)

    return False

def eliminar_alerta(alerta_id: int) -> bool:
    """Elimina una alerta"""
    alertas = cargar_alertas()
    alertas = [a for a in alertas if a['id'] != alerta_id]
    return guardar_alertas(alertas)

def obtener_alertas_activas() -> List[Dict]:
    """Obtiene solo alertas activas"""
    alertas = cargar_alertas()
    return [a for a in alertas if a.get('activo', False)]

def activar_desactivar_alerta(alerta_id: int, activo: bool) -> bool:
    """Activa o desactiva una alerta"""
    return actualizar_alerta(alerta_id, {'activo': activo})

def registrar_ejecucion_alerta(alerta_id: int):
    """Registra la última ejecución de una alerta"""
    return actualizar_alerta(alerta_id, {
        'ultima_ejecucion': datetime.now().isoformat()
    })

# ===== FUNCIONES AUXILIARES =====

def obtener_estadisticas() -> Dict:
    """Obtiene estadísticas generales"""
    usuarios = cargar_usuarios()
    alertas = cargar_alertas()

    usuarios_activos = [u for u in usuarios if u.get('activo', False)]
    alertas_activas = [a for a in alertas if a.get('activo', False)]

    return {
        "total_usuarios": len(usuarios),
        "usuarios_activos": len(usuarios_activos),
        "total_alertas": len(alertas),
        "alertas_activas": len(alertas_activas)
    }

def importar_usuarios_desde_conversaciones():
    """Importa usuarios desde conversaciones_log.json"""
    from conversaciones_logger import obtener_todas_conversaciones

    conversaciones = obtener_todas_conversaciones()
    usuarios_importados = 0

    for numero, conv in conversaciones.items():
        numero_limpio = numero.split('@')[0]
        nombre = conv.get('nombre', f"Usuario {numero_limpio[-4:]}")

        if not obtener_usuario(numero_limpio):
            if agregar_usuario(numero_limpio, nombre):
                usuarios_importados += 1

    return usuarios_importados

# Inicializar al importar el módulo
inicializar_usuarios_db()
inicializar_alertas_db()
