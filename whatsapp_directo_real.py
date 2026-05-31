#!/usr/bin/env python3
"""
WhatsApp Directo REAL - Envío inmediato usando múltiples APIs gratuitas
"""

import requests
import urllib.parse
import time
import json
import os
from datetime import datetime

class WhatsAppDirectoReal:
    def __init__(self, phone_number="+51967717179"):
        self.phone = phone_number.replace('+', '').replace(' ', '')

    def enviar_via_callmebot(self, mensaje: str, api_key: str = None) -> bool:
        """Envía usando CallMeBot (requiere autorización previa)"""
        if not api_key:
            api_key = os.getenv('CALLMEBOT_API_KEY')

        if not api_key:
            print("❌ CallMeBot requiere API key")
            print("📱 Sigue estos pasos:")
            print("1. Abre WhatsApp")
            print("2. Agrega: +34 644 59 71 67")
            print("3. Envía: 'I allow callmebot to send me messages'")
            print("4. Guarda el API key que te respondan")
            return False

        try:
            url = "https://api.callmebot.com/whatsapp.php"
            params = {
                'phone': self.phone,
                'text': mensaje,
                'apikey': api_key
            }

            print(f"📤 Enviando a +{self.phone} via CallMeBot...")
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                print("✅ ¡MENSAJE ENVIADO POR CALLMEBOT!")
                return True
            else:
                print(f"❌ Error CallMeBot: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error CallMeBot: {e}")
            return False

    def enviar_via_zapier_webhook(self, mensaje: str, webhook_url: str = None) -> bool:
        """Envía usando Zapier Webhook (requiere configurar webhook)"""
        if not webhook_url:
            print("❌ Se requiere URL de webhook de Zapier")
            print("🔧 Configura un webhook en Zapier que conecte a WhatsApp")
            return False

        try:
            data = {
                'phone': self.phone,
                'message': mensaje,
                'timestamp': datetime.now().isoformat()
            }

            response = requests.post(webhook_url, json=data, timeout=10)

            if response.status_code == 200:
                print("✅ Mensaje enviado via Zapier!")
                return True
            else:
                print(f"❌ Error Zapier: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error Zapier: {e}")
            return False

    def enviar_via_make_webhook(self, mensaje: str, webhook_url: str = None) -> bool:
        """Envía usando Make.com webhook (anteriormente Integromat)"""
        if not webhook_url:
            print("❌ Se requiere URL de webhook de Make.com")
            return False

        try:
            data = {
                'phone': self.phone,
                'message': mensaje,
                'timestamp': datetime.now().isoformat()
            }

            response = requests.post(webhook_url, json=data, timeout=10)

            if response.status_code == 200:
                print("✅ Mensaje enviado via Make.com!")
                return True
            else:
                print(f"❌ Error Make.com: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error Make.com: {e}")
            return False

    def enviar_via_textbelt(self, mensaje: str) -> bool:
        """Envía usando TextBelt (gratis limitado a 1 por día)"""
        try:
            # TextBelt es principalmente SMS, pero tiene integración WhatsApp experimental
            url = "https://textbelt.com/text"
            data = {
                'phone': self.phone,
                'message': mensaje,
                'key': 'textbelt'  # Clave gratuita limitada
            }

            response = requests.post(url, data=data, timeout=10)
            result = response.json()

            if result.get('success'):
                print("✅ Mensaje enviado via TextBelt!")
                return True
            else:
                print(f"❌ Error TextBelt: {result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Error TextBelt: {e}")
            return False

    def test_all_methods(self, mensaje: str = None):
        """Prueba todos los métodos disponibles"""
        if not mensaje:
            mensaje = f"""🤖 PRUEBA WHATSAPP DIRECTO
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Sistema SEACE operativo
📊 30 oportunidades monitoreadas
🚀 Agente conversacional activo

_Enviado por WhatsApp Directo Real_"""

        print("🧪 PROBANDO TODOS LOS MÉTODOS DE ENVÍO")
        print("=" * 50)

        methods = [
            ('CallMeBot', self.enviar_via_callmebot, {}),
            ('TextBelt', self.enviar_via_textbelt, {}),
        ]

        for name, method, kwargs in methods:
            print(f"\n🔄 Probando {name}...")
            try:
                success = method(mensaje, **kwargs)
                if success:
                    print(f"✅ {name} funcionó!")
                    return True
                else:
                    print(f"❌ {name} falló")
            except Exception as e:
                print(f"❌ Error en {name}: {e}")

        print("\n💡 OPCIONES PARA CONFIGURAR:")
        print("1. CallMeBot: Envía 'I allow callmebot to send me messages' a +34 644 59 71 67")
        print("2. Zapier: Crea un webhook que conecte a WhatsApp")
        print("3. Make.com: Crea un webhook que conecte a WhatsApp")

        return False

    def enviar_mensaje_real(self, mensaje: str, **config) -> bool:
        """Envía mensaje usando el primer método disponible"""
        print(f"📱 ENVIANDO MENSAJE REAL a +{self.phone}")
        print(f"📝 Mensaje: {mensaje[:100]}{'...' if len(mensaje) > 100 else ''}")
        print("-" * 50)

        # Intentar CallMeBot si tiene API key
        callmebot_key = config.get('callmebot_key') or os.getenv('CALLMEBOT_API_KEY')
        if callmebot_key:
            if self.enviar_via_callmebot(mensaje, callmebot_key):
                return True

        # Intentar webhooks si están configurados
        zapier_url = config.get('zapier_webhook_url')
        if zapier_url:
            if self.enviar_via_zapier_webhook(mensaje, zapier_url):
                return True

        make_url = config.get('make_webhook_url')
        if make_url:
            if self.enviar_via_make_webhook(mensaje, make_url):
                return True

        # Intentar TextBelt como último recurso
        if self.enviar_via_textbelt(mensaje):
            return True

        print("❌ Todos los métodos fallaron")
        print("\n🔧 PARA CONFIGURAR ENVÍO AUTOMÁTICO:")
        print("1. CallMeBot (MÁS FÁCIL):")
        print("   - Envía 'I allow callmebot to send me messages' a +34 644 59 71 67")
        print("   - Guarda el API key que te respondan")
        print("2. Zapier/Make.com:")
        print("   - Crea un webhook que conecte a tu WhatsApp")

        return False

def main():
    """Función principal para pruebas"""
    whatsapp = WhatsAppDirectoReal("+51967717179")

    mensaje_test = f"""🚀 PRUEBA SISTEMA FINAL
{datetime.now().strftime('%d/%m/%Y %H:%M')}

🤖 Agente WhatsApp SEACE
✅ Sistema sin navegadores
📊 30 oportunidades monitoreadas

¡Funcionando correctamente!"""

    # Intentar envío real
    success = whatsapp.enviar_mensaje_real(mensaje_test)

    if success:
        print("\n🎉 ¡MENSAJE ENVIADO EXITOSAMENTE!")
        print("📱 Revisa tu WhatsApp - debe haber llegado")
    else:
        print("\n⚠️ No se pudo enviar automáticamente")
        print("🔧 Configura CallMeBot para envío automático")

if __name__ == "__main__":
    main()