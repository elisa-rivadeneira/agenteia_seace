#!/usr/bin/env python3
"""
SOLUCIÓN ULTRA SIMPLE - Un solo comando para configurar envío automático
"""

import webbrowser
import time

def configurar_en_30_segundos():
    """Configuración en 30 segundos"""
    print("🚀 CONFIGURACIÓN AUTOMÁTICA EN 30 SEGUNDOS")
    print("=" * 50)

    print("📱 PASO 1: Abriendo WhatsApp Web...")

    # URL que abre WhatsApp Web directamente con el contacto y mensaje preparado
    url = "https://web.whatsapp.com/send?phone=34644597167&text=I%20allow%20callmebot%20to%20send%20me%20messages"

    webbrowser.open(url)

    print("✅ WhatsApp Web abierto")
    print("📱 PASO 2: HAZ CLIC EN 'ENVIAR' (1 solo clic)")
    print("⏳ PASO 3: Espera 1-2 minutos tu API key")
    print()
    print("🔑 CUANDO RECIBAS EL API KEY:")
    print("   export CALLMEBOT_API_KEY='tu_key_aqui'")
    print()
    print("🎉 DESPUÉS: Todos los mensajes del agente llegan automáticamente")
    print("   ¡Sin navegadores, sin configuración compleja!")

if __name__ == "__main__":
    configurar_en_30_segundos()