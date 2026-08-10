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

# Registrar blueprint de administración
from admin_routes import admin_bp
app.register_blueprint(admin_bp)

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
        respuesta = agente_seace.procesar_comando(mensaje, numero_usuario=numero)
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

@app.route('/')
def index():
    """Landing page"""
    # Leer y servir landing page
    with open('landing_page.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/robots.txt')
def robots():
    """Archivo robots.txt para bloquear buscadores"""
    with open('robots.txt', 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/plain'}

@app.route('/status', methods=['GET'])
def status():
    """Estado del webhook server"""
    comandos_disponibles = []
    if agente_seace:
        comandos_disponibles = list(agente_seace.comandos.keys())

    return jsonify({
        'status': 'running',
        'version': '2.6.1',
        'agente_activo': agente_seace is not None,
        'comandos_disponibles': comandos_disponibles,
        'tiene_comando_excel': '/excel' in comandos_disponibles,
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

@app.route('/admin/alertas')
@require_auth
def admin_alertas():
    """Página de configuración de alertas"""
    from alertas_manager import cargar_config_alertas, obtener_estadisticas_alertas
    from conversaciones_logger import obtener_todas_conversaciones

    config = cargar_config_alertas()
    stats = obtener_estadisticas_alertas()
    conversaciones = obtener_todas_conversaciones()

    # Preparar lista de contactos disponibles
    contactos = [
        {
            'numero': num,
            'nombre': conv.get('nombre', f"Usuario {num.split('@')[0][-4:]}"),
            'total_mensajes': conv.get('total_mensajes', 0)
        }
        for num, conv in conversaciones.items()
    ]

    return render_template_string(ADMIN_ALERTAS_HTML,
                                 config=config,
                                 stats=stats,
                                 usuarios=contactos)

# API para gestión de alertas
@app.route('/admin/alertas/destinatario/agregar', methods=['POST'])
@require_auth
def agregar_destinatario_alerta():
    """Agrega destinatario a las alertas"""
    from alertas_manager import agregar_destinatario

    data = request.json
    numero = data.get('numero', '')
    nombre = data.get('nombre', '')

    success = agregar_destinatario(numero, nombre)
    return jsonify({'success': success})

@app.route('/admin/alertas/destinatario/eliminar', methods=['POST'])
@require_auth
def eliminar_destinatario_alerta():
    """Elimina destinatario de las alertas"""
    from alertas_manager import eliminar_destinatario

    data = request.json
    numero = data.get('numero', '')

    success = eliminar_destinatario(numero)
    return jsonify({'success': success})

@app.route('/admin/alertas/destinatario/toggle', methods=['POST'])
@require_auth
def toggle_destinatario_alerta():
    """Activa/desactiva destinatario"""
    from alertas_manager import activar_desactivar_destinatario

    data = request.json
    numero = data.get('numero', '')
    activo = data.get('activo', False)

    success = activar_desactivar_destinatario(numero, activo)
    return jsonify({'success': success})

@app.route('/admin/alertas/horario/agregar', methods=['POST'])
@require_auth
def agregar_horario_alerta():
    """Agrega horario de alerta"""
    from alertas_manager import agregar_horario

    data = request.json
    hora = data.get('hora', '')
    descripcion = data.get('descripcion', '')

    success = agregar_horario(hora, descripcion)
    return jsonify({'success': success})

@app.route('/admin/alertas/horario/eliminar', methods=['POST'])
@require_auth
def eliminar_horario_alerta():
    """Elimina horario de alerta"""
    from alertas_manager import eliminar_horario

    data = request.json
    hora = data.get('hora', '')

    success = eliminar_horario(hora)
    return jsonify({'success': success})

@app.route('/admin/alertas/horario/toggle', methods=['POST'])
@require_auth
def toggle_horario_alerta():
    """Activa/desactiva horario"""
    from alertas_manager import activar_desactivar_horario

    data = request.json
    hora = data.get('hora', '')
    activo = data.get('activo', False)

    success = activar_desactivar_horario(hora, activo)
    return jsonify({'success': success})

@app.route('/admin/alertas/config/actualizar', methods=['POST'])
@require_auth
def actualizar_config_alertas():
    """Actualiza configuración de alertas"""
    from alertas_manager import actualizar_configuracion

    data = request.json
    score_minimo = data.get('score_minimo')
    max_oportunidades = data.get('max_oportunidades')

    success = actualizar_configuracion(score_minimo, max_oportunidades)
    return jsonify({'success': success})

@app.route('/admin/usuarios/agregar-manual', methods=['POST'])
@require_auth
def agregar_usuario_manual():
    """Agrega usuario manualmente al sistema"""
    from conversaciones_logger import registrar_usuario_manual

    data = request.json
    numero = data.get('numero')
    nombre = data.get('nombre')

    if not numero or not nombre:
        return jsonify({'success': False, 'error': 'Faltan datos'})

    success = registrar_usuario_manual(numero, nombre)
    return jsonify({'success': success})

@app.route('/admin/alertas/crear', methods=['POST'])
@require_auth
def crear_alerta_endpoint():
    """Crea una nueva alerta"""
    from database_manager import crear_alerta

    data = request.json
    nombre = data.get('nombre')
    segmento = data.get('segmento')
    horarios = data.get('horarios', [])
    dias_semana = data.get('dias_semana', [])
    usuarios = data.get('usuarios', [])
    score_minimo = data.get('score_minimo', 30)
    max_oportunidades = data.get('max_oportunidades', 5)

    if not nombre or not segmento or not horarios or not dias_semana or not usuarios:
        return jsonify({'success': False, 'error': 'Faltan campos obligatorios'})

    success = crear_alerta(nombre, segmento, horarios, dias_semana, usuarios, score_minimo, max_oportunidades)
    return jsonify({'success': success})

@app.route('/admin/alertas/actualizar', methods=['POST'])
@require_auth
def actualizar_alerta_endpoint():
    """Actualiza una alerta existente"""
    from database_manager import actualizar_alerta

    data = request.json
    alerta_id = data.get('id')
    datos = data.get('datos', {})

    if not alerta_id:
        return jsonify({'success': False, 'error': 'Falta ID de alerta'})

    success = actualizar_alerta(alerta_id, datos)
    return jsonify({'success': success})

@app.route('/admin/alertas/eliminar', methods=['POST'])
@require_auth
def eliminar_alerta_endpoint():
    """Elimina una alerta"""
    from database_manager import eliminar_alerta

    data = request.json
    alerta_id = data.get('id')

    if not alerta_id:
        return jsonify({'success': False, 'error': 'Falta ID de alerta'})

    success = eliminar_alerta(alerta_id)
    return jsonify({'success': success})

@app.route('/admin/alertas/toggle', methods=['POST'])
@require_auth
def toggle_alerta_endpoint():
    """Activa o desactiva una alerta"""
    from database_manager import activar_desactivar_alerta

    data = request.json
    alerta_id = data.get('id')
    activo = data.get('activo', False)

    if not alerta_id:
        return jsonify({'success': False, 'error': 'Falta ID de alerta'})

    success = activar_desactivar_alerta(alerta_id, activo)
    return jsonify({'success': success})

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
        .header a {
            color: white;
            text-decoration: none;
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 5px;
            transition: background 0.2s;
        }
        .header a:hover {
            background: rgba(255,255,255,0.3);
        }
        .header a:visited {
            color: white;
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
        <div>
            <a href="/admin/usuarios" style="margin-right: 10px;">⚙️ Configuración</a>
            <a href="/admin/logout" class="logout">Cerrar sesión</a>
        </div>
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

ADMIN_ALERTAS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Configuración de Alertas - SEACE Bot</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f2f5;
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
        .header a {
            color: white;
            text-decoration: none;
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 5px;
            margin-left: 10px;
        }
        .container {
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .stat-card .label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .section {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f2f5;
        }
        .horarios-list, .destinatarios-list {
            list-style: none;
        }
        .horario-item, .destinatario-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            margin-bottom: 10px;
            transition: all 0.2s;
        }
        .horario-item:hover, .destinatario-item:hover {
            background: #f8f9fa;
            border-color: #667eea;
        }
        .horario-info, .destinatario-info {
            flex: 1;
        }
        .horario-hora {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }
        .horario-desc {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        .destinatario-nombre {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .destinatario-numero {
            font-size: 12px;
            color: #666;
        }
        .actions {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        .btn-toggle {
            background: #28a745;
            color: white;
        }
        .btn-toggle.inactive {
            background: #6c757d;
        }
        .btn-delete {
            background: #dc3545;
            color: white;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn:hover {
            opacity: 0.8;
            transform: translateY(-2px);
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .add-form {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }
        .badge-active {
            background: #d4edda;
            color: #155724;
        }
        .badge-inactive {
            background: #f8d7da;
            color: #721c24;
        }
        .contactos-select {
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        }
        .contacto-option {
            padding: 10px;
            cursor: pointer;
            border-bottom: 1px solid #f0f2f5;
            transition: background 0.2s;
        }
        .contacto-option:hover {
            background: #f0f2f5;
        }
        .contacto-nombre {
            font-weight: 600;
        }
        .contacto-numero {
            font-size: 12px;
            color: #666;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⏰ Configuración de Alertas Automáticas</h1>
        <div>
            <a href="/admin">← Dashboard</a>
            <a href="/admin/logout">Cerrar sesión</a>
        </div>
    </div>

    <div class="container">
        <!-- Estadísticas -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Horarios Activos</div>
                <div class="value">{{ stats.horarios_activos }}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Horarios</div>
                <div class="value">{{ stats.total_horarios }}</div>
            </div>
            <div class="stat-card">
                <div class="label">Destinatarios Activos</div>
                <div class="value">{{ stats.destinatarios_activos }}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Destinatarios</div>
                <div class="value">{{ stats.total_destinatarios }}</div>
            </div>
        </div>

        <div class="alert alert-info">
            <strong>ℹ️ Información:</strong> Las alertas se envían automáticamente en los horarios configurados.
            Solo se notifican oportunidades nuevas con score ≥ {{ config.configuracion.score_minimo }}%.
        </div>

        <!-- Horarios de Alerta -->
        <div class="section">
            <h2>📅 Horarios de Alerta</h2>

            <ul class="horarios-list">
                {% for horario in config.horarios %}
                <li class="horario-item">
                    <div class="horario-info">
                        <div class="horario-hora">{{ horario.hora }}</div>
                        <div class="horario-desc">{{ horario.descripcion }}</div>
                    </div>
                    <div class="actions">
                        <span class="badge {% if horario.activo %}badge-active{% else %}badge-inactive{% endif %}">
                            {% if horario.activo %}ACTIVO{% else %}INACTIVO{% endif %}
                        </span>
                        <button class="btn btn-toggle {% if not horario.activo %}inactive{% endif %}"
                                onclick="toggleHorario('{{ horario.hora }}', {{ 'false' if horario.activo else 'true' }})">
                            {% if horario.activo %}Desactivar{% else %}Activar{% endif %}
                        </button>
                        <button class="btn btn-delete" onclick="eliminarHorario('{{ horario.hora }}')">Eliminar</button>
                    </div>
                </li>
                {% endfor %}
            </ul>

            <!-- Formulario agregar horario -->
            <div class="add-form">
                <h3 style="margin-bottom: 15px;">➕ Agregar Nuevo Horario</h3>
                <div class="form-group">
                    <label>Hora (HH:MM)</label>
                    <input type="time" id="nueva-hora" placeholder="14:00">
                </div>
                <div class="form-group">
                    <label>Descripción</label>
                    <input type="text" id="nueva-hora-desc" placeholder="Ej: Alerta de medio día">
                </div>
                <button class="btn btn-primary" onclick="agregarHorario()">Agregar Horario</button>
            </div>
        </div>

        <!-- Destinatarios -->
        <div class="section">
            <h2>📱 Destinatarios de Alertas</h2>

            <ul class="destinatarios-list">
                {% for dest in config.destinatarios %}
                <li class="destinatario-item">
                    <div class="destinatario-info">
                        <div class="destinatario-nombre">{{ dest.nombre }}</div>
                        <div class="destinatario-numero">📞 {{ dest.numero }}</div>
                    </div>
                    <div class="actions">
                        <span class="badge {% if dest.activo %}badge-active{% else %}badge-inactive{% endif %}">
                            {% if dest.activo %}ACTIVO{% else %}INACTIVO{% endif %}
                        </span>
                        <button class="btn btn-toggle {% if not dest.activo %}inactive{% endif %}"
                                onclick="toggleDestinatario('{{ dest.numero }}', {{ 'false' if dest.activo else 'true' }})">
                            {% if dest.activo %}Desactivar{% else %}Activar{% endif %}
                        </button>
                        <button class="btn btn-delete" onclick="eliminarDestinatario('{{ dest.numero }}')">Eliminar</button>
                    </div>
                </li>
                {% endfor %}
            </ul>

            <!-- Formulario agregar destinatario -->
            <div class="add-form">
                <h3 style="margin-bottom: 15px;">➕ Agregar Nuevo Destinatario</h3>

                <div style="margin-bottom: 20px;">
                    <label style="font-weight: 600; margin-bottom: 10px; display: block;">Seleccionar de contactos existentes:</label>
                    <div class="contactos-select">
                        {% for contacto in contactos %}
                        <div class="contacto-option" onclick="seleccionarContacto('{{ contacto.numero }}', '{{ contacto.nombre }}')">
                            <div class="contacto-nombre">{{ contacto.nombre }}</div>
                            <div class="contacto-numero">{{ contacto.numero }} ({{ contacto.total_mensajes }} mensajes)</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div style="text-align: center; margin: 20px 0;">
                    <strong>- O -</strong>
                </div>

                <div class="form-group">
                    <label>Número de Teléfono</label>
                    <input type="text" id="nuevo-numero" placeholder="51967717179">
                </div>
                <div class="form-group">
                    <label>Nombre</label>
                    <input type="text" id="nuevo-nombre" placeholder="Nombre del contacto">
                </div>
                <button class="btn btn-primary" onclick="agregarDestinatario()">Agregar Destinatario</button>
            </div>
        </div>

        <!-- Configuración Avanzada -->
        <div class="section">
            <h2>⚙️ Configuración Avanzada</h2>

            <div class="form-group">
                <label>Score Mínimo de Compatibilidad (%)</label>
                <input type="number" id="score-minimo" value="{{ config.configuracion.score_minimo }}" min="0" max="100">
                <small style="color: #666;">Solo se enviarán alertas de oportunidades con este score o superior</small>
            </div>

            <div class="form-group">
                <label>Máximo de Oportunidades por Alerta</label>
                <input type="number" id="max-oportunidades" value="{{ config.configuracion.max_oportunidades_por_alerta }}" min="1" max="20">
                <small style="color: #666;">Cantidad máxima de oportunidades a notificar en cada alerta</small>
            </div>

            <button class="btn btn-primary" onclick="guardarConfiguracion()">Guardar Configuración</button>
        </div>
    </div>

    <script>
        function toggleHorario(hora, activo) {
            fetch('/admin/alertas/horario/toggle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({hora: hora, activo: activo})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error al actualizar horario');
                }
            });
        }

        function eliminarHorario(hora) {
            if (!confirm('¿Eliminar este horario?')) return;

            fetch('/admin/alertas/horario/eliminar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({hora: hora})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error al eliminar horario');
                }
            });
        }

        function agregarHorario() {
            const hora = document.getElementById('nueva-hora').value;
            const descripcion = document.getElementById('nueva-hora-desc').value;

            if (!hora) {
                alert('Ingresa una hora');
                return;
            }

            fetch('/admin/alertas/horario/agregar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({hora: hora, descripcion: descripcion})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error al agregar horario (puede que ya exista)');
                }
            });
        }

        function toggleDestinatario(numero, activo) {
            fetch('/admin/alertas/destinatario/toggle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({numero: numero, activo: activo})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error al actualizar destinatario');
                }
            });
        }

        function eliminarDestinatario(numero) {
            if (!confirm('¿Eliminar este destinatario?')) return;

            fetch('/admin/alertas/destinatario/eliminar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({numero: numero})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error al eliminar destinatario');
                }
            });
        }

        function seleccionarContacto(numero, nombre) {
            document.getElementById('nuevo-numero').value = numero.split('@')[0];
            document.getElementById('nuevo-nombre').value = nombre;
        }

        function agregarDestinatario() {
            const numero = document.getElementById('nuevo-numero').value;
            const nombre = document.getElementById('nuevo-nombre').value;

            if (!numero) {
                alert('Ingresa un número');
                return;
            }

            fetch('/admin/alertas/destinatario/agregar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({numero: numero, nombre: nombre})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error al agregar destinatario (puede que ya exista)');
                }
            });
        }

        function guardarConfiguracion() {
            const scoreMinimo = parseInt(document.getElementById('score-minimo').value);
            const maxOportunidades = parseInt(document.getElementById('max-oportunidades').value);

            fetch('/admin/alertas/config/actualizar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    score_minimo: scoreMinimo,
                    max_oportunidades: maxOportunidades
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Configuración guardada');
                    location.reload();
                } else {
                    alert('Error al guardar configuración');
                }
            });
        }
    </script>
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