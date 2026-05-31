#!/usr/bin/env python3
"""
Enviar reporte real de oportunidades SEACE por WhatsApp
"""

from whatsapp_notifier import WhatsAppNotifier
import json
from datetime import datetime

def main():
    print("📊 ENVIANDO REPORTE REAL SEACE")
    print("=" * 40)

    # Cargar últimas oportunidades
    with open('seace_todas_oportunidades_20260531_095650.json', 'r') as f:
        data = json.load(f)

    notifier = WhatsAppNotifier()
    oportunidades = data['oportunidades']
    relevantes = [op for op in oportunidades if op.get('score_compatibilidad', 0) >= 25]

    # Top 3 urgentes
    top_urgentes = []
    for op in oportunidades[:3]:
        entidad = op['entidad'][:30] + "..." if len(op['entidad']) > 30 else op['entidad']
        fecha = op['fecha_fin'][:10]
        top_urgentes.append(f"• {entidad} - {fecha}")

    mensaje = f"""📊 REPORTE SEACE - SEGMENTO 43
{datetime.now().strftime('%d/%m/%Y %H:%M')}

🔍 RESUMEN:
• Total oportunidades: {len(oportunidades)}
• Relevantes (≥25%): {len(relevantes)}
• Más compatible: {oportunidades[0]['entidad'][:40]}... ({oportunidades[0].get('score_compatibilidad', 0)}%)

🚨 TOP 3 URGENTES:
{chr(10).join(top_urgentes)}

💼 {notifier.empresa}
🤖 Monitor automático SEACE"""

    print("📝 Mensaje a enviar:")
    print(mensaje)
    print("\n" + "=" * 40)

    print("📱 Enviando reporte actualizado...")
    success = notifier.send_message(mensaje, priority='high')

    if success:
        print("✅ ¡REPORTE ENVIADO EXITOSAMENTE!")
        print("📲 El mensaje llegará a WhatsApp en ~30 segundos")
    else:
        print("❌ Error enviando reporte")

if __name__ == "__main__":
    main()