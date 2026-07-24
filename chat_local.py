#!/usr/bin/env python3
"""
Chat local interactivo con el Agente SEACE
"""
import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    print("⚠️  OPENAI_API_KEY no configurada en .env")
    exit(1)

from agente_whatsapp import AgenteWhatsAppSEACE
from conversaciones_logger import log_conversacion

print("="*80)
print("CHAT LOCAL CON AGENTE SEACE")
print("="*80)
print("\n✅ Inicializando agente con IA...")
agente = AgenteWhatsAppSEACE()

print("\n" + "="*80)
print("💬 CHAT INICIADO")
print("="*80)
print("\nComandos disponibles:")
print("  /escanear - Buscar oportunidades")
print("  /estado - Estado del sistema")
print("  /ayuda - Ver todos los comandos")
print("  exit - Salir del chat")
print("\nO escribe preguntas como:")
print("  ¿Qué oportunidades me recomiendas?")
print("  Analiza las mejores licitaciones")
print("="*80)

while True:
    try:
        print("\n")
        mensaje = input("🧑 Tú: ").strip()

        if not mensaje:
            continue

        if mensaje.lower() in ['exit', 'salir', 'quit']:
            print("\n👋 Hasta luego!")
            break

        print("\n🤖 Agente: Procesando...\n")
        respuesta = agente.procesar_comando(mensaje)

        # Registrar conversación (usando número de prueba)
        log_conversacion("LOCAL_TEST", mensaje, respuesta)

        print("─" * 80)
        print(respuesta)
        print("─" * 80)

    except KeyboardInterrupt:
        print("\n\n👋 Chat terminado!")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}")
