#!/bin/bash
set -e

echo "🚀 Iniciando servicios SEACE..."

echo "📅 Iniciando Scheduler de Alertas Programadas..."
python -u scheduler_alertas_v2.py &
SCHEDULER_PID=$!

echo "🚨 Iniciando Monitor EDITH (Alertas en Tiempo Real)..."
python -u monitor_realtime.py &
MONITOR_PID=$!

echo "🌐 Iniciando Webhook Server..."
python -u webhook_server.py &
WEBHOOK_PID=$!

echo "✅ Servicios iniciados:"
echo "   - Scheduler Alertas: $SCHEDULER_PID"
echo "   - Monitor EDITH: $MONITOR_PID"
echo "   - Webhook Server: $WEBHOOK_PID"

wait -n

exit $?
