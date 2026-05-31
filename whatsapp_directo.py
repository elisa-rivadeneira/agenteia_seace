#!/usr/bin/env python3
"""
WhatsApp DIRECTO - Sin navegadores, envío inmediato
Usa CallMeBot API que envía directamente sin configuración compleja
"""

import requests
import urllib.parse
import time
from datetime import datetime

class WhatsAppDirecto:
    def __init__(self, phone_number="+51967717179"):
        """Inicializa el enviador directo"""
        self.phone_number = phone_number.replace('+', '').replace(' ', '')

        # Servicios de WhatsApp API gratuitos
        self.servicios = [
            {
                'nombre': 'CallMeBot',
                'url': 'https://api.callmebot.com/whatsapp.php',
                'requiere_key': True,
                'instrucciones': 'Envía "I allow callmebot to send me messages" al +34 644 59 71 67'
            },
            {
                'nombre': 'WhatsMate',
                'url': 'http://api.whatsmate.net/v3/whatsapp/single/text/message/{instance_id}',
                'requiere_key': True,
                'instrucciones': 'Requiere registro en whatsmate.net'
            }
        ]

    def enviar_con_callmebot(self, mensaje: str, api_key: str = None) -> bool:
        """Envía usando CallMeBot API"""
        try:
            # Para usar CallMeBot necesitas enviar un mensaje de autorización primero
            # Paso 1: Envía "I allow callmebot to send me messages" al +34 644 59 71 67
            # Paso 2: Te responden con tu API key personal

            if not api_key:
                print("❌ CallMeBot requiere API key")
                print("📱 Envía este mensaje a +34 644 59 71 67:")
                print("   'I allow callmebot to send me messages'")
                print("🔑 Te responderán con tu API key personal")
                return False

            url = "https://api.callmebot.com/whatsapp.php"
            params = {
                'phone': self.phone_number,
                'text': mensaje,
                'apikey': api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                print("✅ Mensaje enviado por CallMeBot")
                return True
            else:
                print(f"❌ Error CallMeBot: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error CallMeBot: {e}")
            return False

    def enviar_con_whatsmate(self, mensaje: str, instance_id: str = None, client_id: str = None, client_secret: str = None) -> bool:
        """Envía usando WhatsMate API"""
        try:
            if not all([instance_id, client_id, client_secret]):
                print("❌ WhatsMate requiere credenciales")
                print("🌐 Regístrate en: http://www.whatsmate.net")
                return False

            url = f"http://api.whatsmate.net/v3/whatsapp/single/text/message/{instance_id}"

            headers = {
                'X-WM-CLIENT-ID': client_id,
                'X-WM-CLIENT-SECRET': client_secret,
                'Content-Type': 'application/json'
            }

            data = {
                'number': self.phone_number,
                'message': mensaje
            }

            response = requests.post(url, json=data, headers=headers, timeout=10)

            if response.status_code == 200:
                print("✅ Mensaje enviado por WhatsMate")
                return True
            else:
                print(f"❌ Error WhatsMate: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error WhatsMate: {e}")
            return False

    def enviar_mensaje(self, mensaje: str, **credenciales) -> bool:
        """Envía mensaje usando el servicio disponible"""
        print(f"📤 Enviando mensaje directo a {self.phone_number}")
        print(f"📝 Mensaje: {mensaje[:50]}{'...' if len(mensaje) > 50 else ''}")

        # Intentar CallMeBot
        if 'callmebot_key' in credenciales:
            if self.enviar_con_callmebot(mensaje, credenciales['callmebot_key']):
                return True

        # Intentar WhatsMate
        if all(k in credenciales for k in ['whatsmate_instance', 'whatsmate_client_id', 'whatsmate_secret']):
            if self.enviar_con_whatsmate(
                mensaje,
                credenciales['whatsmate_instance'],
                credenciales['whatsmate_client_id'],
                credenciales['whatsmate_secret']
            ):
                return True

        # Si no hay credenciales, mostrar opciones
        print("\n💡 PARA ENVÍO DIRECTO SIN NAVEGADORES:")
        print("=" * 50)

        for i, servicio in enumerate(self.servicios, 1):
            print(f"\n{i}. {servicio['nombre']}")
            print(f"   {servicio['instrucciones']}")

        print(f"\n📱 Tu número: {self.phone_number}")
        return False

def test_whatsapp_directo():
    """Prueba el enviador directo"""
    print("🚀 WHATSAPP DIRECTO - SIN NAVEGADORES")
    print("=" * 50)

    whatsapp = WhatsAppDirecto("+51967717179")

    mensaje = f"""🤖 PRUEBA WHATSAPP DIRECTO
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Sistema funcionando sin navegadores!

🔍 Monitor SEACE operativo
📊 30 oportunidades detectadas

_Enviado directo por API_"""

    # Intentar envío (requiere configuración de API keys)
    success = whatsapp.enviar_mensaje(
        mensaje,
        # callmebot_key="TU_KEY_AQUI",  # Descomenta cuando tengas el key
        # whatsmate_instance="TU_INSTANCE",
        # whatsmate_client_id="TU_CLIENT_ID",
        # whatsmate_secret="TU_SECRET"
    )

    if success:
        print("🎉 ¡Mensaje enviado exitosamente!")
    else:
        print("⚠️ Configuración de API requerida")

if __name__ == "__main__":
    test_whatsapp_directo()