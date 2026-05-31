#!/usr/bin/env python3
"""
Verificar instancias disponibles en VPS Evolution API
"""

import requests
import json

def check_instances():
    """Verificar qué instancias están disponibles"""

    vps_url = "https://automation-evolution-api.gnrjtm.easypanel.host"
    api_key = "429683C4C977415CAAFCCE10F7D57E11"

    print("🔍 VERIFICANDO INSTANCIAS EN VPS")
    print("=" * 50)

    try:
        response = requests.get(f"{vps_url}/instance/fetchInstances",
                              headers={'apikey': api_key}, timeout=10)

        if response.status_code == 200:
            instances = response.json()
            print(f"📱 Total de instancias: {len(instances)}")

            for i, instance in enumerate(instances, 1):
                print(f"\n📋 INSTANCIA {i}:")
                print(f"   Nombre: {instance.get('instanceName', 'Sin nombre')}")
                print(f"   ID: {instance.get('instanceId', 'Sin ID')}")
                print(f"   Estado: {instance.get('connectionStatus', {}).get('state', 'Desconocido')}")
                print(f"   WhatsApp: {instance.get('connectionStatus', {}).get('isConnected', False)}")

                # Usar la primera instancia conectada
                if instance.get('connectionStatus', {}).get('state') == 'open':
                    instance_name = instance.get('instanceName') or instance.get('instanceId', f'instance_{i}')
                    print(f"\n✅ Encontrada instancia conectada: {instance_name}")

                    # Probar envío con esta instancia
                    return test_send_with_instance(vps_url, api_key, instance_name)

            # Si no hay instancias conectadas, usar la primera disponible
            if instances:
                first_instance = instances[0]
                instance_name = first_instance.get('instanceName') or first_instance.get('instanceId', 'default')
                print(f"\n⚠️ No hay instancias conectadas, probando con: {instance_name}")
                return test_send_with_instance(vps_url, api_key, instance_name)

        else:
            print(f"❌ Error obteniendo instancias: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_send_with_instance(vps_url: str, api_key: str, instance_name: str):
    """Probar envío con una instancia específica"""

    print(f"\n🧪 PROBANDO ENVÍO CON INSTANCIA: {instance_name}")

    try:
        url = f"{vps_url}/message/sendText/{instance_name}"

        headers = {
            'Content-Type': 'application/json',
            'apikey': api_key
        }

        mensaje = f"""🎉 VPS EVOLUTION API - PRUEBA EXITOSA!
📱 Instancia: {instance_name}
🤖 Envío automático desde VPS
📊 Sistema SEACE configurado

¡Funcionando perfectamente!"""

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
            print("✅ ¡MENSAJE ENVIADO AUTOMÁTICAMENTE!")
            print(f"📱 Message ID: {result.get('key', {}).get('id', 'N/A')}")

            # Guardar configuración exitosa
            config = {
                'evolution_vps': {
                    'enabled': True,
                    'base_url': vps_url,
                    'api_key': api_key,
                    'instance_name': instance_name,
                    'status': 'working'
                }
            }

            with open('evolution_vps_working.json', 'w') as f:
                json.dump(config, f, indent=2)

            print(f"💾 Configuración exitosa guardada para instancia: {instance_name}")
            return True

        else:
            print(f"❌ Error enviando: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if check_instances():
        print("\n🎉 ¡VPS EVOLUTION API FUNCIONANDO!")
        print("📱 El agente puede usar esta configuración")
    else:
        print("\n❌ Problemas con VPS Evolution API")
        print("💡 Verifica que las instancias estén conectadas")