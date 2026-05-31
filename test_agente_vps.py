#!/usr/bin/env python3
"""
Prueba rápida del agente SEACE con VPS
"""

from agente_whatsapp import AgenteWhatsAppSEACE
from datetime import datetime

def test_agente_vps():
    print("🧪 PROBANDO AGENTE SEACE CON VPS...")

    agente = AgenteWhatsAppSEACE()

    mensaje_test = f"""🚀 AGENTE SEACE VPS OPERATIVO!
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Evolution API VPS funcionando
🤖 Envío completamente automático
📊 30 oportunidades SEACE monitoreadas
⚡ Sin navegadores, desde la nube

¡Sistema 100% automático!"""

    success = agente.enviar_mensaje(mensaje_test)

    if success:
        print("🎉 ¡AGENTE FUNCIONANDO PERFECTAMENTE!")
        print("📱 El mensaje debe haber llegado a tu WhatsApp")
    else:
        print("❌ Error en el agente")

if __name__ == "__main__":
    test_agente_vps()
