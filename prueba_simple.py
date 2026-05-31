#!/usr/bin/env python3
"""
Prueba simple de WhatsApp
"""

from whatsapp_notifier import WhatsAppNotifier
from datetime import datetime

def main():
    print("🧪 PRUEBA SIMPLE WHATSAPP")
    print("=" * 40)

    try:
        # Crear notificador
        notifier = WhatsAppNotifier()
        print(f"✅ Empresa: {notifier.empresa}")
        print(f"📱 Número: {notifier.whatsapp_number}")

        # Mensaje simple
        mensaje = f"""📊 PRUEBA SEACE MONITOR

🏢 {notifier.empresa}
📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Sistema WhatsApp funcionando correctamente!

🔍 Monitor SEACE activo
🎯 Segmento 43: 30 oportunidades detectadas

_Mensaje de prueba automático_"""

        print("\n📝 Enviando mensaje...")
        print(mensaje[:100] + "...")

        # Intentar envío
        success = notifier.send_message(mensaje, priority='normal')

        if success:
            print("\n✅ ¡MENSAJE ENVIADO!")
            print("📲 Revisa WhatsApp para confirmarlo")
        else:
            print("\n❌ ERROR al enviar mensaje")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()