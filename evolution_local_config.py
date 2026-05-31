#!/usr/bin/env python3
"""
Configuración Evolution API local - Usando la instancia existente
"""

import requests
import json
from datetime import datetime

def configurar_evolution_local():
    """Configura Evolution API local con la instancia existente"""

    print("🔗 CONFIGURANDO EVOLUTION API LOCAL")
    print("=" * 50)

    # Configuración basada en el screenshot
    config = {
        'base_url': 'http://localhost:8080',
        'api_key': '429683C4C977415CAAFCCE10F7D57E11',  # Del .env
        'instance_name': 'ElisaRivadaneira',  # Basado en la instancia visible
        'instance_id': 'D1E66A0B73B1-45DC-B083-392928F636D0'
    }

    print(f"🌐 URL: {config['base_url']}")
    print(f"📱 Instancia: {config['instance_name']}")
    print(f"🔑 Instance ID: {config['instance_id'][:20]}...")

    # Verificar que la instancia esté conectada
    try:
        url = f"{config['base_url']}/instance/connectionState/{config['instance_name']}"
        headers = {'apikey': config['api_key']}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            state = response.json()
            status = state.get('instance', {}).get('state', 'unknown')
            print(f"✅ Estado de conexión: {status}")

            if status != 'open':
                print("⚠️ La instancia no está conectada")
                print("💡 Ve a Evolution Manager y conecta la instancia")
                return False

        else:
            print(f"❌ Error verificando estado: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return False

    # Test de envío
    print("\n🧪 PROBANDO ENVÍO AUTOMÁTICO...")

    try:
        url = f"{config['base_url']}/message/sendText/{config['instance_name']}"

        headers = {
            'Content-Type': 'application/json',
            'apikey': config['api_key']
        }

        data = {
            "number": "51967717179",
            "options": {
                "delay": 1200,
                "presence": "composing"
            },
            "textMessage": {
                "text": f"""🎉 EVOLUTION API LOCAL FUNCIONANDO!
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Instancia: {config['instance_name']}
🤖 Envío automático real
📊 Sistema SEACE operativo

¡Sin navegadores, completamente automático!"""
            }
        }

        print(f"📤 Enviando a +51967717179...")
        response = requests.post(url, json=data, headers=headers, timeout=30)

        if response.status_code == 201:
            result = response.json()
            print("✅ ¡MENSAJE ENVIADO AUTOMÁTICAMENTE!")
            print(f"📱 Message ID: {result.get('key', {}).get('id', 'N/A')}")

            # Guardar configuración exitosa
            with open('evolution_local_config.json', 'w') as f:
                json.dump(config, f, indent=2)

            print("💾 Configuración guardada en evolution_local_config.json")
            return True

        else:
            print(f"❌ Error enviando: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

def actualizar_agente_seace():
    """Actualiza el agente SEACE para usar Evolution API local"""

    print("\n🔄 ACTUALIZANDO AGENTE SEACE...")

    # Leer configuración de Evolution
    try:
        with open('evolution_local_config.json', 'r') as f:
            evolution_config = json.load(f)
    except:
        print("❌ No se encontró configuración de Evolution")
        return False

    # Actualizar whatsapp_notifier.py
    try:
        # Leer archivo actual
        with open('whatsapp_notifier.py', 'r') as f:
            content = f.read()

        # Actualizar configuración de Evolution API
        new_evolution_config = f"""
            'evolution': {{
                'enabled': True,
                'base_url': '{evolution_config['base_url']}',
                'instance': '{evolution_config['instance_name']}',
                'api_key': '{evolution_config['api_key']}'
            }},"""

        # Buscar y reemplazar la configuración
        import re
        pattern = r"'evolution': \{[^}]*\},"

        if re.search(pattern, content):
            content = re.sub(pattern, new_evolution_config, content, flags=re.DOTALL)
        else:
            print("⚠️ No se encontró configuración evolution en whatsapp_notifier.py")
            return False

        # Guardar archivo actualizado
        with open('whatsapp_notifier.py', 'w') as f:
            f.write(content)

        print("✅ whatsapp_notifier.py actualizado")

        # También cambiar el orden de prioridad para que Evolution API sea primero
        content = content.replace(
            "('WhatsApp wa.me URL', self.send_via_wa_me_url),  # MÉTODO ORIGINAL QUE FUNCIONABA",
            "('Evolution API', self.send_via_evolution),  # MÉTODO AUTOMÁTICO REAL"
        )

        with open('whatsapp_notifier.py', 'w') as f:
            f.write(content)

        print("✅ Prioridad de Evolution API configurada")
        return True

    except Exception as e:
        print(f"❌ Error actualizando agente: {e}")
        return False

def main():
    """Configuración completa"""

    if configurar_evolution_local():
        print("\n✅ Evolution API local configurado correctamente")

        if actualizar_agente_seace():
            print("\n🎉 ¡AGENTE SEACE COMPLETAMENTE CONFIGURADO!")
            print("📱 Ahora todos los mensajes llegan automáticamente")
            print("🚀 Sin navegadores, sin intervención manual")

            print("\n🧪 PRUEBA FINAL:")
            print("python3 -c \"from agente_whatsapp import AgenteWhatsAppSEACE; agente=AgenteWhatsAppSEACE(); agente.enviar_mensaje('¡Sistema completamente automático!')\"")
        else:
            print("⚠️ Error configurando agente")
    else:
        print("❌ Error configurando Evolution API")

if __name__ == "__main__":
    main()