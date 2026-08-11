#!/bin/bash
# Script de prueba para el monitor de nuevas oportunidades

echo "================================================================================"
echo "🧪 TEST: Monitor de Nuevas Oportunidades"
echo "================================================================================"
echo ""

# Mostrar estado actual del historial
echo "📊 Estado actual del historial:"
mysql -u root -p123456 seace_monitor -e "
SELECT
    u.nombre,
    u.numero,
    COUNT(h.id) as total_vistas,
    MAX(h.fecha_visto) as ultima_actualizacion
FROM usuarios u
LEFT JOIN historial_oportunidades h ON u.id = h.usuario_id
WHERE u.activo = TRUE
GROUP BY u.id
"

echo ""
echo "================================================================================"
echo "🔧 PASO 1: Seleccionar oportunidad para simular como nueva"
echo "================================================================================"
echo ""

# PRIMERO: Guardar la nomenclatura que vamos a borrar (sin borrar aún)
BORRADA=$(mysql -u root -p123456 seace_monitor -se "
SELECT nomenclatura
FROM historial_oportunidades
WHERE usuario_id = 1
ORDER BY RAND()
LIMIT 1
")

echo "📝 Oportunidad seleccionada: $BORRADA"
echo ""
read -p "¿Borrar esta oportunidad del historial? (s/n): " CONFIRMAR

if [ "$CONFIRMAR" != "s" ]; then
    echo "❌ Cancelado - No se borró nada"
    exit 1
fi

# SEGUNDO: Ahora sí borrar del historial
mysql -u root -p123456 seace_monitor -e "
DELETE FROM historial_oportunidades
WHERE usuario_id = 1
AND nomenclatura = '$BORRADA'
"

echo "✅ Oportunidad borrada del historial"
echo ""

echo "================================================================================"
echo "🔧 PASO 2: Ejecutar monitor en modo test"
echo "================================================================================"
echo ""

# Ejecutar monitor
python3 monitor_nuevas_oportunidades.py --test

echo ""
echo "================================================================================"
echo "✅ TEST COMPLETADO"
echo "================================================================================"
echo ""
echo "📱 Verifica tu WhatsApp para ver si llegó la alerta de: $BORRADA"
echo ""
echo "📊 Para verificar en la base de datos:"
echo "mysql -u root -p123456 seace_monitor -e \"SELECT * FROM historial_oportunidades WHERE nomenclatura = '$BORRADA'\""
echo ""
