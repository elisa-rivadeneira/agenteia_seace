#!/usr/bin/env python3
"""
Activar Agente SEACE - Script simple para iniciar comunicación
"""

from agente_whatsapp import AgenteWhatsAppSEACE
from datetime import datetime

def activar_agente():
    """Activa el agente y envía mensaje de bienvenida"""
    print("🚀 ACTIVANDO AGENTE WHATSAPP SEACE")
    print("=" * 50)

    try:
        # Crear agente
        agente = AgenteWhatsAppSEACE()

        # Mensaje de activación personalizado
        mensaje_activacion = f"""🤖 *AGENTE SEACE ACTIVADO*
{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

¡Hola! Tu asistente inteligente SEACE está ahora ACTIVO y listo para conversar.

🎯 *YA PUEDES:*
• Escribir "/escanear" para buscar oportunidades
• Escribir "/reporte" para ver resumen completo
• Escribir "/urgentes" para ver solo las urgentes
• Preguntar "¿Cuántas oportunidades hay?"
• Escribir "/ayuda" para ver todos los comandos

📊 *ESTADO INICIAL:*
• Sistema: ✅ Operativo
• Empresa: {agente.notifier.empresa[:25]}...
• Segmento: 43 - Tecnologías TI
• Monitoreo: 🔄 Automático cada 30 min

💬 *EJEMPLOS DE USO:*
• "/estado" → Ver estado del sistema
• "/config" → Ver configuración actual
• "Quiero ver las urgentes" → Consulta natural

🚨 *¡RESPONDERÉ AUTOMÁTICAMENTE A TUS MENSAJES!*

_Solo escribe cualquier comando o pregunta_"""

        print("📝 Mensaje de activación preparado:")
        print("-" * 40)
        print(mensaje_activacion[:300] + "..." if len(mensaje_activacion) > 300 else mensaje_activacion)
        print("-" * 40)

        # Enviar mensaje
        print("\n📤 Enviando mensaje de activación...")

        success = agente.enviar_mensaje(mensaje_activacion)

        if success:
            print("✅ ¡AGENTE ACTIVADO EXITOSAMENTE!")
            print("📲 Revisa tu WhatsApp - el agente ya está operativo")
            print("\n🎯 PRÓXIMOS PASOS:")
            print("1. Ve a WhatsApp en tu celular")
            print("2. Verifica que llegó el mensaje de activación")
            print("3. Responde con cualquier comando (ej: /estado)")
            print("4. ¡El agente responderá automáticamente!")

            # Información sobre el monitor completo
            print(f"\n🔄 PARA CONVERSACIONES AUTOMÁTICAS:")
            print("   python3 monitor_whatsapp.py")
            print("   (Esto habilita respuesta automática a TODOS tus mensajes)")

        else:
            print("❌ Error activando agente")
            print("💡 Verifica que WhatsApp Web funcione correctamente")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def enviar_comando_demo():
    """Envía comandos de demostración"""
    print("\n📋 ENVIANDO COMANDOS DE DEMO")
    print("=" * 40)

    agente = AgenteWhatsAppSEACE()

    comandos_demo = [
        ("/estado", "Estado del sistema"),
        ("/escanear", "Buscar nuevas oportunidades"),
        ("/reporte", "Reporte completo")
    ]

    for comando, descripcion in comandos_demo:
        print(f"\n📤 Enviando: {comando} ({descripcion})")

        # Procesar comando localmente primero
        respuesta = agente.procesar_comando(comando)
        print(f"🤖 Respuesta: {respuesta[:100]}...")

        # Enviar por WhatsApp
        success = agente.enviar_mensaje(f"Demo: {comando}\n\n{respuesta}")

        if success:
            print("✅ Enviado por WhatsApp")
        else:
            print("❌ Error enviando")

        time.sleep(3)  # Pausa entre mensajes

if __name__ == "__main__":
    print("🤖 AGENTE WHATSAPP SEACE - ACTIVACIÓN")
    print("=" * 50)

    try:
        opcion = input("""
Selecciona una opción:
1. Activar agente (mensaje de bienvenida)
2. Enviar comandos de demostración
3. Solo mostrar mensaje de activación

Opción (1-3): """).strip()
    except:
        opcion = "1"  # Default

    if opcion == "1":
        activar_agente()
    elif opcion == "2":
        enviar_comando_demo()
    elif opcion == "3":
        # Solo mostrar el mensaje
        agente = AgenteWhatsAppSEACE()
        mensaje = agente.procesar_comando("/inicio")
        print("\nMensaje de activación:")
        print("=" * 40)
        print(mensaje)
    else:
        print("Opción no válida")
        activar_agente()  # Default