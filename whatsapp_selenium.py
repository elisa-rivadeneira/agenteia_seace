#!/usr/bin/env python3
"""
WhatsApp Sender usando Selenium - Más confiable que PyWhatKit
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import json

class WhatsAppSelenium:
    def __init__(self):
        """Inicializa el driver de Selenium"""
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Configura el driver de Chrome para WhatsApp Web"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # No usar headless para WhatsApp Web
        # options.add_argument('--headless=new')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 30)

    def open_whatsapp(self):
        """Abre WhatsApp Web"""
        print("🌐 Abriendo WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")

        print("📱 Esperando que escanees el código QR o que la sesión esté activa...")
        print("⚠️ Una vez que veas la interfaz principal de WhatsApp, presiona ENTER aquí")
        input("   Presiona ENTER cuando WhatsApp Web esté listo...")

    def send_message(self, phone_number: str, message: str) -> bool:
        """
        Envía un mensaje a un número específico

        Args:
            phone_number: Número de teléfono (ej: +51967717179)
            message: Mensaje a enviar

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Buscar el contacto/número
            print(f"🔍 Buscando contacto: {phone_number}")

            # Hacer clic en el botón de nueva conversación
            try:
                new_chat_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@title='Nueva conversación']"))
                )
                new_chat_btn.click()
                time.sleep(2)
            except:
                # Intentar con el método alternativo
                try:
                    search_box = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
                    )
                except:
                    # Usar URL directa
                    clean_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')
                    self.driver.get(f"https://web.whatsapp.com/send?phone={clean_number}")
                    time.sleep(5)

            # Buscar la caja de texto para escribir
            print("✍️ Escribiendo mensaje...")
            try:
                # Esperar a que aparezca la caja de texto
                text_box = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
                )

                # Escribir el mensaje
                text_box.click()
                time.sleep(1)
                text_box.send_keys(message)
                time.sleep(2)

                # Enviar el mensaje
                send_button = self.driver.find_element(By.XPATH, "//span[@data-icon='send']")
                send_button.click()

                print("✅ Mensaje enviado exitosamente!")
                time.sleep(3)
                return True

            except Exception as e:
                print(f"❌ Error enviando mensaje: {e}")
                return False

        except Exception as e:
            print(f"❌ Error general: {e}")
            return False

    def close(self):
        """Cierra el navegador"""
        if self.driver:
            print("🔚 Cerrando navegador...")
            self.driver.quit()

def test_whatsapp_selenium():
    """Función de prueba"""
    print("🧪 PRUEBA WHATSAPP CON SELENIUM")
    print("=" * 50)

    # Cargar configuración
    try:
        with open('config_empresa.json', 'r') as f:
            config = json.load(f)
        phone = config['notificaciones']['whatsapp']
        empresa = config['empresa']['nombre']
    except:
        phone = "+51967717179"  # Número por defecto
        empresa = "SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C"

    # Mensaje de prueba
    mensaje = f"""📊 PRUEBA SEACE MONITOR (Selenium)

🏢 {empresa}
📅 {time.strftime('%d/%m/%Y %H:%M')}

✅ Sistema WhatsApp con Selenium funcionando!

🔍 Monitor SEACE activo
🎯 Segmento 43: 30 oportunidades detectadas

_Enviado con Selenium WebDriver_"""

    whatsapp = WhatsAppSelenium()

    try:
        whatsapp.setup_driver()
        whatsapp.open_whatsapp()

        success = whatsapp.send_message(phone, mensaje)

        if success:
            print("\n🎉 ¡MENSAJE ENVIADO EXITOSAMENTE!")
        else:
            print("\n❌ Error enviando mensaje")

    except KeyboardInterrupt:
        print("\n⚠️ Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        whatsapp.close()

if __name__ == "__main__":
    test_whatsapp_selenium()