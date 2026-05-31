#!/usr/bin/env python3
"""
Envío automático REAL sin intervención manual
"""

import requests
import os
from datetime import datetime

def enviar_con_callmebot_demo():
    """Prueba con CallMeBot usando API key demo para testing"""
    try:
        # Número de destino
        phone = "51967717179"

        mensaje = f"""🤖 PRUEBA ENVÍO AUTOMÁTICO
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Este mensaje debe llegar SIN intervención manual
📱 Directo a tu WhatsApp
🚀 Sistema SEACE completamente automático

¡Testing exitoso!"""

        print("🧪 PROBANDO CALLMEBOT CON DIFERENTES MÉTODOS...")

        # Método 1: Intentar con credenciales demo
        apis_test = [
            {
                'name': 'CallMeBot Demo',
                'url': 'https://api.callmebot.com/whatsapp.php',
                'params': {
                    'phone': phone,
                    'text': mensaje,
                    'apikey': 'demo123'  # Intentar con key demo
                }
            },
            {
                'name': 'TextBelt Free Trial',
                'url': 'https://textbelt.com/text',
                'method': 'POST',
                'data': {
                    'phone': f'+{phone}',
                    'message': mensaje,
                    'key': 'textbelt'
                }
            }
        ]

        for api in apis_test:
            print(f"\n🔄 Probando {api['name']}...")

            try:
                if api.get('method') == 'POST':
                    response = requests.post(api['url'], data=api['data'], timeout=10)
                else:
                    response = requests.get(api['url'], params=api['params'], timeout=10)

                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:100]}...")

                if response.status_code == 200:
                    print(f"✅ {api['name']} respondió exitosamente")

                    if 'success' in response.text.lower() or 'sent' in response.text.lower():
                        print("🎉 ¡MENSAJE ENVIADO AUTOMÁTICAMENTE!")
                        return True
                else:
                    print(f"❌ {api['name']} falló")

            except Exception as e:
                print(f"❌ Error {api['name']}: {e}")

        print("\n💡 PARA ENVÍO AUTOMÁTICO GARANTIZADO:")
        print("1. Configura CallMeBot (2 minutos):")
        print("   - Envía 'I allow callmebot to send me messages' a +34 644 59 71 67")
        print("   - Recibe tu API key personal")
        print("   - Ejecuta: export CALLMEBOT_API_KEY='tu_key'")
        print("\n2. O configura Twilio ($0.05/mensaje):")
        print("   - Crea cuenta en console.twilio.com")
        print("   - Configura WhatsApp Sandbox")

        return False

    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def mostrar_configuracion_rapida():
    """Muestra cómo configurar envío automático en 2 minutos"""
    print("🚀 CONFIGURACIÓN ENVÍO AUTOMÁTICO REAL")
    print("=" * 50)
    print("⏰ Tiempo: 2 minutos")
    print("💰 Costo: GRATIS")
    print("🤖 Resultado: Mensajes 100% automáticos")
    print()
    print("📱 PASOS:")
    print("1. Abre WhatsApp en tu celular")
    print("2. Agrega contacto: +34 644 59 71 67")
    print("3. Envía: 'I allow callmebot to send me messages'")
    print("4. Recibes tu API key en 1-2 minutos")
    print("5. Ejecuta: export CALLMEBOT_API_KEY='tu_key_aqui'")
    print()
    print("✅ DESPUÉS: Todos los mensajes del agente SEACE")
    print("   llegan automáticamente sin intervención manual")
    print()
    print("🔧 ALTERNATIVA INMEDIATA (PAGO):")
    print("   python3 setup_twilio_rapido.py")

if __name__ == "__main__":
    print("🤖 TESTING ENVÍO AUTOMÁTICO REAL")
    print("=" * 40)

    success = enviar_con_callmebot_demo()

    if not success:
        print()
        mostrar_configuracion_rapida()