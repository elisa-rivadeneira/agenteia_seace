#!/usr/bin/env python3
"""
Servidor Webhook Local para Evolution API + Agente SEACE
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Almacenar mensajes recibidos
mensajes_recibidos = []

# Importar agente SEACE
from agente_whatsapp import AgenteWhatsAppSEACE
agente_seace = None

def inicializar_agente():
    """Inicializar agente SEACE en thread separado"""
    global agente_seace
    agente_seace = AgenteWhatsAppSEACE()
    print("🤖 Agente SEACE inicializado en webhook server")

@app.route('/webhook', methods=['POST'])
def webhook_evolution():
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

                    # Procesar comando con agente SEACE
                    if agente_seace:
                        respuesta = procesar_mensaje_con_agente(texto_mensaje, numero_remitente)
                        if respuesta:
                            # Enviar respuesta automática
                            enviar_respuesta_automatica(respuesta, numero_remitente)

        return jsonify({'status': 'success', 'received': True})

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

def procesar_mensaje_con_agente(mensaje: str, numero: str):
    """Procesar mensaje con agente SEACE"""
    try:
        print(f"🧠 Procesando con agente: {mensaje}")

        # Si el mensaje empieza con /, es un comando
        if mensaje.startswith('/'):
            respuesta = agente_seace.procesar_comando(mensaje)
            return respuesta

        # Si no es comando, procesar como conversación natural
        elif any(palabra in mensaje.lower() for palabra in ['estado', 'oportunidades', 'seace', 'reporte']):
            # Mapear palabras clave a comandos
            if 'estado' in mensaje.lower():
                return agente_seace.procesar_comando('/estado')
            elif 'urgentes' in mensaje.lower() or 'urgente' in mensaje.lower():
                return agente_seace.procesar_comando('/urgentes')
            elif 'reporte' in mensaje.lower():
                return agente_seace.procesar_comando('/reporte')
            elif 'oportunidades' in mensaje.lower() or 'escanear' in mensaje.lower():
                return agente_seace.procesar_comando('/escanear')
            else:
                return agente_seace.procesar_comando('/ayuda')

        # Respuesta por defecto
        return """🤖 Hola! Soy tu agente SEACE.

Comandos disponibles:
• /estado - Estado del sistema
• /escanear - Buscar oportunidades
• /urgentes - Oportunidades urgentes
• /reporte - Reporte completo
• /ayuda - Lista de comandos

O puedes escribir: "estado", "urgentes", "reporte", etc."""

    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")
        return None

def enviar_respuesta_automatica(respuesta: str, numero_destino: str):
    """Enviar respuesta automática usando Evolution API"""
    try:
        import requests

        # Limpiar número
        clean_number = numero_destino.replace('@s.whatsapp.net', '').replace('+', '')

        url = "https://automation-evolution-api.gnrjtm.easypanel.host/message/sendText/Elisa Rivadeneira"

        headers = {
            'Content-Type': 'application/json',
            'apikey': '429683C4C977415CAAFCCE10F7D57E11'
        }

        data = {
            'number': clean_number,
            'text': respuesta
        }

        response = requests.post(url, json=data, headers=headers, timeout=30)

        if response.status_code == 201:
            print(f"✅ Respuesta automática enviada a {clean_number}")
        else:
            print(f"❌ Error enviando respuesta: {response.status_code}")

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

    # Inicializar agente en thread separado
    thread_agente = threading.Thread(target=inicializar_agente)
    thread_agente.daemon = True
    thread_agente.start()

    print("🌐 Servidor webhook corriendo en:")
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