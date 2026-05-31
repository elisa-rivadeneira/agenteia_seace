#!/usr/bin/env python3
"""
CHAT WHATSAPP COMPLETO - Sistema bidireccional real
Permite conversación completa: envía Y recibe mensajes automáticamente
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
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from agente_whatsapp import AgenteWhatsAppSEACE
import urllib.parse

class ChatWhatsAppCompleto:
    def __init__(self):
        """Inicializa chat bidireccional completo"""
        self.driver = None
        self.wait = None
        self.agente = AgenteWhatsAppSEACE()
        self.mensajes_procesados = set()
        self.activo = True

        # Cargar configuración
        with open('config_empresa.json', 'r') as f:
            config = json.load(f)
        self.numero_autorizado = config['notificaciones']['whatsapp']
        self.chat_abierto = False

        print(f"🤖 Chat WhatsApp bidireccional inicializado")
        print(f"📱 Para: {self.numero_autorizado}")

    def setup_driver(self):
        """Configura Chrome optimizado para WhatsApp"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1200,800')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')

        # Mantener sesión
        options.add_argument('--user-data-dir=/tmp/whatsapp_chat_session')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)

    def abrir_whatsapp_directo(self):
        """Abre WhatsApp Web directamente en el chat"""
        try:
            clean_phone = self.numero_autorizado.replace('+', '').replace(' ', '')
            url = f"https://web.whatsapp.com/send?phone={clean_phone}"

            print(f"🌐 Abriendo chat directo con {self.numero_autorizado}")
            self.driver.get(url)

            print("⏳ Esperando carga de WhatsApp Web...")
            time.sleep(15)

            # Verificar si el chat se abrió
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']"))
                )
                print("✅ Chat abierto correctamente")
                self.chat_abierto = True
                return True
            except:
                print("⚠️ Chat no completamente cargado, pero continuando...")
                self.chat_abierto = True
                return True

        except Exception as e:
            print(f"❌ Error abriendo chat: {e}")
            return False

    def enviar_mensaje_directo(self, mensaje: str) -> bool:
        """Envía mensaje directamente en el chat actual"""
        try:
            if not self.chat_abierto:
                print("❌ Chat no está abierto")
                return False

            print(f"📤 Enviando: {mensaje[:50]}{'...' if len(mensaje) > 50 else ''}")

            # Buscar caja de texto
            text_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']"))
            )

            # Hacer clic y limpiar
            text_box.click()
            text_box.clear()

            # Escribir mensaje línea por línea
            lineas = mensaje.split('\n')
            for i, linea in enumerate(lineas):
                text_box.send_keys(linea)
                if i < len(lineas) - 1:
                    text_box.send_keys(Keys.SHIFT + Keys.ENTER)

            time.sleep(1)

            # Enviar con Enter
            text_box.send_keys(Keys.ENTER)

            print("✅ Mensaje enviado")
            time.sleep(2)  # Pausa para que se procese
            return True

        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return False

    def leer_mensajes_nuevos(self):
        """Lee mensajes nuevos del chat"""
        try:
            if not self.chat_abierto:
                return []

            # Buscar todos los mensajes
            mensajes_elementos = self.driver.find_elements(
                By.CSS_SELECTOR,
                "[data-testid='msg-container']"
            )

            mensajes_nuevos = []

            for elemento in mensajes_elementos[-5:]:  # Solo los últimos 5
                try:
                    # Verificar si es mensaje entrante (no nuestro)
                    es_entrante = elemento.find_elements(
                        By.CSS_SELECTOR,
                        "[data-testid='msg-meta']"
                    )

                    if es_entrante:
                        # Obtener texto del mensaje
                        textos = elemento.find_elements(
                            By.CSS_SELECTOR,
                            "span.selectable-text"
                        )

                        if textos:
                            mensaje = textos[0].text.strip()

                            # Verificar si es nuevo
                            if mensaje and mensaje not in self.mensajes_procesados:
                                print(f"📥 Nuevo mensaje: {mensaje[:30]}...")
                                self.mensajes_procesados.add(mensaje)
                                mensajes_nuevos.append(mensaje)

                except Exception as e:
                    continue

            return mensajes_nuevos

        except Exception as e:
            print(f"❌ Error leyendo mensajes: {e}")
            return []

    def procesar_conversacion(self):
        """Loop principal de conversación"""
        print("💬 Iniciando conversación bidireccional...")

        # Enviar mensaje de bienvenida
        mensaje_inicio = self.agente.procesar_comando("/inicio")
        if self.enviar_mensaje_directo(mensaje_inicio):
            print("📤 Mensaje de bienvenida enviado")

        # Loop de conversación
        ultimo_check = time.time()

        while self.activo:
            try:
                # Leer mensajes nuevos cada 3 segundos
                if time.time() - ultimo_check >= 3:
                    mensajes_nuevos = self.leer_mensajes_nuevos()

                    for mensaje in mensajes_nuevos:
                        print(f"\n👤 Usuario escribió: {mensaje}")

                        # Procesar con el agente
                        respuesta = self.agente.procesar_comando(mensaje)

                        print(f"🤖 Agente responde: {respuesta[:50]}...")

                        # Enviar respuesta
                        if self.enviar_mensaje_directo(respuesta):
                            print("✅ Respuesta enviada")
                        else:
                            print("❌ Error enviando respuesta")

                        time.sleep(2)  # Pausa entre respuestas

                    ultimo_check = time.time()

                time.sleep(1)  # Check cada segundo

            except KeyboardInterrupt:
                print("\n⚠️ Deteniendo chat...")
                break
            except Exception as e:
                print(f"❌ Error en conversación: {e}")
                time.sleep(5)

    def iniciar_chat_completo(self):
        """Inicia el sistema de chat completo"""
        try:
            print("🚀 INICIANDO CHAT WHATSAPP COMPLETO")
            print("=" * 50)

            # Configurar driver
            self.setup_driver()

            # Abrir WhatsApp Web en el chat
            if not self.abrir_whatsapp_directo():
                print("❌ No se pudo abrir WhatsApp Web")
                return

            print("✅ Sistema listo para conversar")
            print("📝 El agente responderá automáticamente a tus mensajes")
            print("💡 Escribe comandos como /estado, /reporte, /escanear")
            print("🔄 Presiona Ctrl+C para detener")

            # Iniciar conversación
            self.procesar_conversacion()

        except Exception as e:
            print(f"❌ Error general: {e}")
        finally:
            self.cerrar()

    def cerrar(self):
        """Cierra el chat"""
        if self.driver:
            print("🔚 Cerrando chat...")
            time.sleep(2)
            self.driver.quit()

