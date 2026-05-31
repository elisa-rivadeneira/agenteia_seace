#!/usr/bin/env python3
"""
Setup completo: Webhook Server + Ngrok + Evolution API
"""

import subprocess
import requests
import time
import json
import threading

def configurar_evolution_webhook():
    """Configurar webhook en Evolution API"""

    print("🔧 CONFIGURACIÓN EVOLUTION API WEBHOOK")
    print("=" * 50)

    # Configuración
    evolution_url = "https://automation-evolution-api.gnrjtm.easypanel.host"
    api_key = "429683C4C977415CAAFCCE10F7D57E11"
    instance_name = "Elisa Rivadeneira"

    print(f"📱 Instancia: {instance_name}")
    print("⏳ Esperando ngrok tunnel...")

    # Esperar a que el usuario proporcione la URL de ngrok
    ngrok_url = input("🌐 Pega aquí tu URL de ngrok (ej: https://xxx.ngrok.io): ").strip()

    if not ngrok_url:
        print("❌ URL de ngrok requerida")
        return False

    webhook_url = f"{ngrok_url}/webhook"

    print(f"🔗 Configurando webhook: {webhook_url}")

    # Configurar webhook en Evolution API
    try:
        url = f"{evolution_url}/webhook/set/{instance_name}"

        headers = {
            'Content-Type': 'application/json',
            'apikey': api_key
        }

        webhook_config = {
            "url": webhook_url,
            "events": [
                "APPLICATION_STARTUP",
                "QRCODE_UPDATED",
                "MESSAGES_SET",
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE"
            ],
            "webhook_by_events": False,
            "webhook_base64": False
        }

        response = requests.post(url, json=webhook_config, headers=headers, timeout=30)

        if response.status_code in [200, 201]:
            print("✅ Webhook configurado exitosamente")
            print(f"📨 Evolution API enviará eventos a: {webhook_url}")
            return True
        else:
            print(f"❌ Error configurando webhook: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verificar_conexion_instancia():
    """Verificar que la instancia esté conectada"""

    print("\n🔍 VERIFICANDO CONEXIÓN INSTANCIA...")

    evolution_url = "https://automation-evolution-api.gnrjtm.easypanel.host"
    api_key = "429683C4C977415CAAFCCE10F7D57E11"
    instance_name = "Elisa Rivadeneira"

    try:
        url = f"{evolution_url}/instance/connectionState/{instance_name}"
        headers = {'apikey': api_key}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            state = data.get('instance', {}).get('state', 'unknown')

            print(f"📱 Estado instancia: {state}")

            if state == 'open':
                print("✅ Instancia conectada y lista")
                return True
            else:
                print("⚠️ Instancia no conectada")
                print("💡 Ve a tu Evolution API y escanea el QR code")
                return False
        else:
            print(f"❌ Error verificando estado: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_sistema_completo():
    """Test del sistema completo"""

    print("\n🧪 PROBANDO SISTEMA COMPLETO...")

    # Test 1: Verificar webhook server
    try:
        response = requests.get("http://localhost:5000/status", timeout=5)
        if response.status_code == 200:
            print("✅ Webhook server funcionando")
        else:
            print("❌ Webhook server no responde")
            return False
    except Exception:
        print("❌ Webhook server no está corriendo")
        return False

    # Test 2: Enviar mensaje de prueba
    try:
        test_data = {
            "message": "🧪 TEST SISTEMA COMPLETO\n\n✅ Webhook configurado\n🤖 Agente SEACE operativo\n📱 Evolution API conectado\n\n¡Sistema funcionando!",
            "number": "51967717179"
        }

        response = requests.post("http://localhost:5000/send", json=test_data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Mensaje de prueba enviado")
                print("📱 Revisa tu WhatsApp")
                return True
            else:
                print(f"❌ Error enviando: {result.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

def main():
    """Setup principal"""

    print("🚀 SETUP WEBHOOK EVOLUTION API + AGENTE SEACE")
    print("=" * 60)

    print("📋 PASOS PARA CONFIGURAR:")
    print("1. Iniciar webhook server (puerto 5000)")
    print("2. Exponer con ngrok")
    print("3. Configurar webhook en Evolution API")
    print("4. Verificar instancia conectada")
    print("5. Probar sistema completo")

    print("\n🎯 COMANDOS A EJECUTAR:")
    print("Terminal 1: python3 webhook_server.py")
    print("Terminal 2: ngrok http 5000")
    print("Terminal 3: python3 setup_webhook_completo.py")

    input("\nPresiona Enter cuando tengas webhook server y ngrok corriendo...")

    if verificar_conexion_instancia():
        if configurar_evolution_webhook():
            print("\n⏳ Esperando 5 segundos para que se active...")
            time.sleep(5)

            if test_sistema_completo():
                print("\n🎉 ¡SISTEMA COMPLETAMENTE CONFIGURADO!")
                print("📱 Ahora puedes enviar mensajes a tu WhatsApp")
                print("🤖 El agente responderá automáticamente")
                print("\n📋 COMANDOS DISPONIBLES VIA WHATSAPP:")
                print("• /estado - Estado del sistema")
                print("• /escanear - Buscar oportunidades")
                print("• /urgentes - Oportunidades urgentes")
                print("• /reporte - Reporte completo")
                print("• estado, urgentes, reporte (lenguaje natural)")
            else:
                print("❌ Error en test del sistema")
        else:
            print("❌ Error configurando webhook")
    else:
        print("❌ Instancia no está conectada")

if __name__ == "__main__":
    main()