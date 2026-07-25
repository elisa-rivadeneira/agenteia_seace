#!/usr/bin/env python3
"""
Gestor de configuración de alertas
Maneja la configuración de horarios y destinatarios de alertas
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from config_paths import ALERTAS_CONFIG_FILE

def cargar_config_alertas() -> Dict:
    """Carga la configuración de alertas"""
    if ALERTAS_CONFIG_FILE.exists():
        try:
            with open(ALERTAS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return crear_config_por_defecto()
    return crear_config_por_defecto()

def crear_config_por_defecto() -> Dict:
    """Crea configuración por defecto"""
    config = {
        "horarios": [
            {"hora": "10:00", "activo": True, "descripcion": "Escaneo matutino"},
            {"hora": "19:00", "activo": True, "descripcion": "Escaneo vespertino"}
        ],
        "destinatarios": [],
        "configuracion": {
            "score_minimo": 30,
            "max_oportunidades_por_alerta": 5,
            "enviar_resumen": True,
            "enviar_detalles": True
        }
    }
    guardar_config_alertas(config)
    return config

def guardar_config_alertas(config: Dict) -> bool:
    """Guarda la configuración de alertas"""
    try:
        with open(ALERTAS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando config alertas: {e}")
        return False

def obtener_destinatarios_activos() -> List[str]:
    """Obtiene lista de números activos para recibir alertas"""
    config = cargar_config_alertas()
    return [
        d['numero'] for d in config.get('destinatarios', [])
        if d.get('activo', False)
    ]

def agregar_destinatario(numero: str, nombre: str = "") -> bool:
    """Agrega un nuevo destinatario"""
    config = cargar_config_alertas()

    # Verificar si ya existe
    for dest in config.get('destinatarios', []):
        if dest['numero'] == numero:
            return False

    config['destinatarios'].append({
        'numero': numero,
        'nombre': nombre or f"Usuario {numero[-4:]}",
        'activo': True,
        'agregado_el': datetime.now().isoformat()
    })

    return guardar_config_alertas(config)

def eliminar_destinatario(numero: str) -> bool:
    """Elimina un destinatario"""
    config = cargar_config_alertas()
    config['destinatarios'] = [
        d for d in config.get('destinatarios', [])
        if d['numero'] != numero
    ]
    return guardar_config_alertas(config)

def activar_desactivar_destinatario(numero: str, activo: bool) -> bool:
    """Activa o desactiva un destinatario"""
    config = cargar_config_alertas()

    for dest in config.get('destinatarios', []):
        if dest['numero'] == numero:
            dest['activo'] = activo
            return guardar_config_alertas(config)

    return False

def agregar_horario(hora: str, descripcion: str = "") -> bool:
    """Agrega un nuevo horario de alerta"""
    config = cargar_config_alertas()

    # Verificar formato HH:MM
    try:
        h, m = hora.split(':')
        if not (0 <= int(h) <= 23 and 0 <= int(m) <= 59):
            return False
    except:
        return False

    # Verificar si ya existe
    for horario in config.get('horarios', []):
        if horario['hora'] == hora:
            return False

    config['horarios'].append({
        'hora': hora,
        'activo': True,
        'descripcion': descripcion or f"Alerta {hora}"
    })

    return guardar_config_alertas(config)

def eliminar_horario(hora: str) -> bool:
    """Elimina un horario de alerta"""
    config = cargar_config_alertas()
    config['horarios'] = [
        h for h in config.get('horarios', [])
        if h['hora'] != hora
    ]
    return guardar_config_alertas(config)

def activar_desactivar_horario(hora: str, activo: bool) -> bool:
    """Activa o desactiva un horario"""
    config = cargar_config_alertas()

    for horario in config.get('horarios', []):
        if horario['hora'] == hora:
            horario['activo'] = activo
            return guardar_config_alertas(config)

    return False

def actualizar_configuracion(score_minimo: int = None, max_oportunidades: int = None) -> bool:
    """Actualiza parámetros de configuración"""
    config = cargar_config_alertas()

    if score_minimo is not None:
        config['configuracion']['score_minimo'] = score_minimo

    if max_oportunidades is not None:
        config['configuracion']['max_oportunidades_por_alerta'] = max_oportunidades

    return guardar_config_alertas(config)

def obtener_estadisticas_alertas() -> Dict:
    """Obtiene estadísticas de alertas"""
    config = cargar_config_alertas()

    horarios = config.get('horarios', [])
    destinatarios = config.get('destinatarios', [])

    return {
        'total_horarios': len(horarios),
        'horarios_activos': len([h for h in horarios if h.get('activo', False)]),
        'total_destinatarios': len(destinatarios),
        'destinatarios_activos': len([d for d in destinatarios if d.get('activo', False)]),
        'configuracion': config.get('configuracion', {})
    }
