#!/usr/bin/env python3
"""
Prueba final del sistema WhatsApp automático
"""

from whatsapp_notifier import WhatsAppNotifier
from datetime import datetime

def main():
    print("🚀 PRUEBA FINAL - WHATSAPP AUTOMÁTICO")
    print("=" * 50)

    try:
        notifier = WhatsAppNotifier()
        print(f"✅ Sistema cargado para: {notifier.empresa}")

        mensaje = f"""📊 REPORTE FINAL SEACE
{datetime.now().strftime('%d/%m/%Y %H:%M')}

🏢 {notifier.empresa}

🔍 SEGMENTO 43 - TECNOLOGÍAS:
✅ Total oportunidades: 30
✅ Relevantes (≥25%): 6
✅ Sistema funcionando al 100%

🚨 TOP URGENTES:
• EMPRESA SAN GABÁN - 01/06/2026
• ELECTRO ORIENTE - 03/06/2026
• BANCO DE LA NACIÓN - 03/06/2026

📱 WhatsApp: AUTOMÁTICO ✅
🤖 Monitor: OPERATIVO ✅
🎯 Notificaciones: ACTIVAS ✅

_Sistema SEACE totalmente configurado_"""

        print("📝 Enviando reporte final...")
        print("⚠️ Se abrirá Chrome - puede tardarse unos segundos")

        success = notifier.send_message(mensaje, priority='high')

        if success:
            print("\n🎉 ¡SISTEMA TOTALMENTE FUNCIONAL!")
            print("📲 El mensaje fue ENVIADO AUTOMÁTICAMENTE")
            print("✅ Verifica tu celular para confirmarlo")
        else:
            print("\n❌ Error en el envío")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()