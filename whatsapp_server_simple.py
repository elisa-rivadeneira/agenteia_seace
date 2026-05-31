#!/usr/bin/env python3
"""
Servidor WhatsApp simple - Envío automático REAL
Basado en whatsapp-web.js, más simple que Evolution API
"""

import subprocess
import time
import requests
import json
from datetime import datetime
import os

def instalar_dependencias():
    """Instala whatsapp-web.js si no está instalado"""
    try:
        # Verificar si ya está instalado
        result = subprocess.run(['npm', 'list', 'whatsapp-web.js'],
                              capture_output=True, text=True)

        if 'whatsapp-web.js' in result.stdout:
            print("✅ whatsapp-web.js ya está instalado")
            return True

        print("📦 Instalando whatsapp-web.js...")
        subprocess.run(['npm', 'install', 'whatsapp-web.js', 'qrcode-terminal'],
                      check=True)
        print("✅ whatsapp-web.js instalado")
        return True

    except Exception as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def crear_servidor_whatsapp():
    """Crea un servidor WhatsApp simple"""
    servidor_code = '''
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const client = new Client({
    authStrategy: new LocalAuth()
});

client.on('qr', (qr) => {
    console.log('📱 Escanea este QR code con WhatsApp:');
    qrcode.generate(qr, {small: true});
});

client.on('ready', () => {
    console.log('✅ WhatsApp conectado exitosamente!');
    console.log('🚀 Servidor listo para envío automático');

    // Crear servidor HTTP simple para recibir mensajes
    const http = require('http');

    const server = http.createServer((req, res) => {
        if (req.method === 'POST' && req.url === '/send') {
            let body = '';

            req.on('data', chunk => {
                body += chunk.toString();
            });

            req.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    const { number, message } = data;

                    client.sendMessage(number + '@c.us', message)
                        .then(() => {
                            res.writeHead(200, {'Content-Type': 'application/json'});
                            res.end(JSON.stringify({success: true, message: 'Enviado'}));
                            console.log(`✅ Mensaje enviado a ${number}: ${message.substring(0, 50)}...`);
                        })
                        .catch(err => {
                            res.writeHead(500, {'Content-Type': 'application/json'});
                            res.end(JSON.stringify({success: false, error: err.message}));
                            console.log(`❌ Error enviando: ${err.message}`);
                        });
                } catch (err) {
                    res.writeHead(400, {'Content-Type': 'application/json'});
                    res.end(JSON.stringify({success: false, error: 'JSON inválido'}));
                }
            });
        } else if (req.method === 'GET' && req.url === '/status') {
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify({
                status: 'connected',
                ready: client.info !== null
            }));
        } else {
            res.writeHead(404);
            res.end('Not Found');
        }
    });

    server.listen(3001, () => {
        console.log('🌐 Servidor HTTP corriendo en puerto 3001');
        console.log('📡 Endpoint: POST /send');
        console.log('📊 Status: GET /status');
    });
});

client.on('message', message => {
    // Puedes agregar lógica para responder mensajes aquí
});

client.initialize();
'''

    # Guardar el código del servidor
    with open('whatsapp_server.js', 'w') as f:
        f.write(servidor_code)

    print("📁 Servidor WhatsApp creado: whatsapp_server.js")
    return True

def iniciar_servidor_background():
    """Inicia el servidor WhatsApp en background"""
    try:
        print("🚀 Iniciando servidor WhatsApp...")

        # Iniciar en background
        proceso = subprocess.Popen(
            ['node', 'whatsapp_server.js'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Esperar un poco para que inicie
        time.sleep(3)

        # Verificar si está corriendo
        if proceso.poll() is None:
            print("✅ Servidor WhatsApp iniciado en background")
            print("📱 Escanea el QR code para conectar")
            return proceso
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Error iniciando servidor: {stderr}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def enviar_mensaje_automatico(numero: str, mensaje: str):
    """Envía mensaje usando el servidor local"""
    try:
        url = "http://localhost:3001/send"

        data = {
            "number": numero.replace('+', '').replace(' ', ''),
            "message": mensaje
        }

        print(f"📤 Enviando mensaje automático a {numero}...")

        response = requests.post(url, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ ¡MENSAJE ENVIADO AUTOMÁTICAMENTE!")
                return True
            else:
                print(f"❌ Error: {result.get('error')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")

        return False

    except Exception as e:
        print(f"❌ Error enviando: {e}")
        return False

def verificar_servidor():
    """Verifica si el servidor está corriendo y conectado"""
    try:
        response = requests.get("http://localhost:3001/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"📊 Estado servidor: {status.get('status')}")
            print(f"📱 WhatsApp listo: {status.get('ready')}")
            return status.get('status') == 'connected'
    except Exception:
        print("❌ Servidor no está corriendo")
    return False

def setup_completo():
    """Setup completo del sistema WhatsApp automático"""
    print("🚀 SETUP WHATSAPP AUTOMÁTICO SIMPLE")
    print("=" * 50)

    # 1. Instalar dependencias
    print("\n1️⃣ Instalando dependencias...")
    if not instalar_dependencias():
        return False

    # 2. Crear servidor
    print("\n2️⃣ Creando servidor WhatsApp...")
    if not crear_servidor_whatsapp():
        return False

    # 3. Iniciar servidor
    print("\n3️⃣ Iniciando servidor...")
    proceso = iniciar_servidor_background()
    if not proceso:
        return False

    # 4. Esperar conexión
    print("\n4️⃣ Esperando conexión WhatsApp...")
    print("📱 Escanea el QR code que aparece arriba")

    max_intentos = 60  # 5 minutos
    for i in range(max_intentos):
        if verificar_servidor():
            print("✅ ¡WhatsApp conectado y listo!")
            break
        print(f"⏳ Esperando conexión... {i+1}/{max_intentos}")
        time.sleep(5)
    else:
        print("❌ Timeout esperando conexión")
        proceso.terminate()
        return False

    # 5. Test de envío
    print("\n5️⃣ Probando envío automático...")

    mensaje_test = f"""🚀 WHATSAPP AUTOMÁTICO FUNCIONANDO!
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Envío completamente automático
🤖 Sin intervención manual
📊 Sistema SEACE operativo

¡Configuración exitosa!"""

    if enviar_mensaje_automatico("+51967717179", mensaje_test):
        print("\n🎉 ¡SISTEMA COMPLETAMENTE OPERATIVO!")
        print("📱 Revisa tu WhatsApp - debe haber llegado el mensaje")
        print("✅ Ahora el agente SEACE puede enviar mensajes automáticos")

        # Guardar configuración
        with open('whatsapp_config_automatico.json', 'w') as f:
            json.dump({
                'servidor_activo': True,
                'puerto': 3001,
                'endpoint': 'http://localhost:3001/send',
                'configurado': datetime.now().isoformat()
            }, f, indent=2)

        return True
    else:
        print("❌ Error en el test")
        proceso.terminate()
        return False

def main():
    """Función principal"""
    # Verificar si ya está configurado
    if os.path.exists('whatsapp_config_automatico.json') and verificar_servidor():
        print("✅ Sistema ya está configurado y corriendo")

        mensaje_test = f"""🧪 TEST SISTEMA EXISTENTE
{datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ Sistema funcionando correctamente
📱 Envío automático operativo

¡Todo listo!"""

        enviar_mensaje_automatico("+51967717179", mensaje_test)
    else:
        print("🔧 Configurando sistema por primera vez...")
        setup_completo()

if __name__ == "__main__":
    main()