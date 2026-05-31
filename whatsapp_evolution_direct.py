#!/usr/bin/env python3
"""
Evolution API - Envío directo automático SIN configuración compleja
Usa Evolution API local para envío automático real
"""

import requests
import json
import time
from datetime import datetime

class EvolutionAPIDirect:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.api_key = "429683C4C977415CAAFCCE10F7D57E11"  # Del .env
        self.instance_name = "seace_whatsapp"

    def verificar_servidor(self):
        """Verifica si Evolution API está corriendo"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Evolution API está corriendo")
                return True
        except Exception as e:
            print(f"❌ Evolution API no disponible: {e}")
            return False

    def crear_instancia_simple(self):
        """Crea una instancia simple para WhatsApp"""
        try:
            url = f"{self.base_url}/instance/create"

            headers = {
                'Content-Type': 'application/json',
                'apikey': self.api_key
            }

            data = {
                "instanceName": self.instance_name,
                "integration": "WHATSAPP-BAILEYS",
                "token": self.api_key,
                "qrcode": True
            }

            response = requests.post(url, json=data, headers=headers, timeout=30)

            if response.status_code == 201:
                result = response.json()
                print("✅ Instancia creada exitosamente")
                print(f"📱 QR Code: {result.get('qrcode', {}).get('code', 'No disponible')}")
                return True
            else:
                print(f"⚠️ Instancia ya existe o error: {response.status_code}")
                print(response.text)
                return True  # Continuar aunque ya exista

        except Exception as e:
            print(f"❌ Error creando instancia: {e}")
            return False

    def obtener_estado_instancia(self):
        """Obtiene el estado de conexión de la instancia"""
        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance_name}"

            headers = {'apikey': self.api_key}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                state = response.json()
                print(f"📱 Estado conexión: {state.get('instance', {}).get('state', 'unknown')}")
                return state.get('instance', {}).get('state') == 'open'
            else:
                print(f"⚠️ No se pudo obtener estado: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
            return False

    def enviar_mensaje_directo(self, mensaje: str, numero: str = "+51967717179"):
        """Envía mensaje directo usando Evolution API"""
        try:
            url = f"{self.base_url}/message/sendText/{self.instance_name}"

            headers = {
                'Content-Type': 'application/json',
                'apikey': self.api_key
            }

            # Limpiar número
            clean_number = numero.replace('+', '').replace(' ', '')

            data = {
                "number": clean_number,
                "options": {
                    "delay": 1200,
                    "presence": "composing",
                    "linkPreview": False
                },
                "textMessage": {
                    "text": mensaje
                }
            }

            print(f"📤 Enviando mensaje a {numero}...")
            response = requests.post(url, json=data, headers=headers, timeout=30)

            if response.status_code == 201:
                result = response.json()
                print("✅ ¡MENSAJE ENVIADO AUTOMÁTICAMENTE!")
                print(f"📱 Message ID: {result.get('key', {}).get('id', 'N/A')}")
                return True
            else:
                print(f"❌ Error enviando mensaje: {response.status_code}")
                print(response.text)
                return False

        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return False

    def configuracion_completa(self):
        """Configuración completa paso a paso"""
        print("🚀 CONFIGURACIÓN EVOLUTION API PARA ENVÍO AUTOMÁTICO")
        print("=" * 60)

        # Paso 1: Verificar servidor
        print("\n1️⃣ Verificando servidor Evolution API...")
        if not self.verificar_servidor():
            print("❌ Inicia Evolution API primero:")
            print("   cd evolution-api && npm start")
            return False

        # Paso 2: Crear instancia
        print("\n2️⃣ Creando instancia WhatsApp...")
        if not self.crear_instancia_simple():
            return False

        # Paso 3: Esperar conexión (QR Code)
        print("\n3️⃣ Conectando a WhatsApp...")
        print("📱 Escanea el QR code en Evolution API dashboard:")
        print(f"   {self.base_url}")

        # Esperar conexión
        max_intentos = 30
        for i in range(max_intentos):
            if self.obtener_estado_instancia():
                print("✅ ¡WhatsApp conectado!")
                break
            print(f"⏳ Esperando conexión... {i+1}/{max_intentos}")
            time.sleep(5)
        else:
            print("❌ Timeout esperando conexión")
            return False

        return True

    def test_envio_automatico(self):
        """Test completo de envío automático"""
        print("🧪 TEST ENVÍO AUTOMÁTICO EVOLUTION API")
        print("=" * 50)

        mensaje_test = f"""🤖 EVOLUTION API - ENVÍO AUTOMÁTICO
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Mensaje enviado automáticamente
🚀 Sin intervención manual
📊 Sistema SEACE operativo

¡Evolution API funcionando!"""

        # Verificar conexión
        if not self.obtener_estado_instancia():
            print("❌ WhatsApp no conectado")
            print("💡 Ejecuta: python3 whatsapp_evolution_direct.py para configurar")
            return False

        # Enviar mensaje
        success = self.enviar_mensaje_directo(mensaje_test)

        if success:
            print("\n🎉 ¡EVOLUTION API FUNCIONANDO PERFECTAMENTE!")
            print("📱 Revisa tu WhatsApp - el mensaje debe haber llegado")
            print("✅ Sistema listo para envío automático sin intervención")
        else:
            print("\n⚠️ Error en el envío, verifica la configuración")

        return success

def main():
    """Función principal"""
    evolution = EvolutionAPIDirect()

    # Verificar si ya está configurado
    if evolution.obtener_estado_instancia():
        print("✅ Evolution API ya configurado")
        evolution.test_envio_automatico()
    else:
        print("🔧 Configurando Evolution API...")
        if evolution.configuracion_completa():
            print("\n🎉 Configuración completada!")
            evolution.test_envio_automatico()

if __name__ == "__main__":
    main()