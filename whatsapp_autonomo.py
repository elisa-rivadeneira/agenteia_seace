#!/usr/bin/env python3
"""
WhatsApp Autónomo - Envío 100% automático sin intervención manual
"""

import requests
import json
import time
from datetime import datetime
import os

class WhatsAppAutonomo:
    def __init__(self, phone="+51967717179"):
        self.phone = phone.replace('+', '').replace(' ', '')

    def enviar_via_whatsmate_trial(self, mensaje: str) -> bool:
        """Envía usando la API trial gratuita de WhatsMate"""
        try:
            # WhatsMate tiene un plan trial gratuito
            url = "http://api.whatsmate.net/v3/whatsapp/single/text/message/demo"

            data = {
                'number': self.phone,
                'message': mensaje
            }

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(url, json=data, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Mensaje enviado por WhatsMate Trial")
                    return True
                else:
                    print(f"❌ WhatsMate error: {result.get('error')}")
            else:
                print(f"❌ WhatsMate HTTP error: {response.status_code}")

        except Exception as e:
            print(f"❌ Error WhatsMate: {e}")

        return False

    def enviar_via_api_gratuita_peru(self, mensaje: str) -> bool:
        """Intenta usar APIs gratuitas específicas para Perú"""
        try:
            # Algunas APIs que funcionan en Perú sin registro
            apis_gratuitas = [
                {
                    'url': 'https://api.green-api.com/waInstance{{idInstance}}/sendMessage/{{apiTokenInstance}}',
                    'trial': True,
                    'demo_token': 'demo'
                },
                {
                    'url': 'https://api.ultramsg.com/instance1/messages/chat',
                    'trial': True,
                    'demo_token': 'demo'
                }
            ]

            for api in apis_gratuitas:
                try:
                    # Intentar con credenciales demo/trial
                    data = {
                        'chatId': f'{self.phone}@c.us',
                        'message': mensaje
                    }

                    response = requests.post(
                        api['url'].replace('{{idInstance}}', 'demo').replace('{{apiTokenInstance}}', 'demo'),
                        json=data,
                        timeout=5
                    )

                    if response.status_code == 200:
                        print("✅ Mensaje enviado por API gratuita")
                        return True

                except Exception:
                    continue

        except Exception as e:
            print(f"❌ Error APIs gratuitas: {e}")

        return False

    def enviar_via_telegram_bridge(self, mensaje: str) -> bool:
        """Envía via Telegram como alternativa temporal"""
        try:
            # Bot de Telegram que reenvia a WhatsApp (si está configurado)
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
            telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

            if not telegram_token or not telegram_chat_id:
                return False

            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

            data = {
                'chat_id': telegram_chat_id,
                'text': f"📱 SEACE WhatsApp para {self.phone}:\n\n{mensaje}",
                'parse_mode': 'HTML'
            }

            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 200:
                print("✅ Enviado a Telegram como backup")
                return True

        except Exception as e:
            print(f"❌ Error Telegram: {e}")

        return False

    def enviar_mensaje_autonomo(self, mensaje: str) -> bool:
        """Envía mensaje de forma completamente autónoma"""
        print(f"🤖 ENVÍO AUTÓNOMO a +{self.phone}")
        print(f"📝 {mensaje[:100]}{'...' if len(mensaje) > 100 else ''}")
        print("-" * 50)

        # Intentar todos los métodos autónomos
        metodos = [
            ("WhatsMate Trial", self.enviar_via_whatsmate_trial),
            ("APIs Gratuitas", self.enviar_via_api_gratuita_peru),
            ("Telegram Bridge", self.enviar_via_telegram_bridge)
        ]

        for nombre, metodo in metodos:
            try:
                print(f"🔄 Probando {nombre}...")
                if metodo(mensaje):
                    print(f"✅ Éxito con {nombre}")
                    return True
                else:
                    print(f"❌ {nombre} no funcionó")
            except Exception as e:
                print(f"❌ Error en {nombre}: {e}")

        print("❌ Ningún método autónomo funcionó")
        print("\n💡 SOLUCIÓN DEFINITIVA:")
        print("1. Configura CallMeBot: python3 configurar_callmebot.py")
        print("2. O configura Twilio: export TWILIO_ACCOUNT_SID=tu_sid")

        return False

def main():
    """Prueba el envío autónomo"""
    whatsapp = WhatsAppAutonomo("+51967717179")

    mensaje = f"""🚀 PRUEBA AUTÓNOMA
{datetime.now().strftime('%d/%m/%Y %H:%M')}

🤖 Sistema completamente autónomo
✅ Sin intervención manual
📊 SEACE operativo

¡Funcionando!"""

    success = whatsapp.enviar_mensaje_autonomo(mensaje)

    if success:
        print("\n🎉 ¡MENSAJE ENVIADO AUTOMÁTICAMENTE!")
    else:
        print("\n⚠️ Requiere configuración para envío autónomo")

if __name__ == "__main__":
    main()