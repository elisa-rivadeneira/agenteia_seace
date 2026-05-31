#!/usr/bin/env python3
"""
Setup rápido de Twilio para WhatsApp autónomo inmediato
"""
import os

def setup_twilio():
    print("🚀 TWILIO - WHATSAPP AUTÓNOMO INMEDIATO")
    print("=" * 50)
    print("💰 Costo: ~$0.05 por mensaje")
    print("⚡ Sin autorizaciones previas")
    print("✅ 100% autónomo desde el primer mensaje")
    print()

    print("📋 PASOS RÁPIDOS:")
    print("1. Ve a: https://console.twilio.com")
    print("2. Crea cuenta gratuita (incluye $15 de crédito)")
    print("3. Ve a WhatsApp Sandbox")
    print("4. Copia tus credenciales aquí")
    print()

    account_sid = input("Account SID: ").strip()
    auth_token = input("Auth Token: ").strip()

    if account_sid and auth_token:
        # Guardar credenciales
        with open('.env', 'a') as f:
            f.write(f"\nTWILIO_ACCOUNT_SID={account_sid}")
            f.write(f"\nTWILIO_AUTH_TOKEN={auth_token}")
            f.write(f"\nTWILIO_FROM_NUMBER=whatsapp:+14155238886")

        print("✅ Credenciales guardadas")

        # Probar inmediatamente
        print("\n🧪 PROBANDO ENVÍO INMEDIATO...")

        try:
            from twilio.rest import Client

            client = Client(account_sid, auth_token)

            message = client.messages.create(
                body="🎉 TWILIO CONFIGURADO! Agente SEACE puede enviar mensajes automáticos sin intervención manual ✅",
                from_='whatsapp:+14155238886',
                to='whatsapp:+51967717179'
            )

            print("🎉 ¡MENSAJE ENVIADO AUTOMÁTICAMENTE!")
            print(f"📱 ID: {message.sid}")
            print("✅ Sistema completamente autónomo")

        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Verifica las credenciales y el sandbox de WhatsApp")
    else:
        print("❌ Credenciales incompletas")

if __name__ == "__main__":
    setup_twilio()