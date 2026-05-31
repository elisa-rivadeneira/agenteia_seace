#!/usr/bin/env python3
"""
Integración con Evolution API en VPS - Envío automático real
"""

import requests
import json
from datetime import datetime

class EvolutionVPS:
    def __init__(self, base_url, api_key, instance_name="seace_agent"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name

        print(f"🔗 Conectando a Evolution API: {self.base_url}")

    def test_connection(self):
        """Prueba la conexión con el VPS"""
        try:
            url = f"{self.base_url}/instance/fetchInstances"
            headers = {'apikey': self.api_key}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                print("✅ Conexión con VPS exitosa")
                instances = response.json()
                print(f"📱 Instancias disponibles: {len(instances)}")
                return True
            else:
                print(f"❌ Error conexión: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error conectando VPS: {e}")
            return False

    def get_instance_state(self):
        """Obtiene estado de la instancia"""
        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
            headers = {'apikey': self.api_key}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                state = response.json()
                status = state.get('instance', {}).get('state', 'unknown')
                print(f"📱 Estado instancia '{self.instance_name}': {status}")
                return status == 'open'
            else:
                print(f"❌ Error obteniendo estado: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def send_message_vps(self, message: str, phone: str = "+51967717179"):
        """Envía mensaje usando Evolution API en VPS"""
        try:
            url = f"{self.base_url}/message/sendText/{self.instance_name}"

            headers = {
                'Content-Type': 'application/json',
                'apikey': self.api_key
            }

            # Limpiar número
            clean_phone = phone.replace('+', '').replace(' ', '')

            data = {
                "number": clean_phone,
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                },
                "textMessage": {
                    "text": message
                }
            }

            print(f"📤 Enviando mensaje automático via VPS a {phone}...")

            response = requests.post(url, json=data, headers=headers, timeout=30)

            if response.status_code == 201:
                result = response.json()
                print("✅ ¡MENSAJE ENVIADO AUTOMÁTICAMENTE VIA VPS!")
                print(f"📱 Message ID: {result.get('key', {}).get('id', 'N/A')}")
                return True
            else:
                print(f"❌ Error enviando: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error enviando via VPS: {e}")
            return False

    def configure_for_seace(self, vps_url: str, api_key: str, instance_name: str = None):
        """Configuración rápida para SEACE con datos del VPS"""

        if instance_name:
            self.instance_name = instance_name

        self.base_url = vps_url.rstrip('/')
        self.api_key = api_key

        print("🚀 CONFIGURANDO EVOLUTION VPS PARA SEACE")
        print("=" * 50)
        print(f"🔗 VPS URL: {self.base_url}")
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"📱 Instance: {self.instance_name}")

        # Test conexión
        if not self.test_connection():
            print("❌ No se puede conectar al VPS")
            return False

        # Verificar instancia
        if not self.get_instance_state():
            print("❌ Instancia no conectada o no existe")
            print("💡 Activa la instancia en tu VPS primero")
            return False

        # Test de envío
        test_message = f"""🎉 VPS EVOLUTION API FUNCIONANDO!
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Conexión VPS exitosa
🤖 Envío automático operativo
📊 Agente SEACE configurado

¡Sistema completamente automático!"""

        if self.send_message_vps(test_message):
            # Guardar configuración
            config = {
                'evolution_vps': {
                    'enabled': True,
                    'base_url': self.base_url,
                    'api_key': self.api_key,
                    'instance_name': self.instance_name,
                    'configured_at': datetime.now().isoformat()
                }
            }

            with open('evolution_vps_config.json', 'w') as f:
                json.dump(config, f, indent=2)

            print("✅ Configuración guardada en evolution_vps_config.json")
            print("🎉 ¡SISTEMA LISTO PARA ENVÍO AUTOMÁTICO!")
            return True
        else:
            print("❌ Error en test de envío")
            return False

def setup_rapido():
    """Setup rápido con datos del usuario"""
    print("🚀 SETUP EVOLUTION API VPS")
    print("=" * 40)

    print("📋 Proporciona los datos de tu VPS:")
    vps_url = input("URL VPS (ej: https://tu-vps.com:8080): ").strip()
    api_key = input("API Key: ").strip()
    instance_name = input("Nombre instancia (Enter=seace_agent): ").strip() or "seace_agent"

    if vps_url and api_key:
        evolution = EvolutionVPS(vps_url, api_key, instance_name)
        return evolution.configure_for_seace(vps_url, api_key, instance_name)
    else:
        print("❌ Datos incompletos")
        return False

if __name__ == "__main__":
    setup_rapido()