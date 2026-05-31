
import pywhatkit as kit
import datetime

# Obtener hora actual + 2 minutos
ahora = datetime.datetime.now()
hora = ahora.hour
minuto = ahora.minute + 2

mensaje = '''
🔔 REPORTE SEACE - 26/05 06:48

📊 Encontradas: 25 oportunidades
✅ Top 5 más compatibles:

1. UNIVERSIDAD NACIONAL JOSE F. S... (45%)
   📅 Vence: 26/05/2026 23:59:00

2. MUNICIPALIDAD DISTRITAL DE LA ... (40%)
   📅 Vence: 15/06/2026 23:59:00

3. EMPRESA DE GENERACION ELECTRIC... (35%)
   📅 Vence: 31/05/2026 23:59:00

4. EMPRESA REGIONAL DE SERVICIOS ... (25%)
   📅 Vence: 31/05/2026 23:59:00

5. GOBIERNO REGIONAL DE MOQUEGUA ... (25%)
   📅 Vence: 07/06/2026 23:59:00


🚨 URGENTES (vencen mañana):
• UNIVERSIDAD NACIONAL JOSE F. SANCHEZ CAR...
• MINAG - PROYECTO ESPECIAL BINACIONAL DES...
• MUNICIPALIDAD DISTRITAL DE SAMEGUA...

💼 SEACE Buscador de Oportunidades'''

# Enviar mensaje (abrirá WhatsApp Web)
kit.sendwhatmsg("+51967717179", mensaje, hora, minuto)
print("✅ Mensaje programado para envío en 2 minutos")
