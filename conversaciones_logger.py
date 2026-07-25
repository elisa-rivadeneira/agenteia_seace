#!/usr/bin/env python3
"""
Logger de conversaciones para el admin dashboard
Guarda todas las interacciones con el bot
"""

import json
import os
from datetime import datetime
from config_paths import CONVERSACIONES_FILE

def log_conversacion(numero_telefono, mensaje_usuario, respuesta_bot, nombre_usuario="", tipo_mensaje="texto"):
    """
    Registra una interacción usuario-bot

    Args:
        numero_telefono: Número de WhatsApp del usuario
        mensaje_usuario: Mensaje enviado por el usuario
        respuesta_bot: Respuesta del bot
        nombre_usuario: Nombre del usuario de WhatsApp (pushName)
        tipo_mensaje: Tipo de mensaje (texto, comando, etc.)
    """
    try:
        # Cargar conversaciones existentes
        if CONVERSACIONES_FILE.exists():
            with open(CONVERSACIONES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"conversaciones": {}}

        # Crear entrada para el usuario si no existe
        if numero_telefono not in data["conversaciones"]:
            data["conversaciones"][numero_telefono] = {
                "numero": numero_telefono,
                "nombre": nombre_usuario,
                "primera_interaccion": datetime.now().isoformat(),
                "ultima_interaccion": datetime.now().isoformat(),
                "total_mensajes": 0,
                "historial": []
            }

        # Actualizar nombre si se proporciona y es diferente
        if nombre_usuario and data["conversaciones"][numero_telefono].get("nombre") != nombre_usuario:
            data["conversaciones"][numero_telefono]["nombre"] = nombre_usuario

        # Agregar mensaje al historial
        data["conversaciones"][numero_telefono]["historial"].append({
            "timestamp": datetime.now().isoformat(),
            "tipo": tipo_mensaje,
            "mensaje_usuario": mensaje_usuario,
            "respuesta_bot": respuesta_bot
        })

        # Actualizar metadatos
        data["conversaciones"][numero_telefono]["ultima_interaccion"] = datetime.now().isoformat()
        data["conversaciones"][numero_telefono]["total_mensajes"] += 1

        # Guardar
        with open(CONVERSACIONES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error logging conversación: {e}")

def obtener_todas_conversaciones():
    """Obtiene todas las conversaciones"""
    try:
        if CONVERSACIONES_FILE.exists():
            with open(CONVERSACIONES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("conversaciones", {})
        return {}
    except Exception as e:
        print(f"Error obteniendo conversaciones: {e}")
        return {}

def obtener_conversacion(numero_telefono):
    """Obtiene una conversación específica"""
    conversaciones = obtener_todas_conversaciones()
    return conversaciones.get(numero_telefono, None)

def obtener_estadisticas():
    """Obtiene estadísticas generales"""
    conversaciones = obtener_todas_conversaciones()

    total_usuarios = len(conversaciones)
    total_mensajes = sum(c.get("total_mensajes", 0) for c in conversaciones.values())

    # Usuarios más activos
    usuarios_ordenados = sorted(
        conversaciones.items(),
        key=lambda x: x[1].get("total_mensajes", 0),
        reverse=True
    )[:5]

    return {
        "total_usuarios": total_usuarios,
        "total_mensajes": total_mensajes,
        "usuarios_mas_activos": [
            {
                "numero": u[0],
                "mensajes": u[1].get("total_mensajes", 0),
                "ultima_interaccion": u[1].get("ultima_interaccion", "N/A")
            }
            for u in usuarios_ordenados
        ]
    }
