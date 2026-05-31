#!/usr/bin/env python3
"""
Configurar CallMeBot para envío directo de WhatsApp
"""

import os
import webbrowser

def configurar_callmebot():
    """Guía para configurar CallMeBot"""
    print("🔑 CONFIGURAR CALLMEBOT - WHATSAPP DIRECTO")
    print("=" * 50)

    print("📱 CallMeBot permite enviar WhatsApp SIN navegadores")
    print("Es GRATIS y muy fácil de configurar")

    print("\n📋 PASOS PARA CONFIGURAR:")
    print("1. Abre WhatsApp en tu celular")
    print("2. Agrega el contacto: +34 644 59 71 67")
    print("3. Envía este mensaje EXACTO:")
    print("   'I allow callmebot to send me messages'")
    print("4. Espera la respuesta con tu API key")

    print(f"\n📲 Tu número registrado será: +51967717179")

    # Abrir WhatsApp Web para facilitar el proceso
    mensaje_autorizacion = "I allow callmebot to send me messages"
    contact_number = "34644597167"

    whatsapp_url = f"https://web.whatsapp.com/send?phone={contact_number}&text={mensaje_autorizacion.replace(' ', '%20')}"

    print(f"\n🚀 OPCIÓN RÁPIDA:")
    print("Abriendo WhatsApp Web con el mensaje preparado...")

    webbrowser.open(whatsapp_url)

    print("\n✅ WhatsApp Web abierto")
    print("💡 Solo haz clic en ENVIAR")
    print("⏳ Espera la respuesta con tu API key")

    print("\n🔐 CUANDO RECIBAS TU API KEY:")
    api_key = input("Pega tu API key aquí (o Enter para omitir): ").strip()

    if api_key:
        # Guardar en variable de entorno
        os.environ['CALLMEBOT_API_KEY'] = api_key

        # También guardarlo en un archivo
        with open('.env', 'w') as f:
            f.write(f"CALLMEBOT_API_KEY={api_key}\n")

        print(f"✅ API key guardado: {api_key[:10]}...")

        # Hacer prueba
        print("\n🧪 Probando envío...")

        from whatsapp_notifier import WhatsAppNotifier

        notifier = WhatsAppNotifier()
        mensaje_prueba = "🎉 CallMeBot configurado correctamente! El sistema SEACE puede enviar mensajes automáticamente."

        success = notifier.send_message(mensaje_prueba)

        if success:
            print("🎉 ¡CALLMEBOT FUNCIONANDO!")
            print("📱 Revisa tu WhatsApp - debe haber llegado el mensaje")
        else:
            print("⚠️ Prueba el API key manualmente")

    else:
        print("⏳ Configura el API key cuando lo recibas:")
        print("   export CALLMEBOT_API_KEY='tu_api_key_aqui'")

    print(f"\n📋 RESUMEN:")
    print("✅ Mensaje de autorización preparado")
    print("✅ Proceso de configuración iniciado")
    print("⏳ Esperando API key de CallMeBot")

def test_callmebot_directo():
    """Prueba CallMeBot con API key"""
    api_key = os.getenv('CALLMEBOT_API_KEY')

    if not api_key:
        print("❌ No hay API key de CallMeBot configurado")
        print("🔧 Ejecuta: python3 configurar_callmebot.py")
        return

    print("🧪 PROBANDO CALLMEBOT DIRECTO")
    print("=" * 40)

    import requests
    from datetime import datetime

    phone = "51967717179"
    mensaje = f"""🤖 AGENTE SEACE - CALLMEBOT
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Sistema directo funcionando!
📊 30 oportunidades monitoreadas
🚀 Sin navegadores necesarios

_Enviado por CallMeBot API_"""

    url = "https://api.callmebot.com/whatsapp.php"
    params = {
        'phone': phone,
        'text': mensaje,
        'apikey': api_key
    }

    try:
        print(f"📤 Enviando a +51{phone}...")
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            print("✅ ¡MENSAJE ENVIADO DIRECTAMENTE!")
            print("📱 Revisa tu WhatsApp - debe haber llegado")
            print("🎉 Sistema CallMeBot 100% operativo")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")

    except Exception as e:
        print(f"❌ Error enviando: {e}")

if __name__ == "__main__":
    print("🤖 CONFIGURACIÓN CALLMEBOT")
    print("=" * 40)

    if os.getenv('CALLMEBOT_API_KEY'):
        print("✅ API key encontrado")
        test_callmebot_directo()
    else:
        print("🔧 Configurando CallMeBot...")
        configurar_callmebot()