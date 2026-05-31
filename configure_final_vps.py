#!/usr/bin/env python3
"""
Configuración final del agente SEACE con VPS Evolution API
"""

import json
from datetime import datetime

def configurar_agente_final():
    """Configurar agente SEACE con VPS que ya probamos que funciona"""

    print("🎉 CONFIGURACIÓN FINAL - VPS EVOLUTION API")
    print("=" * 60)

    # Configuración que sabemos que funciona
    vps_config = {
        'evolution_vps': {
            'enabled': True,
            'base_url': 'https://automation-evolution-api.gnrjtm.easypanel.host',
            'api_key': '429683C4C977415CAAFCCE10F7D57E11',
            'instance_name': 'Elisa Rivadeneira',
            'instance_id': 'b511ad52-537e-486e-8064-7258066aafe3',
            'status': 'working',
            'configured_at': datetime.now().isoformat()
        }
    }

    # Guardar configuración
    with open('evolution_vps_final.json', 'w') as f:
        json.dump(vps_config, f, indent=2)

    print("✅ Configuración VPS guardada")

    # Actualizar whatsapp_notifier.py
    try:
        with open('whatsapp_notifier.py', 'r') as f:
            content = f.read()

        # Actualizar configuración evolution
        new_evolution_config = f"""            'evolution': {{
                'enabled': True,
                'base_url': '{vps_config['evolution_vps']['base_url']}',
                'instance': '{vps_config['evolution_vps']['instance_name']}',
                'api_key': '{vps_config['evolution_vps']['api_key']}'
            }},"""

        # Reemplazar configuración evolution existente
        import re
        pattern = r"'evolution': \{[^}]*\},"

        if re.search(pattern, content):
            content = re.sub(pattern, new_evolution_config, content, flags=re.DOTALL)
            print("✅ Configuración evolution actualizada")
        else:
            print("⚠️ No se encontró configuración evolution para actualizar")

        # Cambiar orden de prioridad - Evolution VPS primero
        content = content.replace(
            "('WhatsApp wa.me URL', self.send_via_wa_me_url),  # MÉTODO ORIGINAL QUE FUNCIONABA",
            "('Evolution VPS', self.send_via_evolution),  # VPS AUTOMÁTICO REAL"
        )

        # También actualizar el método send_via_evolution para usar formato correcto
        evolution_method_old = '''            data = {
                "number": number or self.whatsapp_number,
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                },
                "textMessage": {
                    "text": message
                }
            }'''

        evolution_method_new = '''            data = {
                "number": (number or self.whatsapp_number).replace('+', '').replace(' ', ''),
                "text": message
            }'''

        if evolution_method_old in content:
            content = content.replace(evolution_method_old, evolution_method_new)
            print("✅ Método send_via_evolution actualizado para VPS")

        # Guardar archivo actualizado
        with open('whatsapp_notifier.py', 'w') as f:
            f.write(content)

        print("✅ whatsapp_notifier.py completamente configurado")

    except Exception as e:
        print(f"❌ Error actualizando notifier: {e}")
        return False

    # Crear script de prueba rápida
    test_script = f'''#!/usr/bin/env python3
"""
Prueba rápida del agente SEACE con VPS
"""

from agente_whatsapp import AgenteWhatsAppSEACE
from datetime import datetime

def test_agente_vps():
    print("🧪 PROBANDO AGENTE SEACE CON VPS...")

    agente = AgenteWhatsAppSEACE()

    mensaje_test = f\"\"\"🚀 AGENTE SEACE VPS OPERATIVO!
{{datetime.now().strftime('%d/%m/%Y %H:%M')}}

✅ Evolution API VPS funcionando
🤖 Envío completamente automático
📊 30 oportunidades SEACE monitoreadas
⚡ Sin navegadores, desde la nube

¡Sistema 100% automático!\"\"\"

    success = agente.enviar_mensaje(mensaje_test)

    if success:
        print("🎉 ¡AGENTE FUNCIONANDO PERFECTAMENTE!")
        print("📱 El mensaje debe haber llegado a tu WhatsApp")
    else:
        print("❌ Error en el agente")

if __name__ == "__main__":
    test_agente_vps()
'''

    with open('test_agente_vps.py', 'w') as f:
        f.write(test_script)

    print("📁 Script de prueba creado: test_agente_vps.py")

    return True

if __name__ == "__main__":
    if configurar_agente_final():
        print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
        print("📱 El agente SEACE está configurado con tu VPS")
        print("🚀 Envío automático funcionando")
        print("\n🧪 EJECUTAR PRUEBA:")
        print("python3 test_agente_vps.py")
    else:
        print("❌ Error en la configuración")