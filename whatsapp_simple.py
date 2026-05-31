#!/usr/bin/env python3
"""
WhatsApp Simple - Usando URL directa sin automatización compleja
"""

import webbrowser
import urllib.parse
import time
from datetime import datetime

class WhatsAppSimple:
    def __init__(self, phone_number="+51967717179"):
        self.phone_number = phone_number

    def send_message(self, message: str) -> bool:
        """
        Abre WhatsApp Web con el mensaje pre-escrito
        El usuario solo necesita hacer clic en enviar
        """
        try:
            # Limpiar número de teléfono
            clean_phone = self.phone_number.replace('+', '').replace(' ', '').replace('-', '')

            # Codificar mensaje para URL
            encoded_message = urllib.parse.quote(message)

            # Crear URL de WhatsApp
            whatsapp_url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"

            print(f"🌐 Abriendo WhatsApp Web...")
            print(f"📱 Número: {self.phone_number}")
            print(f"📝 Mensaje preparado, solo haz clic en ENVIAR")

            # Abrir en navegador
            webbrowser.open(whatsapp_url)

            print("✅ URL abierta en el navegador")
            print("💡 El mensaje ya está escrito, solo presiona ENVIAR en WhatsApp")

            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def test_simple():
    """Prueba del método simple"""
    print("📱 WHATSAPP SIMPLE - MÉTODO URL")
    print("=" * 50)

    # Cargar configuración
    try:
        import json
        with open('config_empresa.json', 'r') as f:
            config = json.load(f)
        phone = config['notificaciones']['whatsapp']
        empresa = config['empresa']['nombre']
    except:
        phone = "+51967717179"
        empresa = "SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C"

    mensaje = f"""📊 REPORTE SEACE - {datetime.now().strftime('%d/%m/%Y %H:%M')}

🏢 {empresa}

🔍 RESUMEN SEGMENTO 43:
• Total oportunidades: 30
• Relevantes (≥25%): 6
• Más compatible: MUNICIPALIDAD DE LA MOLINA (40%)

🚨 URGENTES:
• EMPRESA SAN GABÁN - 01/06/2026
• ELECTRO ORIENTE - 03/06/2026
• BANCO DE LA NACIÓN - 03/06/2026

🤖 Sistema automático SEACE
✅ Monitor funcionando correctamente"""

    print("📝 Mensaje a enviar:")
    print("-" * 30)
    print(mensaje)
    print("-" * 30)

    whatsapp = WhatsAppSimple(phone)
    success = whatsapp.send_message(mensaje)

    if success:
        print("\n🎉 ¡LISTO! Ve al navegador y haz clic en ENVIAR")
        print("📲 El mensaje ya está preparado en WhatsApp Web")
    else:
        print("\n❌ Error preparando el mensaje")

if __name__ == "__main__":
    test_simple()