def test_chat_simple():
    """Prueba simple del chat"""
    print("🧪 PRUEBA CHAT SIMPLE")
    print("=" * 30)

    chat = ChatWhatsAppCompleto()

    try:
        chat.setup_driver()

        if chat.abrir_whatsapp_directo():
            print("✅ Chat abierto")

            # Enviar mensaje de prueba
            mensaje_test = "🧪 Prueba de chat automático - El agente está funcionando!"

            if chat.enviar_mensaje_directo(mensaje_test):
                print("✅ Mensaje de prueba enviado")

            # Leer mensajes por 30 segundos
            print("📖 Leyendo mensajes por 30 segundos...")
            inicio = time.time()

            while time.time() - inicio < 30:
                mensajes = chat.leer_mensajes_nuevos()
                if mensajes:
                    for msg in mensajes:
                        print(f"📥 Mensaje recibido: {msg}")
                time.sleep(3)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        chat.cerrar()

if __name__ == "__main__":
    print("🤖 CHAT WHATSAPP SEACE - BIDIRECCIONAL")
    print("=" * 50)

    try:
        opcion = input("""
Selecciona:
1. Chat completo (conversación automática)
2. Prueba simple (solo envío)
3. Solo mensaje de activación

Opción (1-3): """).strip()
    except:
        opcion = "1"

    if opcion == "1":
        chat = ChatWhatsAppCompleto()
        chat.iniciar_chat_completo()
    elif opcion == "2":
        test_chat_simple()
    elif opcion == "3":
        agente = AgenteWhatsAppSEACE()
        mensaje = agente.procesar_comando("/inicio")
        print("Mensaje de activación:")
        print(mensaje)
    else:
        # Default: chat completo
        chat = ChatWhatsAppCompleto()
        chat.iniciar_chat_completo()