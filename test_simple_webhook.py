#!/usr/bin/env python3
"""
Test simple del webhook - envía mensaje y espera respuesta
"""
import requests
import json
import time

webhook_payload = {
    "event": "messages.upsert",
    "instance": "test-instance",
    "data": {
        "key": {
            "remoteJid": "51999999999@s.whatsapp.net",
            "fromMe": False,
            "id": "test-message-1"
        },
        "message": {
            "conversation": "/escanear"
        },
        "messageTimestamp": "1234567890"
    }
}

print("📤 Enviando comando /escanear al webhook...")
response = requests.post(
    'http://localhost:5000/webhook',
    json=webhook_payload,
    headers={'Content-Type': 'application/json'}
)

print(f"✅ Status: {response.status_code}")
print(f"📝 Response: {response.text}")
print("\n⏳ Esperando 30 segundos para que procese...")
time.sleep(30)
print("✅ Revisa los logs del servidor arriba")
