#!/usr/bin/env python3
"""
Configurar API key de CallMeBot manualmente
"""
import os

def configurar_api_key():
    print("🔑 CONFIGURAR CALLMEBOT API KEY")
    print("=" * 40)

    print("📱 ¿Ya enviaste el mensaje de autorización?")
    print("   'I allow callmebot to send me messages' → +34 644 59 71 67")
    print()

    api_key = input("Pega aquí tu API key de CallMeBot: ").strip()

    if api_key:
        # Guardar en archivo .env
        with open('.env', 'w') as f:
            f.write(f"CALLMEBOT_API_KEY={api_key}\n")

        # Exportar variable de entorno
        os.environ['CALLMEBOT_API_KEY'] = api_key

        print(f"✅ API key guardado: {api_key[:10]}...")
        print("📁 Guardado en archivo .env")

        # Hacer prueba inmediata
        print("\n🧪 PROBANDO ENVÍO REAL...")

        from whatsapp_directo_real import WhatsAppDirectoReal

        whatsapp = WhatsAppDirectoReal("+51967717179")

        mensaje_prueba = f"""🎉 CALLMEBOT CONFIGURADO!

🤖 El agente SEACE puede enviarte mensajes automáticos
✅ Sistema funcionando correctamente
📱 Sin navegadores necesarios

¡Listo para usar! 🚀"""

        success = whatsapp.enviar_mensaje_real(mensaje_prueba, callmebot_key=api_key)

        if success:
            print("\n🎉 ¡PERFECTO! Revisa tu WhatsApp")
            print("✅ El sistema ya puede enviarte mensajes automáticos")

            # Actualizar el agente principal
            print("\n🔄 Actualizando configuración del agente...")
            return True
        else:
            print("\n⚠️ Error en la prueba, verifica el API key")
            return False

    else:
        print("❌ No se ingresó API key")
        return False

if __name__ == "__main__":
    configurar_api_key()