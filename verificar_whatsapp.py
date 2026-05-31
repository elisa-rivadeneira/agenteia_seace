#!/usr/bin/env python3
"""
Verificar configuración de WhatsApp paso a paso
"""

import json
import webbrowser
import urllib.parse

def verificar_configuracion():
    print("🔍 VERIFICACIÓN WHATSAPP - PASO A PASO")
    print("=" * 50)

    # 1. Verificar configuración
    try:
        with open('config_empresa.json', 'r') as f:
            config = json.load(f)
        phone = config['notificaciones']['whatsapp']
        empresa = config['empresa']['nombre']
        print(f"✅ Configuración cargada:")
        print(f"   📱 Número: {phone}")
        print(f"   🏢 Empresa: {empresa}")
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return

    # 2. Verificar formato del número
    if phone.startswith('+51') and len(phone) == 12:
        print("✅ Formato de número correcto")
    else:
        print(f"⚠️ Verifica el formato del número: {phone}")
        print("   Debe ser: +51xxxxxxxxx (12 dígitos total)")

    # 3. Mensaje de prueba simple
    mensaje_prueba = "Hola, esta es una prueba del sistema SEACE. Si recibes este mensaje, el sistema funciona correctamente. 👍"

    # 4. Generar URL de WhatsApp
    clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
    encoded_message = urllib.parse.quote(mensaje_prueba)
    whatsapp_url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"

    print(f"\n📱 PASOS PARA VERIFICAR:")
    print("1. ¿Tienes WhatsApp instalado en tu celular?")
    print("2. ¿WhatsApp Web está habilitado? (Configuración > Dispositivos vinculados)")
    print("3. ¿El número +51967717179 puede recibir mensajes?")

    print(f"\n🌐 Abriendo WhatsApp Web con mensaje de prueba...")
    print(f"📝 Mensaje: {mensaje_prueba[:50]}...")

    webbrowser.open(whatsapp_url)

    print("\n✅ URL abierta en el navegador")
    print("\n📋 QUÉ HACER AHORA:")
    print("1. Ve al navegador que se abrió")
    print("2. Si aparece QR Code, escanéalo con tu celular")
    print("3. Verifica que el mensaje aparezca en la caja de texto")
    print("4. HAZ CLIC EN ENVIAR")
    print("5. Verifica que llegue a tu celular")

    print(f"\n🎯 URL generada:")
    print(f"   {whatsapp_url[:80]}...")

if __name__ == "__main__":
    verificar_configuracion()