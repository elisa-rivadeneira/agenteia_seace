#!/usr/bin/env python3
"""
Servidor Webhook Local para Evolution API + Agente SEACE
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Almacenar mensajes recibidos
mensajes_recibidos = []

# Importar agente SEACE
from agente_whatsapp import AgenteWhatsAppSEACE
agente_seace = None

def inicializar_agente():
    """Inicializar agente SEACE en thread separado"""
    global agente_seace
    try:
        print("🔄 Inicializando agente SEACE...")
        agente_seace = AgenteWhatsAppSEACE()
        print("🤖 Agente SEACE inicializado en webhook server")
    except Exception as e:
        print(f"❌ ERROR al inicializar agente: {e}")
        import traceback
        traceback.print_exc()
        agente_seace = None

@app.route('/webhook', methods=['POST'])
@app.route('/webhook/<path:event_type>', methods=['POST'])
def webhook_evolution(event_type=None):
    """Endpoint para recibir mensajes de Evolution API"""
    try:
        data = request.json
        print(f"\n📨 WEBHOOK RECIBIDO: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📋 Data: {json.dumps(data, indent=2)}")

        # Guardar mensaje
        mensajes_recibidos.append({
            'timestamp': datetime.now().isoformat(),
            'data': data
        })

        # Procesar si es un mensaje de texto entrante
        if data.get('event') == 'messages.upsert':
            mensaje_info = data.get('data', {})

            # Verificar que es un mensaje entrante (no enviado por nosotros)
            if not mensaje_info.get('key', {}).get('fromMe', True):
                numero_remitente = mensaje_info.get('key', {}).get('remoteJid', '')
                texto_mensaje = mensaje_info.get('message', {}).get('conversation', '')

                if texto_mensaje:
                    print(f"💬 Mensaje de {numero_remitente}: {texto_mensaje}")

                    # Procesar comando con agente SEACE en thread separado
                    if agente_seace:
                        def procesar_y_responder():
                            respuesta = procesar_mensaje_con_agente(texto_mensaje, numero_remitente)
                            if respuesta:
                                enviar_respuesta_automatica(respuesta, numero_remitente)

                        thread = threading.Thread(target=procesar_y_responder)
                        thread.daemon = True
                        thread.start()
                        print(f"⚡ Procesando mensaje en background...")

        return jsonify({'status': 'success', 'received': True})

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

def procesar_mensaje_con_agente(mensaje: str, numero: str):
    """Procesar mensaje con agente SEACE"""
    try:
        print(f"🧠 Procesando con agente: {mensaje}")

        # Usar el procesador del agente que integra IA
        respuesta = agente_seace.procesar_comando(mensaje)
        return respuesta

    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")
        import traceback
        traceback.print_exc()
        return None

def enviar_respuesta_automatica(respuesta: str, numero_destino: str):
    """Enviar respuesta automática usando Evolution API"""
    try:
        import requests
        import os

        # Limpiar número
        clean_number = numero_destino.replace('@s.whatsapp.net', '').replace('+', '')

        # Configuración desde variables de entorno
        api_url = os.getenv('EVOLUTION_API_URL', 'https://automation-evolution-api.gnrjtm.easypanel.host')
        api_key = os.getenv('EVOLUTION_API_KEY')
        instance_name = os.getenv('EVOLUTION_INSTANCE_NAME')

        if not api_key or not instance_name:
            print("❌ EVOLUTION_API_KEY o EVOLUTION_INSTANCE_NAME no configurados")
            return

        url = f"{api_url}/message/sendText/{instance_name}"

        headers = {
            'Content-Type': 'application/json',
            'apikey': api_key
        }

        data = {
            'number': clean_number,
            'text': respuesta
        }

        response = requests.post(url, json=data, headers=headers, timeout=120)

        if response.status_code == 201:
            print(f"✅ Respuesta automática enviada a {clean_number}")
        else:
            print(f"❌ Error enviando respuesta: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error enviando respuesta automática: {e}")

@app.route('/status', methods=['GET'])
def status():
    """Estado del webhook server"""
    return jsonify({
        'status': 'running',
        'agente_activo': agente_seace is not None,
        'mensajes_recibidos': len(mensajes_recibidos),
        'ultimo_mensaje': mensajes_recibidos[-1] if mensajes_recibidos else None
    })

@app.route('/messages', methods=['GET'])
def get_messages():
    """Ver mensajes recibidos"""
    return jsonify({
        'total': len(mensajes_recibidos),
        'mensajes': mensajes_recibidos[-10:]  # Últimos 10
    })

@app.route('/send', methods=['POST'])
def send_manual():
    """Enviar mensaje manual para testing"""
    try:
        data = request.json
        mensaje = data.get('message', '')
        numero = data.get('number', '51967717179')

        if agente_seace:
            success = agente_seace.enviar_mensaje(mensaje)
            return jsonify({'success': success, 'message': 'Mensaje enviado'})
        else:
            return jsonify({'success': False, 'error': 'Agente no inicializado'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def iniciar_servidor():
    """Iniciar servidor webhook"""
    print("🚀 INICIANDO WEBHOOK SERVER PARA EVOLUTION API")
    print("=" * 60)

    # Inicializar agente ANTES de Flask (de forma síncrona para ver errores)
    inicializar_agente()

    print("\n🌐 Servidor webhook corriendo en:")
    print("   http://localhost:5000/webhook")
    print("   http://localhost:5000/status")
    print("   http://localhost:5000/messages")

    print("\n🔧 Para exponer públicamente (usar en otra terminal):")
    print("   ngrok http 5000")
    print("   Luego configura la URL de ngrok en Evolution API")

    # Iniciar Flask
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    iniciar_servidor()