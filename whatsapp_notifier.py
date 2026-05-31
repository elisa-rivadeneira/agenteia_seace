#!/usr/bin/env python3
"""
Sistema de notificación WhatsApp para SEACE Buscador
Soporta múltiples APIs: Evolution API, WhatsApp Business API, Twilio
"""

import json
import requests
from datetime import datetime
import os
from typing import List, Dict, Optional
import webbrowser
import urllib.parse
import time

class WhatsAppNotifier:
    def __init__(self, config_file='config_empresa.json'):
        """Inicializa el notificador con la configuración"""
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.whatsapp_number = self.config['notificaciones'].get('whatsapp', '')
        self.empresa = self.config['empresa']['nombre']

        # Configuración de APIs (a completar por el usuario)
        self.api_config = {
                        'evolution': {
                'enabled': True,
                'base_url': 'https://automation-evolution-api.gnrjtm.easypanel.host',
                'instance': 'Elisa Rivadeneira',
                'api_key': '429683C4C977415CAAFCCE10F7D57E11'
            },
            'twilio': {
                'enabled': False,
                'account_sid': '',
                'auth_token': '',
                'from_number': ''  # Número de Twilio
            },
            'whatsapp_business': {
                'enabled': False,
                'phone_number_id': '',
                'access_token': ''
            },
            'baileys': {
                'enabled': False,
                'base_url': 'http://localhost:3000',  # URL de tu API Baileys
                'session': ''
            },
            'pywhatkit': {
                'enabled': True,  # REACTIVADO - YA FUNCIONÓ antes
                'tab_close_delay': 3,
                'send_delay': 15
            },
            'selenium': {
                'enabled': False,
                'headless': False
            },
            'simple_url': {
                'enabled': False  # Solo prepara, no envía
            },
            'auto_selenium': {
                'enabled': False,  # Deshabilitado por ser complejo
                'headless': False,
                'wait_for_qr': True
            },
            'whatsapp_auto_direct': {
                'enabled': True,  # REACTIVADO - método que YA FUNCIONÓ
                'auto_send': True
            },
            'whatsapp_api_simple': {
                'enabled': True,
                'use_existing_session': True
            }
        }

        # Cargar configuración adicional si existe
        if os.path.exists('whatsapp_config.json'):
            with open('whatsapp_config.json', 'r') as f:
                self.api_config.update(json.load(f))

    def send_via_evolution(self, message: str, number: str = None) -> bool:
        """Envía mensaje usando Evolution API"""
        if not self.api_config['evolution']['enabled']:
            return False

        config = self.api_config['evolution']
        url = f"{config['base_url']}/message/sendText/{config['instance']}"

        headers = {
            'Content-Type': 'application/json',
            'apikey': config['api_key']
        }

        # Formato correcto para VPS Evolution API
        clean_number = (number or self.whatsapp_number).replace('+', '').replace(' ', '')
        data = {
            'number': clean_number,
            'text': message
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            return response.status_code == 201
        except Exception as e:
            print(f"Error enviando por Evolution API: {e}")
            return False

    def send_via_twilio(self, message: str, number: str = None) -> bool:
        """Envía mensaje usando Twilio"""
        if not self.api_config['twilio']['enabled']:
            return False

        from twilio.rest import Client

        config = self.api_config['twilio']
        client = Client(config['account_sid'], config['auth_token'])

        try:
            message = client.messages.create(
                body=message,
                from_=f"whatsapp:{config['from_number']}",
                to=f"whatsapp:{number or self.whatsapp_number}"
            )
            return message.sid is not None
        except Exception as e:
            print(f"Error enviando por Twilio: {e}")
            return False

    def send_via_whatsapp_business(self, message: str, number: str = None) -> bool:
        """Envía mensaje usando WhatsApp Business API oficial"""
        if not self.api_config['whatsapp_business']['enabled']:
            return False

        config = self.api_config['whatsapp_business']
        url = f"https://graph.facebook.com/v17.0/{config['phone_number_id']}/messages"

        headers = {
            'Authorization': f"Bearer {config['access_token']}",
            'Content-Type': 'application/json'
        }

        data = {
            'messaging_product': 'whatsapp',
            'to': number or self.whatsapp_number,
            'type': 'text',
            'text': {'body': message}
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error enviando por WhatsApp Business API: {e}")
            return False

    def send_via_pywhatkit(self, message: str, number: str = None) -> bool:
        """Envía mensaje usando pywhatkit (WhatsApp Web automático)"""
        if not self.api_config['pywhatkit']['enabled']:
            return False

        try:
            target_number = number or self.whatsapp_number
            if not target_number.startswith('+'):
                target_number = '+' + target_number

            print(f"📱 Enviando mensaje WhatsApp a {target_number}")
            print("⚠️ Se abrirá WhatsApp Web en el navegador")

            # Usar hora actual + 1 minuto
            now = datetime.now()
            hour = now.hour
            minute = now.minute + 1
            if minute >= 60:
                hour += 1
                minute = 0

            # Importar pywhatkit
            import pywhatkit as kit

            config = self.api_config['pywhatkit']
            kit.sendwhatmsg(
                target_number,
                message,
                hour,
                minute,
                config.get('send_delay', 15),
                True,
                config.get('tab_close_delay', 3)
            )
            return True
        except Exception as e:
            print(f"Error enviando por pywhatkit: {e}")
            return False

    def send_via_whatsapp_api_simple(self, message: str, number: str = None) -> bool:
        """Envía usando API simple SIN abrir navegadores"""
        if not self.api_config['whatsapp_api_simple']['enabled']:
            return False

        try:
            target_number = number or self.whatsapp_number

            print(f"📱 Envío directo SIN navegador a {target_number}")

            # Opción 1: Usar Twilio si está configurado
            try:
                from twilio.rest import Client

                # Buscar credenciales de Twilio en variables de entorno o config
                import os
                account_sid = os.getenv('TWILIO_ACCOUNT_SID')
                auth_token = os.getenv('TWILIO_AUTH_TOKEN')
                from_number = os.getenv('TWILIO_FROM_NUMBER', 'whatsapp:+14155238886')

                if account_sid and auth_token:
                    client = Client(account_sid, auth_token)

                    message_obj = client.messages.create(
                        body=message,
                        from_=from_number,
                        to=f"whatsapp:{target_number}"
                    )

                    print("✅ Mensaje enviado por Twilio")
                    return True
            except Exception as e:
                print(f"Twilio no disponible: {e}")

            # Opción 2: Usar CallMeBot si hay API key
            try:
                import os
                callmebot_key = os.getenv('CALLMEBOT_API_KEY')

                if callmebot_key:
                    clean_number = target_number.replace('+', '').replace(' ', '')

                    url = "https://api.callmebot.com/whatsapp.php"
                    params = {
                        'phone': clean_number,
                        'text': message,
                        'apikey': callmebot_key
                    }

                    response = requests.get(url, params=params, timeout=10)

                    if response.status_code == 200:
                        print("✅ Mensaje enviado por CallMeBot")
                        return True
            except Exception as e:
                print(f"CallMeBot no disponible: {e}")

            # Opción 3: Fallback a método URL (sin automatización)
            print("📝 Usando método URL simple como fallback...")
            clean_phone = target_number.replace('+', '').replace(' ', '').replace('-', '')
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"

            print(f"🌐 URL generada: {whatsapp_url[:50]}...")
            print("💡 INSTRUCCIÓN: Ve a WhatsApp Web y el mensaje estará preparado")

            # NO abrir navegador automáticamente
            print("✅ URL preparada - mensaje listo para envío manual")
            return True

        except Exception as e:
            print(f"Error en envío API simple: {e}")
            return False

    def send_via_wa_me_url(self, message: str, number: str = None) -> bool:
        """Envía usando Selenium para automático REAL - sin intervención manual"""
        try:
            target_number = number or self.whatsapp_number
            clean_number = target_number.replace('+', '').replace(' ', '')

            print(f"📱 Enviando automáticamente a {target_number}")
            print("🤖 Usando Selenium para envío automático REAL")

            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.options import Options
            import time

            # Configurar Chrome para usar sesión existente
            chrome_options = Options()
            chrome_options.add_argument("--user-data-dir=/tmp/whatsapp_session")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")

            # Crear driver
            driver = webdriver.Chrome(options=chrome_options)

            # Ir directo a WhatsApp Web con el número
            driver.get("https://web.whatsapp.com/")

            # Esperar a que WhatsApp Web cargue
            print("⏳ Esperando WhatsApp Web...")
            time.sleep(5)

            # Buscar el contacto
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
            )

            search_box.click()
            search_box.send_keys(target_number)
            time.sleep(2)

            # Hacer clic en el contacto
            contact = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[@title='{target_number}']"))
            )
            contact.click()
            time.sleep(2)

            # Escribir mensaje
            message_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )

            message_box.click()
            message_box.send_keys(message)
            time.sleep(1)

            # Enviar mensaje
            send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']")
            send_button.click()

            print("✅ Mensaje enviado automáticamente!")
            time.sleep(2)

            driver.quit()
            return True

        except Exception as e:
            print(f"❌ Error envío automático: {e}")
            print("💡 Intentando método de respaldo...")

            # Método de respaldo - solo preparar URL
            import urllib.parse
            mensaje_url = urllib.parse.quote(message)
            wa_me_url = f"https://api.whatsapp.com/send?phone={clean_number}&text={mensaje_url}"

            with open('whatsapp_url_actual.txt', 'w') as f:
                f.write(wa_me_url)

            print(f"📱 URL preparada: {wa_me_url[:60]}...")
            print("💡 Ve a WhatsApp Web y el mensaje estará listo")

            return False

    def send_via_whatsapp_auto_direct(self, message: str, number: str = None) -> bool:
        """Envía mensaje usando el método que YA FUNCIONÓ automáticamente"""
        if not self.api_config['whatsapp_auto_direct']['enabled']:
            return False

        try:
            from whatsapp_auto import WhatsAppAuto
            import threading
            import time

            target_number = number or self.whatsapp_number
            print(f"📤 Enviando automáticamente a {target_number}")

            # Crear instancia
            whatsapp = WhatsAppAuto()

            def enviar_en_background():
                try:
                    whatsapp.setup_driver(headless=False)

                    # Reducir tiempo de espera
                    success = whatsapp.send_message_direct(
                        target_number,
                        message,
                        wait_for_qr=False  # No esperar QR si ya está conectado
                    )

                    time.sleep(2)  # Breve pausa
                    whatsapp.close()

                    return success
                except Exception as e:
                    print(f"Error en background: {e}")
                    return False

            # Ejecutar en background para no bloquear
            thread = threading.Thread(target=enviar_en_background)
            thread.start()
            thread.join(timeout=45)  # Máximo 45 segundos

            print("✅ Proceso de envío completado")
            return True

        except Exception as e:
            print(f"Error en envío directo: {e}")
            return False

    def send_via_auto_selenium(self, message: str, number: str = None) -> bool:
        """Envía mensaje automáticamente con Selenium (REALMENTE envía)"""
        if not self.api_config['auto_selenium']['enabled']:
            return False

        try:
            from whatsapp_auto import WhatsAppAuto

            target_number = number or self.whatsapp_number
            print(f"📤 Enviando mensaje automático a {target_number}")

            whatsapp = WhatsAppAuto()
            whatsapp.setup_driver(headless=self.api_config['auto_selenium'].get('headless', False))

            success = whatsapp.send_message_direct(
                target_number,
                message,
                wait_for_qr=self.api_config['auto_selenium'].get('wait_for_qr', True)
            )

            whatsapp.close()
            return success

        except Exception as e:
            print(f"Error enviando por Auto Selenium: {e}")
            return False

    def send_via_simple_url(self, message: str, number: str = None) -> bool:
        """Envía mensaje usando URL directa de WhatsApp Web (método más confiable)"""
        if not self.api_config['simple_url']['enabled']:
            return False

        try:
            target_number = number or self.whatsapp_number
            clean_phone = target_number.replace('+', '').replace(' ', '').replace('-', '')
            encoded_message = urllib.parse.quote(message)

            whatsapp_url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"

            print(f"🌐 Abriendo WhatsApp Web con mensaje preparado...")
            print(f"📱 Para: {target_number}")
            print("💡 El mensaje ya estará escrito, solo haz clic en ENVIAR")

            webbrowser.open(whatsapp_url)
            return True

        except Exception as e:
            print(f"Error enviando por URL simple: {e}")
            return False

    def send_via_selenium(self, message: str, number: str = None) -> bool:
        """Envía mensaje usando Selenium WebDriver"""
        if not self.api_config['selenium']['enabled']:
            return False

        try:
            from whatsapp_selenium import WhatsAppSelenium

            print("🌐 Iniciando WhatsApp con Selenium...")
            whatsapp = WhatsAppSelenium()
            whatsapp.setup_driver()
            whatsapp.open_whatsapp()

            target_number = number or self.whatsapp_number
            success = whatsapp.send_message(target_number, message)

            whatsapp.close()
            return success

        except Exception as e:
            print(f"Error enviando por Selenium: {e}")
            return False

    def send_via_baileys(self, message: str, number: str = None) -> bool:
        """Envía mensaje usando Baileys (WhatsApp Web)"""
        if not self.api_config['baileys']['enabled']:
            return False

        config = self.api_config['baileys']
        url = f"{config['base_url']}/send-message"

        data = {
            'session': config['session'],
            'to': f"{number or self.whatsapp_number}@s.whatsapp.net",
            'text': message
        }

        try:
            response = requests.post(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error enviando por Baileys: {e}")
            return False

    def send_message(self, message: str, number: str = None, priority: str = 'normal') -> bool:
        """
        Envía mensaje por WhatsApp usando la primera API disponible

        Args:
            message: Mensaje a enviar
            number: Número de WhatsApp (opcional, usa el configurado por defecto)
            priority: 'urgent', 'high', 'normal', 'low'
        """

        # Agregar prefijo según prioridad
        if priority == 'urgent':
            message = f"🚨 URGENTE\n\n{message}"
        elif priority == 'high':
            message = f"⚠️ IMPORTANTE\n\n{message}"

        # EVOLUTION VPS PRIMERO - Envío automático real
        apis = [
            ('Evolution VPS', self.send_via_evolution),  # VPS AUTOMÁTICO REAL - PRIORIDAD 1
            ('WhatsApp Auto Direct', self.send_via_whatsapp_auto_direct),
            ('WhatsApp Auto Selenium', self.send_via_auto_selenium),
            ('WhatsApp API Simple', self.send_via_whatsapp_api_simple),
            ('WhatsApp URL Simple', self.send_via_simple_url),
            ('Selenium WebDriver', self.send_via_selenium),
            ('PyWhatKit', self.send_via_pywhatkit),
            ('Twilio', self.send_via_twilio),
            ('WhatsApp Business', self.send_via_whatsapp_business),
            ('Baileys', self.send_via_baileys)
        ]

        for api_name, send_func in apis:
            if send_func(message, number):
                print(f"✅ Mensaje enviado exitosamente por {api_name}")
                return True

        print("❌ No se pudo enviar el mensaje por ninguna API")
        return False

    def format_oportunidad(self, oportunidad: Dict) -> str:
        """Formatea una oportunidad para WhatsApp"""
        fecha_limite = oportunidad.get('fecha_fin', 'No especificada')
        valor = oportunidad.get('valor', '---')

        mensaje = f"""
🔔 *NUEVA OPORTUNIDAD SEACE*

*Entidad:* {oportunidad.get('entidad', 'N/A')}
*Nomenclatura:* {oportunidad.get('nomenclatura', 'N/A')}
*Descripción:* {oportunidad.get('descripcion_procedimiento', 'N/A')[:100]}...
*Fecha límite:* {fecha_limite}
*Valor:* {valor}
*Compatibilidad:* {oportunidad.get('score_compatibilidad', 0)}%

Ver más en SEACE: https://prod4.seace.gob.pe/
        """
        return mensaje.strip()

    def send_oportunidades_report(self, oportunidades: List[Dict]) -> bool:
        """Envía reporte de oportunidades encontradas"""
        if not oportunidades:
            return False

        # Filtrar oportunidades más relevantes
        relevantes = [op for op in oportunidades if op.get('score_compatibilidad', 0) >= 30]
        urgentes = [op for op in relevantes if self._es_urgente(op)]

        # Crear mensaje resumen
        mensaje = f"""
📊 *REPORTE SEACE - {self.empresa}*
{datetime.now().strftime('%d/%m/%Y %H:%M')}

Total encontradas: {len(oportunidades)}
Relevantes (≥30%): {len(relevantes)}
Urgentes (≤3 días): {len(urgentes)}
"""

        if urgentes:
            mensaje += "\n🚨 *URGENTES:*\n"
            for op in urgentes[:3]:  # Máximo 3 urgentes
                mensaje += f"• {op['entidad'][:30]}... - {op['fecha_fin']}\n"

        if relevantes:
            mensaje += "\n⭐ *MÁS RELEVANTES:*\n"
            for op in relevantes[:5]:  # Top 5
                if op not in urgentes:
                    mensaje += f"• {op['entidad'][:30]}... ({op['score_compatibilidad']}%)\n"

        mensaje += "\n_Revisa el sistema para más detalles_"

        # Enviar resumen
        self.send_message(mensaje, priority='normal')

        # Enviar detalles de las más urgentes/relevantes
        for op in urgentes[:2]:  # Solo las 2 más urgentes
            self.send_message(self.format_oportunidad(op), priority='urgent')

        return True

    def _es_urgente(self, oportunidad: Dict) -> bool:
        """Determina si una oportunidad es urgente (≤3 días)"""
        try:
            fecha_str = oportunidad.get('fecha_fin', '')
            if not fecha_str:
                return False

            # Parsear fecha (formato: DD/MM/YYYY HH:MM:SS)
            fecha = datetime.strptime(fecha_str.split()[0], '%d/%m/%Y')
            dias_restantes = (fecha - datetime.now()).days

            return dias_restantes <= 3
        except:
            return False

    def test_connection(self) -> Dict[str, bool]:
        """Prueba la conexión con cada API configurada"""
        results = {}

        test_message = f"🔧 Test de conexión SEACE Monitor - {datetime.now().strftime('%H:%M:%S')}"

        for api_name in self.api_config:
            if self.api_config[api_name].get('enabled'):
                print(f"Probando {api_name}...")
                if api_name == 'evolution':
                    results[api_name] = self.send_via_evolution(test_message)
                elif api_name == 'twilio':
                    results[api_name] = self.send_via_twilio(test_message)
                elif api_name == 'whatsapp_business':
                    results[api_name] = self.send_via_whatsapp_business(test_message)
                elif api_name == 'baileys':
                    results[api_name] = self.send_via_baileys(test_message)

        return results


def main():
    """Función principal para pruebas"""
    print("="*60)
    print(" CONFIGURADOR DE NOTIFICACIONES WHATSAPP")
    print("="*60)

    notifier = WhatsAppNotifier()

    print(f"\n📱 Número configurado: {notifier.whatsapp_number}")
    print(f"🏢 Empresa: {notifier.empresa}")

    print("\n¿Qué deseas hacer?")
    print("1. Probar conexión")
    print("2. Enviar mensaje de prueba")
    print("3. Enviar reporte de oportunidades")
    print("4. Configurar API")

    opcion = input("\nOpción: ")

    if opcion == "1":
        print("\nProbando conexiones...")
        results = notifier.test_connection()
        for api, status in results.items():
            print(f"  {api}: {'✅ OK' if status else '❌ Error'}")

    elif opcion == "2":
        mensaje = input("Mensaje a enviar: ")
        if notifier.send_message(mensaje):
            print("✅ Mensaje enviado")
        else:
            print("❌ Error al enviar")

    elif opcion == "3":
        # Cargar últimas oportunidades
        import glob
        files = sorted(glob.glob("seace_todas_oportunidades_*.json"))
        if files:
            with open(files[-1], 'r', encoding='utf-8') as f:
                data = json.load(f)
                notifier.send_oportunidades_report(data['oportunidades'])
                print("✅ Reporte enviado")

    elif opcion == "4":
        print("\n⚠️ Para configurar las APIs, crea un archivo 'whatsapp_config.json' con:")
        config_example = {
            "evolution": {
                "enabled": True,
                "base_url": "http://localhost:8080",
                "instance": "tu_instancia",
                "api_key": "tu_api_key"
            }
        }
        print(json.dumps(config_example, indent=2))

if __name__ == "__main__":
    main()