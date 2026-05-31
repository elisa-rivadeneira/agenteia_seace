#!/usr/bin/env python3
"""
WhatsApp Automático - Envío real con Selenium
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
import urllib.parse

class WhatsAppAuto:
    def __init__(self):
        self.driver = None
        self.wait = None

    def setup_driver(self, headless=False):
        """Configura Chrome para WhatsApp"""
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 60)

    def send_message_direct(self, phone_number: str, message: str, wait_for_qr=True) -> bool:
        """
        Envía mensaje directamente usando URL de WhatsApp
        """
        try:
            # Limpiar número
            clean_phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
            encoded_message = urllib.parse.quote(message)

            # URL directa de WhatsApp
            url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"

            print(f"🌐 Abriendo WhatsApp Web: {clean_phone}")
            self.driver.get(url)

            # Esperar a que cargue
            time.sleep(10)

            if wait_for_qr:
                print("📱 Escanea el QR Code si aparece...")
                print("⏳ Esperando 15 segundos para cargar WhatsApp...")
                time.sleep(15)
            else:
                print("⚡ Carga rápida - 5 segundos...")
                time.sleep(5)

            # Buscar y hacer clic en el botón de enviar
            print("🔍 Buscando botón de enviar...")

            # Múltiples selectores para el botón enviar
            send_selectors = [
                "//span[@data-icon='send']",
                "//button[@aria-label='Enviar']",
                "//button[contains(@class, 'send')]",
                "//*[@data-testid='send']",
                "//div[@role='button']//span[@data-icon='send']"
            ]

            for selector in send_selectors:
                try:
                    send_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"✅ Botón encontrado: {selector}")
                    self.driver.execute_script("arguments[0].click();", send_button)
                    print("📤 ¡Mensaje enviado!")
                    time.sleep(5)
                    return True
                except:
                    continue

            # Si no encuentra el botón, intentar con Enter
            print("🔄 Intentando enviar con Enter...")
            try:
                # Buscar área de texto y enviar con Enter
                text_area = self.driver.find_element(By.XPATH, "//div[@contenteditable='true']")
                text_area.click()
                text_area.send_keys(Keys.ENTER)
                print("📤 ¡Mensaje enviado con Enter!")
                return True
            except:
                print("❌ No se pudo enviar automáticamente")
                print("💡 Ve al navegador y haz clic en ENVIAR manualmente")
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def close(self):
        """Cierra el navegador"""
        if self.driver:
            time.sleep(3)
            self.driver.quit()

def test_auto_send():
    """Prueba de envío automático"""
    print("🚀 WHATSAPP AUTOMÁTICO - ENVÍO REAL")
    print("=" * 50)

    # Cargar configuración
    try:
        import json
        with open('config_empresa.json', 'r') as f:
            config = json.load(f)
        phone = config['notificaciones']['whatsapp']
        empresa = config['empresa']['nombre']
    except:
        phone = "+51967717179"
        empresa = "SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C"

    mensaje = f"""🧪 PRUEBA AUTOMÁTICA SEACE

🏢 {empresa}
📅 {time.strftime('%d/%m/%Y %H:%M')}

✅ Envío automático funcionando!

🔍 Monitor SEACE operativo
📊 30 oportunidades detectadas
🎯 Sistema WhatsApp configurado

_Mensaje enviado automáticamente_"""

    print(f"📱 Enviando a: {phone}")
    print("📝 Mensaje:")
    print("-" * 30)
    print(mensaje)
    print("-" * 30)

    whatsapp = WhatsAppAuto()

    try:
        print("\n🔧 Configurando navegador...")
        whatsapp.setup_driver(headless=False)  # Con interfaz para debugging

        print("📤 Enviando mensaje...")
        success = whatsapp.send_message_direct(phone, mensaje, wait_for_qr=True)

        if success:
            print("\n🎉 ¡MENSAJE ENVIADO EXITOSAMENTE!")
            print("📲 Revisa tu celular para confirmar")
        else:
            print("\n⚠️ Proceso completado - verifica manualmente")

        # Mantener abierto para verificar
        input("\nPresiona ENTER para cerrar el navegador...")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        whatsapp.close()

if __name__ == "__main__":
    test_auto_send()