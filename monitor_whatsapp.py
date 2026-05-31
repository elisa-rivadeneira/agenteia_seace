#!/usr/bin/env python3
"""
MONITOR WHATSAPP - Escucha y responde automáticamente
Sistema que detecta mensajes entrantes y responde usando el agente
"""

import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from agente_whatsapp import AgenteWhatsAppSEACE
import threading

class MonitorWhatsApp:
    def __init__(self):
        """Inicializa el monitor de WhatsApp"""
        self.driver = None
        self.wait = None
        self.agente = AgenteWhatsAppSEACE()
        self.ultimo_mensaje = None
        self.activo = True

        # Configuración de número autorizado
        with open('config_empresa.json', 'r') as f:
            config = json.load(f)
        self.numero_autorizado = config['notificaciones']['whatsapp']

        print(f"🤖 Monitor WhatsApp inicializado")
        print(f"📱 Número autorizado: {self.numero_autorizado}")

    def setup_driver(self):
        """Configura Chrome para WhatsApp Web"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1400,900')
        options.add_argument('--disable-web-security')

        # Configurar perfil para mantener sesión
        options.add_argument('--user-data-dir=/tmp/whatsapp_session')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)

    def iniciar_whatsapp_web(self):
        """Abre WhatsApp Web y espera conexión"""
        print("🌐 Abriendo WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")

        print("📱 Escanea el QR Code si aparece...")
        print("⏳ Esperando a que WhatsApp Web esté listo...")

        # Esperar hasta que aparezca la interfaz principal
        try:
            # Esperar que cargue la lista de chats
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chat-list']"))
            )
            print("✅ WhatsApp Web conectado correctamente")
            return True
        except:
            print("❌ Error conectando WhatsApp Web")
            return False

    def buscar_chat_autorizado(self):
        """Busca y abre el chat del número autorizado"""
        try:
            # Hacer clic en la caja de búsqueda
            search_box = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='chat-list-search']"))
            )
            search_box.click()

            # Limpiar y buscar el número
            search_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='search-input']")
            search_input.clear()
            search_input.send_keys(self.numero_autorizado.replace('+', ''))

            time.sleep(2)

            # Hacer clic en el primer resultado
            chat_result = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='cell-frame-container']"))
            )
            chat_result.click()

            print(f"✅ Chat abierto con {self.numero_autorizado}")
            return True

        except Exception as e:
            print(f"❌ Error buscando chat: {e}")
            return False

    def leer_ultimo_mensaje(self):
        """Lee el último mensaje del chat"""
        try:
            # Buscar todos los mensajes
            mensajes = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='msg-container']")

            if not mensajes:
                return None

            # Obtener el último mensaje
            ultimo_elemento = mensajes[-1]

            # Verificar si es mensaje entrante (no enviado por nosotros)
            es_entrante = ultimo_elemento.find_elements(By.CSS_SELECTOR, "[data-testid='msg-meta']")

            if es_entrante:
                # Buscar el texto del mensaje
                texto_elements = ultimo_elemento.find_elements(By.CSS_SELECTOR, "span.selectable-text")

                if texto_elements:
                    mensaje = texto_elements[0].text.strip()

                    # Verificar si es un mensaje nuevo
                    if mensaje != self.ultimo_mensaje and mensaje:
                        print(f"📥 Nuevo mensaje: {mensaje[:50]}{'...' if len(mensaje) > 50 else ''}")
                        self.ultimo_mensaje = mensaje
                        return mensaje

            return None

        except Exception as e:
            print(f"❌ Error leyendo mensajes: {e}")
            return None

    def enviar_respuesta(self, respuesta: str):
        """Envía respuesta al chat actual"""
        try:
            # Buscar la caja de texto
            text_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']"))
            )

            # Escribir mensaje
            text_box.click()
            text_box.clear()

            # Enviar línea por línea para manejar saltos de línea
            lineas = respuesta.split('\n')
            for i, linea in enumerate(lineas):
                text_box.send_keys(linea)
                if i < len(lineas) - 1:  # No enviar shift+enter en la última línea
                    from selenium.webdriver.common.keys import Keys
                    text_box.send_keys(Keys.SHIFT + Keys.ENTER)

            time.sleep(1)

            # Buscar y hacer clic en el botón enviar
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
            send_button.click()

            print(f"📤 Respuesta enviada: {respuesta[:50]}{'...' if len(respuesta) > 50 else ''}")
            return True

        except Exception as e:
            print(f"❌ Error enviando respuesta: {e}")
            return False

    def monitorear_mensajes(self):
        """Loop principal de monitoreo"""
        print("🔄 Iniciando monitoreo de mensajes...")

        while self.activo:
            try:
                # Leer nuevo mensaje
                nuevo_mensaje = self.leer_ultimo_mensaje()

                if nuevo_mensaje:
                    # Procesar con el agente
                    print(f"🤖 Procesando: {nuevo_mensaje}")
                    respuesta = self.agente.procesar_comando(nuevo_mensaje)

                    # Enviar respuesta
                    if self.enviar_respuesta(respuesta):
                        print("✅ Conversación procesada correctamente")
                    else:
                        print("❌ Error enviando respuesta")

                # Esperar antes del siguiente check
                time.sleep(5)  # Verificar cada 5 segundos

            except KeyboardInterrupt:
                print("\n⚠️ Deteniendo monitor...")
                break
            except Exception as e:
                print(f"❌ Error en monitoreo: {e}")
                time.sleep(10)  # Esperar más tiempo si hay error

    def iniciar_monitor(self):
        """Inicia el sistema completo"""
        try:
            print("🚀 INICIANDO MONITOR WHATSAPP SEACE")
            print("=" * 50)

            # Configurar driver
            self.setup_driver()

            # Conectar WhatsApp Web
            if not self.iniciar_whatsapp_web():
                print("❌ No se pudo conectar a WhatsApp Web")
                return

            # Enviar mensaje de inicio al número autorizado
            print("📱 Enviando mensaje de activación...")
            mensaje_inicio = self.agente.procesar_comando("/inicio")

            # Buscar chat y enviar mensaje
            if self.buscar_chat_autorizado():
                self.enviar_respuesta(mensaje_inicio)

                # Iniciar monitoreo
                self.monitorear_mensajes()
            else:
                print("❌ No se pudo abrir el chat")

        except Exception as e:
            print(f"❌ Error general: {e}")
        finally:
            self.cerrar()

    def cerrar(self):
        """Cierra el navegador"""
        if self.driver:
            print("🔚 Cerrando monitor...")
            self.driver.quit()

def iniciar_bot_conversacional():
    """Función principal para iniciar el bot"""
    monitor = MonitorWhatsApp()

    try:
        monitor.iniciar_monitor()
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        monitor.cerrar()

if __name__ == "__main__":
    # Crear menú de opciones
    print("🤖 AGENTE WHATSAPP SEACE")
    print("=" * 40)
    print("1. Iniciar bot conversacional (monitor completo)")
    print("2. Solo demo de comandos")
    print("3. Enviar mensaje de activación")

    try:
        opcion = input("\nElige una opción (1-3): ").strip()
    except:
        opcion = "1"  # Default para entorno automatizado

    if opcion == "1":
        iniciar_bot_conversacional()
    elif opcion == "2":
        from agente_whatsapp import demo_agente
        demo_agente()
    elif opcion == "3":
        # Solo enviar mensaje de inicio
        agente = AgenteWhatsAppSEACE()
        mensaje = agente.procesar_comando("/inicio")
        print("Mensaje de activación:")
        print(mensaje)

        if agente.enviar_mensaje(mensaje):
            print("✅ Mensaje enviado")
        else:
            print("❌ Error enviando")
    else:
        print("Opción no válida")