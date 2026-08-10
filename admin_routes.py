#!/usr/bin/env python3
"""
Rutas de administración para el sistema SEACE
Maneja usuarios y alertas
"""

from flask import Blueprint, request, jsonify, render_template_string, session, redirect
from functools import wraps
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

def require_auth(f):
    """Decorator para requerir autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated

# ===== AUTENTICACIÓN =====

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login del admin"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect('/admin')
        else:
            from admin_templates import LOGIN_HTML
            return render_template_string(LOGIN_HTML, error="Contraseña incorrecta")

    from admin_templates import LOGIN_HTML
    return render_template_string(LOGIN_HTML, error=None)

@admin_bp.route('/logout')
def logout():
    """Logout del admin"""
    session.pop('admin_authenticated', None)
    return redirect('/admin/login')

# ===== DASHBOARD PRINCIPAL =====

@admin_bp.route('/')
@require_auth
def dashboard():
    """Dashboard principal"""
    from database_mysql import obtener_usuarios
    from admin_templates import DASHBOARD_HTML

    usuarios = obtener_usuarios()

    stats = {
        'total_usuarios': len(usuarios),
        'usuarios_activos': len([u for u in usuarios if u.get('activo', True)]),
        'total_alertas': 0,
        'alertas_activas': 0
    }

    conversaciones = []

    return render_template_string(DASHBOARD_HTML, stats=stats, conversaciones=conversaciones)

# ===== GESTIÓN DE USUARIOS =====

@admin_bp.route('/usuarios')
@require_auth
def usuarios():
    """Página de gestión de usuarios"""
    from database_mysql import obtener_usuarios
    from admin_templates import USUARIOS_HTML

    usuarios = obtener_usuarios()

    return render_template_string(USUARIOS_HTML, usuarios=usuarios)

@admin_bp.route('/usuarios/agregar', methods=['POST'])
@require_auth
def agregar_usuario_route():
    """Agrega un nuevo usuario"""
    from database_mysql import agregar_usuario

    data = request.json
    numero = data.get('numero', '').strip()
    nombre = data.get('nombre', '').strip()
    email = data.get('email', '').strip()

    if not numero or not nombre:
        return jsonify({'success': False, 'error': 'Número y nombre son requeridos'})

    success = agregar_usuario(numero, nombre, email)
    return jsonify({'success': success})

@admin_bp.route('/usuarios/actualizar', methods=['POST'])
@require_auth
def actualizar_usuario_route():
    """Actualiza un usuario"""
    from database_mysql import agregar_usuario

    data = request.json
    numero = data.get('numero', '')
    datos = data.get('datos', {})

    success = agregar_usuario(numero, datos.get('nombre', ''), datos.get('email', ''))
    return jsonify({'success': success})

@admin_bp.route('/usuarios/eliminar', methods=['POST'])
@require_auth
def eliminar_usuario_route():
    """Elimina un usuario (desactiva)"""
    import mysql.connector
    from database_mysql import DB_CONFIG

    data = request.json
    numero = data.get('numero', '')

    try:
        conn = mysql.connector.connect(**{k: v for k, v in DB_CONFIG.items() if k not in ['pool_name', 'pool_size']})
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET activo = FALSE WHERE numero = %s", (numero,))
        conn.commit()
        cursor.close()
        conn.close()
        success = True
    except:
        success = False

    return jsonify({'success': success})

@admin_bp.route('/usuarios/importar', methods=['POST'])
@require_auth
def importar_usuarios_route():
    """Importa usuarios desde conversaciones"""
    from conversaciones_logger import obtener_todas_conversaciones
    from database_mysql import agregar_usuario

    conversaciones = obtener_todas_conversaciones()
    count = 0
    for numero, data in conversaciones.items():
        nombre = data.get('nombre', f'Usuario {numero}')
        if agregar_usuario(numero, nombre):
            count += 1

    return jsonify({'success': True, 'count': count})

@admin_bp.route('/usuarios/configurar-segmentos', methods=['POST'])
@require_auth
def configurar_segmentos_route():
    """Configura los segmentos de un usuario"""
    from database_mysql import configurar_segmentos_usuario

    data = request.json
    numero = data.get('numero', '')
    segmentos = data.get('segmentos', [])

    success = configurar_segmentos_usuario(numero, segmentos)
    return jsonify({'success': success})

@admin_bp.route('/usuarios/obtener-configuracion', methods=['POST'])
@require_auth
def obtener_configuracion_route():
    """Obtiene la configuración de un usuario"""
    from database_mysql import obtener_configuracion_usuario

    data = request.json
    numero = data.get('numero', '')

    config = obtener_configuracion_usuario(numero)
    if config is None:
        return jsonify({'success': False})

    return jsonify({'success': True, 'config': config})

@admin_bp.route('/usuarios/obtener-empresa', methods=['POST'])
@require_auth
def obtener_empresa_route():
    """Obtiene la información de empresa de un usuario"""
    from database_mysql import obtener_empresa_usuario

    data = request.json
    numero = data.get('numero', '')

    empresa = obtener_empresa_usuario(numero)
    return jsonify({'success': True if empresa else False, 'empresa': empresa})

@admin_bp.route('/usuarios/guardar-configuracion', methods=['POST'])
@require_auth
def guardar_configuracion_route():
    """Guarda la configuración completa de un usuario"""
    from database_mysql import configurar_segmentos_usuario, guardar_configuracion_usuario, guardar_empresa_usuario

    data = request.json
    numero = data.get('numero', '')
    segmentos = data.get('segmentos', [])
    empresa = data.get('empresa', {})

    config = {
        'alertas_realtime_activas': data.get('alertas_realtime_activas', True),
        'alertas_programadas_activas': data.get('alertas_programadas_activas', False),
        'score_minimo': data.get('score_minimo', 30),
        'max_oportunidades_alerta': data.get('max_oportunidades', 5),
        'horarios_alertas': data.get('horarios_alertas', ['10:00', '19:00']),
        'dias_semana': data.get('dias_semana', ['L', 'M', 'X', 'J', 'V'])
    }

    success1 = configurar_segmentos_usuario(numero, segmentos)
    success2 = guardar_configuracion_usuario(numero, config)
    success3 = guardar_empresa_usuario(numero, empresa)

    return jsonify({'success': success1 and success2 and success3})

# ===== GESTIÓN DE ALERTAS =====

@admin_bp.route('/alertas')
@require_auth
def alertas():
    """Página de gestión de alertas"""
    from database_manager import cargar_alertas, cargar_usuarios
    from admin_templates import ALERTAS_HTML
    import json

    alertas = cargar_alertas()
    usuarios = cargar_usuarios()

    # Convertir alertas a JSON para JavaScript
    alertas_json = json.dumps(alertas)

    return render_template_string(ALERTAS_HTML, alertas=alertas, usuarios=usuarios, alertas_json=alertas_json)

@admin_bp.route('/alertas/crear', methods=['POST'])
@require_auth
def crear_alerta_route():
    """Crea una nueva alerta"""
    from database_manager import crear_alerta

    data = request.json
    nombre = data.get('nombre', '')
    segmento = data.get('segmento', '43')
    horarios = data.get('horarios', [])
    dias_semana = data.get('dias_semana', [])
    usuarios = data.get('usuarios', [])
    score_minimo = data.get('score_minimo', 30)
    max_oportunidades = data.get('max_oportunidades', 5)

    if not nombre or not horarios or not usuarios:
        return jsonify({'success': False, 'error': 'Faltan datos requeridos'})

    success = crear_alerta(nombre, segmento, horarios, dias_semana, usuarios,
                          score_minimo, max_oportunidades)
    return jsonify({'success': success})

@admin_bp.route('/alertas/actualizar', methods=['POST'])
@require_auth
def actualizar_alerta_route():
    """Actualiza una alerta"""
    from database_manager import actualizar_alerta

    data = request.json
    alerta_id = data.get('id')
    datos = data.get('datos', {})

    success = actualizar_alerta(alerta_id, datos)
    return jsonify({'success': success})

@admin_bp.route('/alertas/eliminar', methods=['POST'])
@require_auth
def eliminar_alerta_route():
    """Elimina una alerta"""
    from database_manager import eliminar_alerta

    data = request.json
    alerta_id = data.get('id')

    success = eliminar_alerta(alerta_id)
    return jsonify({'success': success})

@admin_bp.route('/alertas/toggle', methods=['POST'])
@require_auth
def toggle_alerta_route():
    """Activa/desactiva una alerta"""
    from database_manager import activar_desactivar_alerta

    data = request.json
    alerta_id = data.get('id')
    activo = data.get('activo', False)

    success = activar_desactivar_alerta(alerta_id, activo)
    return jsonify({'success': success})
