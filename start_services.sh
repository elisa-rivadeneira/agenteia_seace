#!/bin/bash
set -e

echo "🚀 Iniciando servicios SEACE..."

echo "📅 Iniciando Scheduler de Alertas..."
python -u scheduler_alertas_v2.py &
SCHEDULER_PID=$!

echo "🌐 Iniciando Webhook Server..."
python -u webhook_server.py &
WEBHOOK_PID=$!

echo "✅ Servicios iniciados:"
echo "   - Scheduler PID: $SCHEDULER_PID"
echo "   - Webhook PID: $WEBHOOK_PID"

wait -n

exit $?
