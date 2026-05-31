#!/usr/bin/env python3
"""
Script rápido para enviar notificación por WhatsApp Web usando pywhatkit
No requiere APIs externas - usa WhatsApp Web directamente
"""

import json
from datetime import datetime

def enviar_notificacion_rapida():
    # Cargar última extracción
    with open('seace_todas_oportunidades_20260525_212224.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    oportunidades = data['oportunidades']

    # Filtrar las más relevantes
    relevantes = sorted(oportunidades, key=lambda x: x.get('score_compatibilidad', 0), reverse=True)[:5]

    # Crear mensaje
    mensaje = f"""
🔔 REPORTE SEACE - {datetime.now().strftime('%d/%m %H:%M')}

📊 Encontradas: {len(oportunidades)} oportunidades
✅ Top 5 más compatibles:

"""

    for i, op in enumerate(relevantes[:5], 1):
        mensaje += f"{i}. {op['entidad'][:30]}... ({op['score_compatibilidad']}%)\n"
        mensaje += f"   📅 Vence: {op['fecha_fin']}\n\n"

    # Identificar urgentes
    urgentes = []
    for op in oportunidades:
        if "26/05/2026" in op['fecha_fin'] or "25/05/2026" in op['fecha_fin']:
            urgentes.append(op)

    if urgentes:
        mensaje += f"\n🚨 URGENTES (vencen mañana):\n"
        for op in urgentes[:3]:
            mensaje += f"• {op['entidad'][:40]}...\n"

    mensaje += "\n💼 SEACE Buscador de Oportunidades"

    print("="*60)
    print("MENSAJE A ENVIAR POR WHATSAPP")
    print("="*60)
    print(mensaje)
    print("="*60)

    # Opción 1: Usando pywhatkit (requiere navegador abierto)
    print("\n📱 Para enviar este mensaje:")
    print("\n1. OPCIÓN RÁPIDA - Copiar y pegar:")
    print(f"   - Abre WhatsApp Web: https://web.whatsapp.com")
    print(f"   - Busca tu número: +51967717179")
    print(f"   - Pega el mensaje de arriba")

    print("\n2. OPCIÓN AUTOMÁTICA con pywhatkit:")
    print("   pip install pywhatkit")
    print("   Luego ejecuta el código siguiente:")

    # Generar código para envío
    codigo = f"""
import pywhatkit as kit
import datetime

# Obtener hora actual + 2 minutos
ahora = datetime.datetime.now()
hora = ahora.hour
minuto = ahora.minute + 2

mensaje = '''{mensaje}'''

# Enviar mensaje (abrirá WhatsApp Web)
kit.sendwhatmsg("+51967717179", mensaje, hora, minuto)
print("✅ Mensaje programado para envío en 2 minutos")
"""

    # Guardar código
    with open('enviar_whatsapp.py', 'w', encoding='utf-8') as f:
        f.write(codigo)

    print("\n💾 Código guardado en: enviar_whatsapp.py")
    print("   Ejecuta: python3 enviar_whatsapp.py")

    # Opción 3: URL de WhatsApp
    import urllib.parse
    mensaje_url = urllib.parse.quote(mensaje)
    url = f"https://wa.me/51967717179?text={mensaje_url}"

    print(f"\n3. OPCIÓN WEB - Click en este enlace:")
    print(f"   {url[:100]}...")

    # Guardar URL completa
    with open('whatsapp_url.txt', 'w') as f:
        f.write(url)
    print("   URL completa guardada en: whatsapp_url.txt")

    return mensaje

if __name__ == "__main__":
    enviar_notificacion_rapida()