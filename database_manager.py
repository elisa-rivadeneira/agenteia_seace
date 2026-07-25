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

def agregar_usuario(numero: str, nombre: str, email: str = "") -> bool:
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
        "activo": True,
        "fecha_creacion": datetime.now().isoformat()
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
    usuarios = cargar_usuarios()

    for u in usuarios:
        if u['numero'] == numero:
            u.update(datos)
            u['ultima_modificacion'] = datetime.now().isoformat()
            return guardar_usuarios(usuarios)

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
