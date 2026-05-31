#!/usr/bin/env python3
"""
Script de prueba para notificaciones WhatsApp
"""

from whatsapp_notifier import WhatsAppNotifier
from datetime import datetime

def test_whatsapp_notification():
    """Prueba básica de notificación WhatsApp"""

    print("🧪 PROBANDO NOTIFICACIÓN WHATSAPP")
    print("=" * 50)

    try:
        # Inicializar notificador
        notifier = WhatsAppNotifier()
        print(f"✅ Notificador inicializado para: {notifier.empresa}")
        print(f"📱 Número objetivo: {notifier.whatsapp_number}")

        # Mensaje de prueba
        mensaje_prueba = f"""📊 *PRUEBA SEACE MONITOR*

🏢 *Empresa:* {notifier.empresa}
📅 *Fecha:* {datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Sistema de notificaciones WhatsApp configurado correctamente

🔍 *Estado del monitor:* Activo
🎯 *Segmento:* 43 - Tecnologías de la Información
📈 *Oportunidades detectadas:* 30

_Este es un mensaje de prueba del sistema SEACE_"""

        print("\n📝 Mensaje a enviar:")
        print(mensaje_prueba)
        print("\n" + "=" * 50)

        # Enviar mensaje
        success = notifier.send_message(mensaje_prueba, priority='high')

        if success:
            print("\n✅ ¡MENSAJE ENVIADO EXITOSAMENTE!")
            print("📲 Revisa tu WhatsApp para confirmar la recepción")
        else:
            print("\n❌ ERROR: No se pudo enviar el mensaje")
            print("💡 Verifica:")
            print("   - Que WhatsApp Web esté cerrado")
            print("   - Conexión a internet")
            print("   - Número en config_empresa.json")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_with_real_opportunity():
    """Prueba con datos reales de oportunidad"""

    notifier = WhatsAppNotifier()

    # Oportunidad de ejemplo basada en datos reales
    oportunidad_ejemplo = {
        'entidad': 'MUNICIPALIDAD DISTRITAL DE LA MOLINA',
        'nomenclatura': 'LP-SM-4-2026-MDLM-1',
        'descripcion_procedimiento': 'ADQUISICION DE SERVIDOR DE ALMACENAMIENTO PARA VIDEOCAMARAS DE SEGURIDAD DE ALTA DISPONIBILIDAD Y CAMARA CORPORAL CON ANALITICA',
        'fecha_fin': '15/06/2026 23:59:00',
        'valor': '---',
        'score_compatibilidad': 40
    }

    mensaje = notifier.format_oportunidad(oportunidad_ejemplo)
    print("\n📋 PRUEBA CON OPORTUNIDAD REAL:")
    print("=" * 50)
    print(mensaje)

    enviar = input("\n¿Enviar esta notificación? (s/N): ").lower().strip()
    if enviar == 's':
        success = notifier.send_message(mensaje, priority='urgent')
        if success:
            print("✅ Notificación de oportunidad enviada!")
        else:
            print("❌ Error enviando notificación")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE WHATSAPP")
    print("=" * 50)

    opcion = input("""
Selecciona una prueba:
1. Mensaje básico de prueba
2. Notificación con oportunidad real
3. Ambas

Opción (1-3): """).strip()

    if opcion in ['1', '3']:
        test_whatsapp_notification()

    if opcion in ['2', '3']:
        test_with_real_opportunity()

    print("\n🏁 Pruebas completadas")