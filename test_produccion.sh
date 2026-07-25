#!/bin/bash
# Test para verificar que el servicio de producción está respondiendo

echo "=========================================="
echo "TEST DE SERVICIO EN PRODUCCIÓN"
echo "=========================================="

echo -e "\n1. Verificando status del servicio..."
curl -s https://automation-agente-seace.gnrjtm.easypanel.host/status | python3 -m json.tool

echo -e "\n\n2. Simulando webhook de /escanear..."
curl -X POST https://automation-agente-seace.gnrjtm.easypanel.host/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "service_reloaded_otronumber",
    "data": {
      "key": {
        "remoteJid": "51999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "test-message-1"
      },
      "message": {
        "conversation": "/escanear"
      },
      "messageTimestamp": "1234567890"
    }
  }'

echo -e "\n\n3. Esperando 5 segundos..."
sleep 5

echo -e "\n4. Verificando últimos mensajes procesados..."
curl -s https://automation-agente-seace.gnrjtm.easypanel.host/messages | python3 -m json.tool

echo -e "\n\n=========================================="
echo "PRUEBA COMPLETADA"
echo "=========================================="
