#!/usr/bin/env python3
"""
Servidor Webhook Local para Evolution API + Agente SEACE
"""

from flask import Flask, request, jsonify, render_template_string, redirect, session
from functools import wraps
import json
from datetime import datetime
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'seace-admin-secret-key-change-this')

# Almacenar mensajes recibidos
mensajes_recibidos = []

# Importar agente SEACE
from agente_whatsapp import AgenteWhatsAppSEACE
from conversaciones_logger import log_conversacion
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
                numero_remitente = mensaje_info.get('key', {}).get('remoteJidAlt') or mensaje_info.get('key', {}).get('remoteJid', '')
                texto_mensaje = mensaje_info.get('message', {}).get('conversation', '')
                push_name = mensaje_info.get('pushName', '')

                if texto_mensaje:
                    print(f"💬 Mensaje de {numero_remitente}: {texto_mensaje}")

                    # Procesar comando con agente SEACE en thread separado
                    if agente_seace:
                        def procesar_y_responder():
                            respuesta = procesar_mensaje_con_agente(texto_mensaje, numero_remitente)
                            if respuesta:
                                # Log conversación
                                log_conversacion(numero_remitente, texto_mensaje, respuesta, push_name)
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

# ===== ADMIN ROUTES =====

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

def require_auth(f):
    """Decorator para requerir autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login del admin"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect('/admin')
        else:
            return render_template_string(LOGIN_HTML, error="Contraseña incorrecta")
    return render_template_string(LOGIN_HTML, error=None)

@app.route('/admin/logout')
def admin_logout():
    """Logout del admin"""
    session.pop('admin_authenticated', None)
    return redirect('/admin/login')

@app.route('/admin')
@require_auth
def admin_dashboard():
    """Dashboard del admin"""
    from conversaciones_logger import obtener_todas_conversaciones, obtener_estadisticas

    conversaciones = obtener_todas_conversaciones()
    stats = obtener_estadisticas()

    # Ordenar por última interacción
    conversaciones_lista = sorted(
        conversaciones.items(),
        key=lambda x: x[1].get('ultima_interaccion', ''),
        reverse=True
    )

    return render_template_string(ADMIN_DASHBOARD_HTML,
                                 conversaciones=conversaciones_lista,
                                 stats=stats)

@app.route('/admin/conversacion/<numero>')
@require_auth
def admin_conversacion(numero):
    """Ver historial de una conversación"""
    from conversaciones_logger import obtener_conversacion

    conversacion = obtener_conversacion(numero)
    if not conversacion:
        return "Conversación no encontrada", 404

    return render_template_string(CONVERSACION_DETAIL_HTML,
                                 numero=numero,
                                 conversacion=conversacion)

@app.route('/admin/conversacion/<numero>/json')
@require_auth
def admin_conversacion_json(numero):
    """API JSON para obtener conversación"""
    from conversaciones_logger import obtener_conversacion

    conversacion = obtener_conversacion(numero)
    if not conversacion:
        return jsonify({'error': 'Not found'}), 404

    return jsonify(conversacion)

# Templates HTML
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login - SEACE Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            width: 300px;
        }
        h2 { text-align: center; color: #333; }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 10px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #5568d3; }
        .error {
            color: red;
            text-align: center;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🤖 SEACE Bot Admin</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Ingresar</button>
        </form>
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Admin - SEACE Bot</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f2f5;
            height: 100vh;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 20px; }
        .header .logout {
            color: white;
            text-decoration: none;
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 5px;
        }
        .main-container {
            display: flex;
            height: calc(100vh - 65px);
        }
        .sidebar {
            width: 350px;
            background: white;
            border-right: 1px solid #e1e4e8;
            display: flex;
            flex-direction: column;
        }
        .stats-bar {
            padding: 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #e1e4e8;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        .stat-mini {
            text-align: center;
        }
        .stat-mini .label {
            font-size: 10px;
            color: #666;
            text-transform: uppercase;
        }
        .stat-mini .value {
            font-size: 20px;
            font-weight: bold;
            color: #667eea;
        }
        .conversations-list {
            flex: 1;
            overflow-y: auto;
        }
        .conversation-item {
            padding: 15px;
            border-bottom: 1px solid #f0f2f5;
            cursor: pointer;
            transition: background 0.2s;
        }
        .conversation-item:hover,
        .conversation-item.active {
            background: #f5f7fa;
        }
        .conversation-item .numero {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .conversation-item .meta {
            font-size: 12px;
            color: #666;
            display: flex;
            justify-content: space-between;
        }
        .conversation-item .badge {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
        }
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #e5ddd5;
        }
        .chat-header {
            background: #f0f2f5;
            padding: 15px 20px;
            border-bottom: 1px solid #d1d7db;
        }
        .chat-header h2 {
            font-size: 16px;
            color: #333;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            max-height: calc(100vh - 200px);
        }
        .message {
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
        }
        .message-user {
            align-items: flex-end;
        }
        .message-bot {
            align-items: flex-start;
        }
        .message-bubble {
            max-width: 65%;
            padding: 8px 12px;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .message-user .message-bubble {
            background: #dcf8c6;
        }
        .message-bot .message-bubble {
            background: white;
        }
        .message-time {
            font-size: 11px;
            color: #667781;
            margin-top: 4px;
            padding: 0 5px;
        }
        .message-text {
            font-size: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .empty-state {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #667781;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 SEACE Bot - Admin Dashboard</h1>
        <a href="/admin/logout" class="logout">Cerrar sesión</a>
    </div>

    <div class="main-container">
        <div class="sidebar">
            <div class="stats-bar">
                <div class="stats-grid">
                    <div class="stat-mini">
                        <div class="label">Usuarios</div>
                        <div class="value">{{ stats.total_usuarios }}</div>
                    </div>
                    <div class="stat-mini">
                        <div class="label">Mensajes</div>
                        <div class="value">{{ stats.total_mensajes }}</div>
                    </div>
                    <div class="stat-mini">
                        <div class="label">Promedio</div>
                        <div class="value">{{ (stats.total_mensajes / stats.total_usuarios) | round(1) if stats.total_usuarios > 0 else 0 }}</div>
                    </div>
                </div>
            </div>

            <div class="conversations-list">
                {% for numero, conv in conversaciones %}
                <div class="conversation-item" onclick="loadConversation('{{ numero }}')">
                    <div class="numero">📱 {{ numero.split('@')[0] }}</div>
                    {% if conv.get('nombre') %}
                    <div style="font-size: 12px; color: #666; margin: 3px 0 8px 0;">👤 {{ conv.nombre }}</div>
                    {% endif %}
                    <div class="meta">
                        <span>{{ conv.ultima_interaccion[11:16] }} - {{ conv.ultima_interaccion[8:10]}}/{{ conv.ultima_interaccion[5:7] }}</span>
                        <span class="badge">{{ conv.total_mensajes }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="chat-area">
            <div id="chat-content" class="empty-state">
                Selecciona una conversación para ver el historial
            </div>
        </div>
    </div>

    <script>
        function loadConversation(numero) {
            fetch('/admin/conversacion/' + numero + '/json')
                .then(r => r.json())
                .then(data => {
                    const chatContent = document.getElementById('chat-content');
                    chatContent.className = '';
                    const numeroLimpio = numero.split('@')[0];
                    const nombreHTML = data.nombre ? `<div style="font-size: 14px; color: #667781; margin-top: 3px;">👤 ${data.nombre}</div>` : '';
                    chatContent.innerHTML = `
                        <div class="chat-header">
                            <h2>📱 ${numeroLimpio}</h2>
                            ${nombreHTML}
                            <div style="font-size: 12px; color: #667781; margin-top: 5px;">
                                Primera interacción: ${data.primera_interaccion.substring(0, 19)} |
                                Total mensajes: ${data.total_mensajes}
                            </div>
                        </div>
                        <div class="chat-messages" id="messages"></div>
                    `;

                    const messagesDiv = document.getElementById('messages');
                    data.historial.forEach(msg => {
                        messagesDiv.innerHTML += `
                            <div class="message message-user">
                                <div class="message-bubble">
                                    <div class="message-text">${msg.mensaje_usuario}</div>
                                </div>
                                <div class="message-time">👤 Usuario - ${msg.timestamp.substring(11, 19)}</div>
                            </div>
                            <div class="message message-bot">
                                <div class="message-bubble">
                                    <div class="message-text">${msg.respuesta_bot}</div>
                                </div>
                                <div class="message-time">🤖 Bot - ${msg.timestamp.substring(11, 19)}</div>
                            </div>
                        `;
                    });

                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                });

            // Mark as active
            document.querySelectorAll('.conversation-item').forEach(el => el.classList.remove('active'));
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""

CONVERSACION_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Conversación {{ numero }} - SEACE Bot</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 24px; }
        .header a {
            color: white;
            text-decoration: none;
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 5px;
            float: right;
        }
        .container {
            max-width: 900px;
            margin: 20px auto;
            padding: 20px;
        }
        .info-box {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .info-box h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .messages {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .message {
            margin-bottom: 20px;
            padding: 15px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .message-timestamp {
            font-size: 12px;
            color: #666;
            margin-bottom: 10px;
        }
        .message-user {
            background: #e3f2fd;
            border-left-color: #2196F3;
        }
        .message-bot {
            background: #f3e5f5;
            border-left-color: #9c27b0;
        }
        .message-content {
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .label {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/admin">← Volver</a>
        <h1>📱 Conversación: {{ numero }}</h1>
    </div>

    <div class="container">
        <div class="info-box">
            <h3>Información</h3>
            <p><strong>Número:</strong> {{ numero }}</p>
            <p><strong>Primera interacción:</strong> {{ conversacion.primera_interaccion[:19] }}</p>
            <p><strong>Última interacción:</strong> {{ conversacion.ultima_interaccion[:19] }}</p>
            <p><strong>Total mensajes:</strong> {{ conversacion.total_mensajes }}</p>
        </div>

        <div class="messages">
            <h3 style="margin-bottom: 20px;">Historial de mensajes</h3>
            {% for msg in conversacion.historial %}
            <div class="message message-user">
                <div class="message-timestamp">👤 Usuario - {{ msg.timestamp[:19] }}</div>
                <div class="message-content">{{ msg.mensaje_usuario }}</div>
            </div>
            <div class="message message-bot">
                <div class="message-timestamp">🤖 Bot - {{ msg.timestamp[:19] }}</div>
                <div class="message-content">{{ msg.respuesta_bot }}</div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

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
    print("   http://localhost:5000/admin (Dashboard)")

    print("\n🔧 Para exponer públicamente (usar en otra terminal):")
    print("   ngrok http 5000")
    print("   Luego configura la URL de ngrok en Evolution API")

    # Iniciar Flask
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    iniciar_servidor()