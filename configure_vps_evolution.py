#!/usr/bin/env python3
"""
Configurar Evolution API VPS con URL proporcionada
"""

import requests
import json
from datetime import datetime

def configurar_con_vps():
    """Configurar con la URL del VPS proporcionada"""

    print("🚀 CONFIGURANDO EVOLUTION API VPS")
    print("=" * 50)

    # Configuración del VPS
    vps_url = "https://automation-evolution-api.gnrjtm.easypanel.host"
    api_key = "429683C4C977415CAAFCCE10F7D57E11"  # API key estándar
    instance_name = "ElisaRivadaneira"

    print(f"🌐 VPS URL: {vps_url}")
    print(f"📱 Instancia: {instance_name}")

    # Test de conexión
    try:
        print("\n1️⃣ Probando conexión con VPS...")
        response = requests.get(f"{vps_url}/instance/fetchInstances",
                              headers={'apikey': api_key}, timeout=10)

        if response.status_code == 200:
            instances = response.json()
            print(f"✅ Conexión exitosa - {len(instances)} instancias encontradas")

            # Buscar nuestra instancia
            target_instance = None
            for instance in instances:
                if instance.get('instanceName') == instance_name:
                    target_instance = instance
                    break

            if target_instance:
                print(f"✅ Instancia '{instance_name}' encontrada")
                state = target_instance.get('connectionStatus', {}).get('state', 'unknown')
                print(f"📱 Estado: {state}")

                if state != 'open':
                    print(f"⚠️ Instancia no está conectada (estado: {state})")
                    print("💡 Ve a tu VPS y conecta la instancia de WhatsApp")
                    return False
            else:
                print(f"⚠️ Instancia '{instance_name}' no encontrada")
                print("📋 Instancias disponibles:")
                for inst in instances:
                    print(f"  - {inst.get('instanceName', 'Sin nombre')}")
                return False

        else:
            print(f"❌ Error de conexión: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error conectando al VPS: {e}")
        return False

    # Test de envío
    print("\n2️⃣ Probando envío de mensaje...")
    try:
        url = f"{vps_url}/message/sendText/{instance_name}"

        headers = {
            'Content-Type': 'application/json',
            'apikey': api_key
        }

        mensaje = f"""🎉 VPS EVOLUTION API FUNCIONANDO!
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ URL: {vps_url}
🤖 Envío automático desde VPS
📊 Agente SEACE configurado
📱 Sin navegadores locales

¡Sistema completamente automático!"""

        data = {
            "number": "51967717179",
            "options": {
                "delay": 1200,
                "presence": "composing"
            },
            "textMessage": {
                "text": mensaje
            }
        }

        print("📤 Enviando mensaje de prueba...")
        response = requests.post(url, json=data, headers=headers, timeout=30)

        if response.status_code == 201:
            result = response.json()
            print("✅ ¡MENSAJE ENVIADO AUTOMÁTICAMENTE DESDE VPS!")
            print(f"📱 Message ID: {result.get('key', {}).get('id', 'N/A')}")

            # Guardar configuración
            config = {
                'evolution_vps': {
                    'enabled': True,
                    'base_url': vps_url,
                    'api_key': api_key,
                    'instance_name': instance_name,
                    'configured_at': datetime.now().isoformat(),
                    'status': 'working'
                }
            }

            with open('evolution_vps_config.json', 'w') as f:
                json.dump(config, f, indent=2)

            print("💾 Configuración guardada en evolution_vps_config.json")
            return True

        else:
            print(f"❌ Error enviando mensaje: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en envío: {e}")
        return False

def actualizar_agente_seace():
    """Actualizar agente SEACE para usar VPS"""

    print("\n3️⃣ Actualizando agente SEACE...")

    try:
        # Leer configuración del VPS
        with open('evolution_vps_config.json', 'r') as f:
            config = json.load(f)

        vps_config = config['evolution_vps']

        # Actualizar whatsapp_notifier.py
        with open('whatsapp_notifier.py', 'r') as f:
            content = f.read()

        # Actualizar configuración de Evolution API
        new_config = f"""            'evolution': {{
                'enabled': True,
                'base_url': '{vps_config['base_url']}',
                'instance': '{vps_config['instance_name']}',
                'api_key': '{vps_config['api_key']}'
            }},"""

        # Reemplazar configuración evolution
        import re
        pattern = r"'evolution': \{[^}]*\},"

        if re.search(pattern, content):
            content = re.sub(pattern, new_config, content, flags=re.DOTALL)
        else:
            # Si no existe, buscar donde insertar
            pattern = r"('api_config' = \{[^}]*)'pywhatkit':"
            if re.search(pattern, content):
                content = re.sub(pattern, f"\\1{new_config}\n            'pywhatkit':", content)

        # Cambiar orden de prioridad para Evolution
        content = content.replace(
            "('WhatsApp wa.me URL', self.send_via_wa_me_url),  # MÉTODO ORIGINAL QUE FUNCIONABA",
            "('Evolution API VPS', self.send_via_evolution),  # MÉTODO AUTOMÁTICO VPS"
        )

        # Guardar archivo actualizado
        with open('whatsapp_notifier.py', 'w') as f:
            f.write(content)

        print("✅ whatsapp_notifier.py actualizado para usar VPS")
        return True

    except Exception as e:
        print(f"❌ Error actualizando agente: {e}")
        return False

def main():
    """Configuración completa"""

    if configurar_con_vps():
        print("\n✅ Evolution API VPS configurado exitosamente")

        if actualizar_agente_seace():
            print("\n🎉 ¡AGENTE SEACE COMPLETAMENTE CONFIGURADO!")
            print("📱 Mensajes enviados automáticamente desde VPS")
            print("🚀 Sin navegadores, sin configuración local")
            print("⚡ Funcionamiento 24/7 desde la nube")

            print("\n🧪 PRUEBA FINAL DEL SISTEMA:")
            print("python3 -c \"from agente_whatsapp import AgenteWhatsAppSEACE; agente=AgenteWhatsAppSEACE(); agente.enviar_mensaje('¡Sistema VPS completamente automático!')\"")

        else:
            print("⚠️ Error actualizando agente, pero VPS funciona")

    else:
        print("❌ Error configurando VPS")

if __name__ == "__main__":
    main()