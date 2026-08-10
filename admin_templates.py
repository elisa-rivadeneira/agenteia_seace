#!/usr/bin/env python3
"""
Templates HTML para el panel de administración
"""

# Estilos CSS compartidos
SHARED_CSS = """
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
    .header-links { display: flex; gap: 10px; }
    .header a {
        color: white;
        text-decoration: none;
        background: rgba(255,255,255,0.2);
        padding: 8px 15px;
        border-radius: 5px;
        transition: background 0.2s;
    }
    .header a:hover { background: rgba(255,255,255,0.3); }
    .container {
        max-width: 1200px;
        margin: 20px auto;
        padding: 20px;
    }
    .card {
        background: white;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .card h2 {
        color: #667eea;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f2f5;
    }
    .btn {
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
        text-decoration: none;
        display: inline-block;
    }
    .btn-primary { background: #667eea; color: white; }
    .btn-success { background: #28a745; color: white; }
    .btn-danger { background: #dc3545; color: white; }
    .btn-secondary { background: #6c757d; color: white; }
    .btn:hover { opacity: 0.8; transform: translateY(-2px); }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }
    th, td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #e1e4e8;
    }
    th {
        background: #f8f9fa;
        font-weight: 600;
        color: #333;
    }
    tr:hover { background: #f8f9fa; }
    .badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
    }
    .badge-active { background: #d4edda; color: #155724; }
    .badge-inactive { background: #f8d7da; color: #721c24; }
    .form-group {
        margin-bottom: 15px;
    }
    .form-group label {
        display: block;
        margin-bottom: 5px;
        font-weight: 600;
        color: #333;
    }
    .form-group input, .form-group select, .form-group textarea {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-size: 14px;
    }
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 1000;
    }
    .modal-content {
        background: white;
        max-width: 600px;
        margin: 50px auto;
        padding: 30px;
        border-radius: 10px;
        max-height: 90vh;
        overflow-y: auto;
    }
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .close {
        font-size: 28px;
        cursor: pointer;
        color: #666;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
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
    .checkbox-group {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
    }
    .checkbox-item {
        display: flex;
        align-items: center;
        gap: 5px;
    }
</style>
"""

# Template de Login
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Adminn Loginnnnnn - SEACE Bot</title>
    <meta charset="UTF-8">
    """ + SHARED_CSS + """
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            width: 350px;
        }
        .login-box h2 { text-align: center; color: #333; margin-bottom: 20px; }
        .login-box input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        .login-box button {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        .login-box button:hover { background: #5568d3; }
        .error {
            color: #dc3545;
            text-align: center;
            margin-top: 10px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🤖 SEACE Bot Admin</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña" required autofocus>
            <button type="submit">Ingresar</button>
        </form>
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

# Template Dashboard Principal
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - SEACE Bot</title>
    <meta charset="UTF-8">
    """ + SHARED_CSS + """
</head>
<body>
    <div class="header">
        <h1><a href="/admin" style="color: white; text-decoration: none;">🤖 SEACE Bot - Gestión de Usuarios</a></h1>
        <div class="header-links">
            <a href="/admin/usuarios">⚙️ Configuración</a>
            <a href="/admin/logout">Cerrar sesión</a>
        </div>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Total Usuarios</div>
                <div class="value">{{ stats.total_usuarios }}</div>
            </div>
            <div class="stat-card">
                <div class="label">Usuarios Activos</div>
                <div class="value">{{ stats.usuarios_activos }}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Alertas</div>
                <div class="value">{{ stats.total_alertas }}</div>
            </div>
            <div class="stat-card">
                <div class="label">Alertas Activas</div>
                <div class="value">{{ stats.alertas_activas }}</div>
            </div>
        </div>

        <div class="card">
            <h2>📊 Conversaciones Recientes</h2>
            <table>
                <thead>
                    <tr>
                        <th>Usuario</th>
                        <th>Número</th>
                        <th>Mensajes</th>
                        <th>Última Interacción</th>
                    </tr>
                </thead>
                <tbody>
                    {% for numero, conv in conversaciones[:10] %}
                    <tr>
                        <td>{{ conv.nombre or 'Sin nombre' }}</td>
                        <td>{{ numero.split('@')[0] }}</td>
                        <td>{{ conv.total_mensajes }}</td>
                        <td>{{ conv.ultima_interaccion[:19] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# Template Gestión de Usuarios
USUARIOS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Gestión de Usuarios - SEACE Bot</title>
    <meta charset="UTF-8">
    """ + SHARED_CSS + """
</head>
<body>
    <div class="header">
        <h1><a href="/admin" style="color: white; text-decoration: none;">🤖 SEACE Bot</a> - 👥 Usuarios</h1>
        <div class="header-links">
            <a href="/admin">← Dashboard</a>
            <a href="/admin/logout">Cerrar sesión</a>
        </div>
    </div>

    <div class="container">
        <div class="card">
            <h2>👥 Usuarios Registrados</h2>
            <div style="margin-bottom: 20px;">
                <button class="btn btn-primary" onclick="mostrarModalAgregar()">➕ Agregar Usuario</button>
                <button class="btn btn-success" onclick="importarUsuarios()">📥 Importar desde Conversaciones</button>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Número</th>
                        <th>Email</th>
                        <th>Segmentos</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for usuario in usuarios %}
                    <tr>
                        <td>{{ usuario.id }}</td>
                        <td>{{ usuario.nombre }}</td>
                        <td>{{ usuario.numero }}</td>
                        <td>{{ usuario.email or '-' }}</td>
                        <td>
                            {% if usuario.segmentos %}
                                <span class="badge badge-active">{{ usuario.segmentos|length }} configurados</span>
                            {% else %}
                                <span class="badge badge-inactive">Sin configurar</span>
                            {% endif %}
                        </td>
                        <td>
                            <span class="badge {% if usuario.activo %}badge-active{% else %}badge-inactive{% endif %}">
                                {% if usuario.activo %}ACTIVO{% else %}INACTIVO{% endif %}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-primary" style="padding: 5px 10px; font-size: 12px; margin: 2px;"
                                    onclick='abrirConfiguracion("{{ usuario.numero }}", "{{ usuario.nombre }}", {{ (usuario.segmentos or []) | tojson }})'>
                                ⚙️ Configuración
                            </button>
                            <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 12px; margin: 2px;"
                                    onclick="toggleUsuario('{{ usuario.numero }}', {{ 'false' if usuario.activo else 'true' }})">
                                {% if usuario.activo %}Desactivar{% else %}Activar{% endif %}
                            </button>
                            <button class="btn btn-danger" style="padding: 5px 10px; font-size: 12px; margin: 2px;"
                                    onclick="eliminarUsuario('{{ usuario.numero }}')">
                                Eliminar
                            </button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Modal Agregar Usuario -->
    <div id="modalAgregar" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>➕ Agregar Nuevo Usuario</h2>
                <span class="close" onclick="cerrarModal()">&times;</span>
            </div>
            <form id="formAgregar">
                <div class="form-group">
                    <label>Nombre *</label>
                    <input type="text" id="nombre" required>
                </div>
                <div class="form-group">
                    <label>Número de Teléfono *</label>
                    <input type="text" id="numero" placeholder="51967717179" required>
                </div>
                <div class="form-group">
                    <label>Email (opcional)</label>
                    <input type="email" id="email">
                </div>
                <button type="submit" class="btn btn-primary">Guardar</button>
            </form>
        </div>
    </div>

    <script>
        function mostrarModalAgregar() {
            document.getElementById('modalAgregar').style.display = 'block';
        }

        function cerrarModal() {
            document.getElementById('modalAgregar').style.display = 'none';
            document.getElementById('formAgregar').reset();
        }

        document.getElementById('formAgregar').onsubmit = function(e) {
            e.preventDefault();
            const nombre = document.getElementById('nombre').value;
            const numero = document.getElementById('numero').value;
            const email = document.getElementById('email').value;

            fetch('/admin/usuarios/agregar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({nombre, numero, email})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Usuario agregado');
                    location.reload();
                } else {
                    alert('❌ Error: ' + (data.error || 'No se pudo agregar'));
                }
            });
        };

        function toggleUsuario(numero, activo) {
            fetch('/admin/usuarios/actualizar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({numero, datos: {activo}})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) location.reload();
                else alert('Error al actualizar');
            });
        }

        function eliminarUsuario(numero) {
            if (!confirm('¿Eliminar este usuario?')) return;

            fetch('/admin/usuarios/eliminar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({numero})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) location.reload();
                else alert('Error al eliminar');
            });
        }

        function importarUsuarios() {
            if (!confirm('¿Importar usuarios desde conversaciones?')) return;

            fetch('/admin/usuarios/importar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(r => r.json())
            .then(data => {
                alert(`✅ ${data.count} usuarios importados`);
                location.reload();
            });
        }

        function abrirConfiguracion(numero, nombre, segmentosActuales) {
            const modal = document.getElementById('modalConfiguracion');
            document.getElementById('nombreUsuarioConfig').textContent = nombre;
            document.getElementById('numeroUsuarioConfig').value = numero;

            fetch('/static/segmentos_seace.json')
            .then(r => r.json())
            .then(segmentosDisponibles => {
                mostrarCheckboxesSegmentos(segmentosDisponibles, segmentosActuales);
            });

            Promise.all([
                fetch('/admin/usuarios/obtener-configuracion', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({numero})
                }).then(r => r.json()),

                fetch('/admin/usuarios/obtener-empresa', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({numero})
                }).then(r => r.json())
            ]).then(([configData, empresaData]) => {
                if (configData.success) {
                    document.getElementById('alertas_realtime_activas').checked = configData.config.alertas_realtime_activas;
                    document.getElementById('alertas_programadas_activas').checked = configData.config.alertas_programadas_activas;
                    document.getElementById('score_minimo').value = configData.config.score_minimo;
                    document.getElementById('max_oportunidades').value = configData.config.max_oportunidades_alerta;

                    const horarios = configData.config.horarios_alertas || [];
                    document.querySelectorAll('.horario-check').forEach(checkbox => {
                        checkbox.checked = horarios.includes(checkbox.value);
                    });

                    const dias = configData.config.dias_semana || [];
                    document.querySelectorAll('.dia-check').forEach(checkbox => {
                        checkbox.checked = dias.includes(checkbox.value);
                    });
                }

                if (empresaData.success && empresaData.empresa) {
                    document.getElementById('empresa_nombre').value = empresaData.empresa.nombre || '';
                    document.getElementById('empresa_ruc').value = empresaData.empresa.ruc || '';
                    document.getElementById('palabras_positivas').value = (empresaData.empresa.palabras_positivas || []).join(', ');
                    document.getElementById('palabras_negativas').value = (empresaData.empresa.palabras_negativas || []).join(', ');
                }
            });

            modal.style.display = 'block';
        }

        function cambiarTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            document.getElementById('tab-' + tab).classList.add('active');
            document.getElementById('content-' + tab).classList.add('active');
        }

        function mostrarCheckboxesSegmentos(segmentosDisponibles, segmentosActuales) {

            const container = document.getElementById('checkboxesSegmentos');
            container.innerHTML = '';

            segmentosDisponibles.forEach(seg => {
                const div = document.createElement('div');
                div.style.marginBottom = '10px';
                div.style.padding = '8px';
                div.style.borderBottom = '1px solid #eee';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `seg_${seg.codigo}`;
                checkbox.value = seg.codigo;
                checkbox.checked = segmentosActuales.includes(seg.codigo);

                const label = document.createElement('label');
                label.htmlFor = `seg_${seg.codigo}`;
                label.innerHTML = `<strong>${seg.codigo}</strong> - ${seg.nombre} <span style="color: #666; font-size: 12px;">(${seg.tipo})</span>`;
                label.style.marginLeft = '8px';
                label.style.cursor = 'pointer';

                div.appendChild(checkbox);
                div.appendChild(label);
                container.appendChild(div);
            });
        }

        function cerrarModalConfig() {
            document.getElementById('modalConfiguracion').style.display = 'none';
        }

        function guardarConfiguracion() {
            const numero = document.getElementById('numeroUsuarioConfig').value;
            const checkboxes = document.querySelectorAll('#checkboxesSegmentos input[type=checkbox]:checked');
            const segmentos = Array.from(checkboxes).map(cb => cb.value);

            const alertas_realtime_activas = document.getElementById('alertas_realtime_activas').checked;
            const alertas_programadas_activas = document.getElementById('alertas_programadas_activas').checked;
            const score_minimo = parseInt(document.getElementById('score_minimo').value);
            const max_oportunidades = parseInt(document.getElementById('max_oportunidades').value);

            const horarios_checks = document.querySelectorAll('.horario-check:checked');
            const horarios_alertas = Array.from(horarios_checks).map(cb => cb.value);

            const dias_checks = document.querySelectorAll('.dia-check:checked');
            const dias_semana = Array.from(dias_checks).map(cb => cb.value);

            const palabras_positivas_text = document.getElementById('palabras_positivas').value;
            const palabras_negativas_text = document.getElementById('palabras_negativas').value;

            const palabras_positivas = palabras_positivas_text
                .split(',')
                .map(p => p.trim())
                .filter(p => p.length > 0);

            const palabras_negativas = palabras_negativas_text
                .split(',')
                .map(p => p.trim())
                .filter(p => p.length > 0);

            const empresa = {
                nombre: document.getElementById('empresa_nombre').value,
                ruc: document.getElementById('empresa_ruc').value,
                palabras_positivas,
                palabras_negativas
            };

            fetch('/admin/usuarios/guardar-configuracion', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    numero,
                    segmentos,
                    alertas_realtime_activas,
                    alertas_programadas_activas,
                    score_minimo,
                    max_oportunidades,
                    horarios_alertas,
                    dias_semana,
                    empresa
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Configuración guardada correctamente');
                    location.reload();
                } else {
                    alert('❌ Error al guardar configuración');
                }
            });
        }
    </script>

    <!-- Modal Configuración de Usuario -->
    <div id="modalConfiguracion" class="modal">
        <div class="modal-content" style="max-width: 700px;">
            <div class="modal-header">
                <h2>⚙️ Configuración - <span id="nombreUsuarioConfig"></span></h2>
                <span class="close" onclick="cerrarModalConfig()">&times;</span>
            </div>
            <input type="hidden" id="numeroUsuarioConfig">

            <!-- Pestañas -->
            <div style="display: flex; border-bottom: 2px solid #667eea; margin-bottom: 20px;">
                <button class="tab-btn active" onclick="cambiarTab('segmentos')" id="tab-segmentos">
                    📊 Segmentos
                </button>
                <button class="tab-btn" onclick="cambiarTab('alertas')" id="tab-alertas">
                    🔔 Alertas
                </button>
                <button class="tab-btn" onclick="cambiarTab('empresa')" id="tab-empresa">
                    🏢 Empresa
                </button>
            </div>

            <!-- Contenido Pestañas -->
            <div id="content-segmentos" class="tab-content active">
                <p style="color: #666; margin-bottom: 15px;">Selecciona los segmentos SEACE que deseas monitorear:</p>
                <div id="checkboxesSegmentos" style="max-height: 400px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                </div>
            </div>

            <div id="content-alertas" class="tab-content">
                <!-- Alertas en Tiempo Real -->
                <div style="border: 2px solid #667eea; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0; color: #667eea;">⚡ Alertas en Tiempo Real</h3>
                    <div class="form-group">
                        <label style="display: flex; align-items: center; margin-bottom: 10px;">
                            <input type="checkbox" id="alertas_realtime_activas" style="margin-right: 10px; width: 20px; height: 20px;">
                            <span style="font-weight: bold;">Activar alertas instantáneas</span>
                        </label>
                        <p style="color: #666; font-size: 13px; margin-left: 30px;">
                            Recibirás una notificación inmediata cuando aparezca una nueva convocatoria en tus segmentos.
                        </p>
                    </div>
                </div>

                <!-- Alertas Programadas -->
                <div style="border: 2px solid #f59e0b; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0; color: #f59e0b;">📅 Alertas Programadas</h3>
                    <div class="form-group">
                        <label style="display: flex; align-items: center; margin-bottom: 10px;">
                            <input type="checkbox" id="alertas_programadas_activas" style="margin-right: 10px; width: 20px; height: 20px;">
                            <span style="font-weight: bold;">Activar alertas diarias</span>
                        </label>
                        <p style="color: #666; font-size: 13px; margin-left: 30px;">
                            Recibirás un resumen de oportunidades en horarios específicos.
                        </p>
                    </div>

                    <div class="form-group" id="horarios_container">
                        <label style="font-weight: bold;">Horarios de envío</label>
                        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="horario-check" value="10:00" style="margin-right: 5px;"> 10:00 AM
                            </label>
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="horario-check" value="19:00" style="margin-right: 5px;"> 7:00 PM
                            </label>
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="horario-check" value="12:00" style="margin-right: 5px;"> 12:00 PM
                            </label>
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="horario-check" value="15:00" style="margin-right: 5px;"> 3:00 PM
                            </label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label style="font-weight: bold;">Días de la semana</label>
                        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="dia-check" value="L" style="margin-right: 5px;"> Lunes
                            </label>
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="dia-check" value="M" style="margin-right: 5px;"> Martes
                            </label>
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="dia-check" value="X" style="margin-right: 5px;"> Miércoles
                            </label>
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="dia-check" value="J" style="margin-right: 5px;"> Jueves
                            </label>
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="dia-check" value="V" style="margin-right: 5px;"> Viernes
                            </label>
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="dia-check" value="S" style="margin-right: 5px;"> Sábado
                            </label>
                            <label style="display: flex; align-items: center;">
                                <input type="checkbox" class="dia-check" value="D" style="margin-right: 5px;"> Domingo
                            </label>
                        </div>
                    </div>
                </div>

                <!-- Configuración Común -->
                <div style="border: 2px solid #10b981; border-radius: 8px; padding: 15px;">
                    <h3 style="margin-top: 0; color: #10b981;">⚙️ Configuración General</h3>
                    <div class="form-group">
                        <label>Score mínimo de compatibilidad (%)</label>
                        <input type="number" id="score_minimo" min="0" max="100" value="30" style="width: 100px;">
                        <p style="color: #666; font-size: 13px; margin-top: 5px;">
                            Solo recibirás alertas de oportunidades con score igual o mayor a este valor.
                        </p>
                    </div>

                    <div class="form-group">
                        <label>Máximo de oportunidades por alerta</label>
                        <input type="number" id="max_oportunidades" min="1" max="20" value="5" style="width: 100px;">
                        <p style="color: #666; font-size: 13px; margin-top: 5px;">
                            Para alertas programadas: cantidad de oportunidades a incluir (Top N).
                        </p>
                    </div>
                </div>
            </div>

            <div id="content-empresa" class="tab-content">
                <h3 style="color: #667eea; margin-top: 0;">📝 Información de la Empresa</h3>
                <div class="form-group">
                    <label>Nombre de la empresa</label>
                    <input type="text" id="empresa_nombre" style="width: 100%;" placeholder="Ej: SOLUCIONES TECNOLÓGICAS S.A.C">
                </div>

                <div class="form-group">
                    <label>RUC</label>
                    <input type="text" id="empresa_ruc" style="width: 200px;" placeholder="20512345678" maxlength="11">
                </div>

                <h3 style="color: #10b981; margin-top: 30px;">✅ Palabras Clave Positivas (+5 pts c/u)</h3>
                <p style="color: #666; font-size: 13px;">Separa las palabras con comas. Estas palabras aumentan el score de compatibilidad.</p>
                <textarea id="palabras_positivas" rows="6" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" placeholder="software, sistema, desarrollo, servidor, tecnología, base de datos..."></textarea>

                <h3 style="color: #ef4444; margin-top: 20px;">❌ Palabras Clave Negativas (-10 pts c/u)</h3>
                <p style="color: #666; font-size: 13px;">Separa las palabras con comas. Estas palabras reducen el score de compatibilidad.</p>
                <textarea id="palabras_negativas" rows="6" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" placeholder="construcción, obra civil, medicamentos, vehículos, mobiliario..."></textarea>

                <div style="background: #f3f4f6; padding: 15px; border-radius: 5px; margin-top: 20px;">
                    <p style="margin: 0; font-size: 13px; color: #666;">
                        <strong>💡 Tip:</strong> Las palabras clave determinan qué tan relevante es una oportunidad para tu empresa.
                        Mientras más palabras positivas encuentre en la convocatoria, mayor será el score de compatibilidad.
                    </p>
                </div>
            </div>

            <button class="btn btn-primary" onclick="guardarConfiguracion()" style="margin-top: 20px;">💾 Guardar Configuración</button>
        </div>
    </div>

    <style>
        .tab-btn {
            flex: 1;
            padding: 12px 20px;
            background: #f5f5f5;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
        }
        .tab-btn:hover {
            background: #e0e0e0;
        }
        .tab-btn.active {
            background: #667eea;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</body>
</html>
"""

# Template Gestión de Alertas
ALERTAS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Gestión de Alertas - SEACE Bot</title>
    <meta charset="UTF-8">
    """ + SHARED_CSS + """
</head>
<body>
    <div class="header">
        <h1><a href="/admin" style="color: white; text-decoration: none;">🤖 SEACE Bot</a> - ⏰ Alertas</h1>
        <div class="header-links">
            <a href="/admin">← Dashboard</a>
            <a href="/admin/usuarios">⚙️ Configuración</a>
            <a href="/admin/logout">Cerrar sesión</a>
        </div>
    </div>

    <div class="container">
        <div class="card">
            <h2>⏰ Alertas Configuradas</h2>
            <div style="margin-bottom: 20px;">
                <button class="btn btn-primary" onclick="mostrarModalCrear()">➕ Crear Nueva Alerta</button>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Segmento</th>
                        <th>Horarios</th>
                        <th>Días</th>
                        <th>Usuarios</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for alerta in alertas %}
                    <tr>
                        <td>{{ alerta.id }}</td>
                        <td>{{ alerta.nombre }}</td>
                        <td>{{ alerta.segmento }}</td>
                        <td>{{ ', '.join(alerta.horarios) }}</td>
                        <td>
                            {% set dias = ['L', 'M', 'X', 'J', 'V', 'S', 'D'] %}
                            {% for d in alerta.dias_semana %}{{ dias[d] }}{% endfor %}
                        </td>
                        <td>{{ alerta.usuarios|length }} usuarios</td>
                        <td>
                            <span class="badge {% if alerta.activo %}badge-active{% else %}badge-inactive{% endif %}">
                                {% if alerta.activo %}ACTIVA{% else %}INACTIVA{% endif %}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 12px;"
                                    onclick="toggleAlerta({{ alerta.id }}, {{ 'false' if alerta.activo else 'true' }})">
                                {% if alerta.activo %}Desactivar{% else %}Activar{% endif %}
                            </button>
                            <button class="btn btn-primary" style="padding: 5px 10px; font-size: 12px;"
                                    onclick="editarAlerta({{ alerta.id }})">
                                Editar
                            </button>
                            <button class="btn btn-danger" style="padding: 5px 10px; font-size: 12px;"
                                    onclick="eliminarAlerta({{ alerta.id }})">
                                Eliminar
                            </button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Modal Crear/Editar Alerta -->
    <div id="modalAlerta" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitulo">➕ Crear Nueva Alerta</h2>
                <span class="close" onclick="cerrarModal()">&times;</span>
            </div>
            <form id="formAlerta">
                <input type="hidden" id="alertaId">

                <div class="form-group">
                    <label>Nombre de la Alerta *</label>
                    <input type="text" id="alertaNombre" placeholder="Ej: Alerta Principal TI" required>
                </div>

                <div class="form-group">
                    <label>Segmento SEACE *</label>
                    <select id="alertaSegmento" required>
                        <option value="43">43 - Tecnologías de la Información</option>
                        <option value="44">44 - Otro segmento</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Horarios (selecciona uno o más) *</label>
                    <div id="horariosContainer" style="margin-top: 10px;">
                        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                            <input type="time" id="nuevoHorario" style="flex: 1;">
                            <button type="button" class="btn btn-success" onclick="agregarHorario()">Agregar</button>
                        </div>
                        <div id="horariosLista" style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                            <!-- Los horarios se agregarán aquí -->
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>Días de la Semana *</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="dia0" value="0">
                            <label for="dia0">Lunes</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="dia1" value="1">
                            <label for="dia1">Martes</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="dia2" value="2">
                            <label for="dia2">Miércoles</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="dia3" value="3">
                            <label for="dia3">Jueves</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="dia4" value="4">
                            <label for="dia4">Viernes</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="dia5" value="5">
                            <label for="dia5">Sábado</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="dia6" value="6">
                            <label for="dia6">Domingo</label>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>Usuarios que recibirán alertas *</label>
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <input type="text" id="nuevoUsuarioNombre" placeholder="Nombre del usuario" style="flex: 1;">
                        <input type="text" id="nuevoUsuarioNumero" placeholder="+51912345678" style="flex: 1;">
                        <button type="button" class="btn btn-secondary" onclick="agregarUsuarioManual()" style="padding: 8px 15px;">
                            ➕ Agregar
                        </button>
                    </div>
                    <select id="alertaUsuarios" multiple style="height: 150px;">
                        {% for usuario in usuarios %}
                        <option value="{{ usuario.numero }}">{{ usuario.nombre }} ({{ usuario.numero }})</option>
                        {% endfor %}
                    </select>
                    <small style="color: #666;">Mantén Ctrl/Cmd presionado para seleccionar múltiples usuarios</small>
                </div>

                <div class="form-group">
                    <label>Score Mínimo de Compatibilidad (%)</label>
                    <input type="number" id="scoreMinimo" value="30" min="0" max="100">
                </div>

                <div class="form-group">
                    <label>Máximo de Oportunidades por Alerta</label>
                    <input type="number" id="maxOportunidades" value="5" min="1" max="20">
                </div>

                <button type="submit" class="btn btn-primary">Guardar Alerta</button>
            </form>
        </div>
    </div>

    <script>
        let horariosSeleccionados = [];
        const alertasData = {{ alertas_json|safe }};

        function mostrarModalCrear() {
            document.getElementById('modalTitulo').textContent = '➕ Crear Nueva Alerta';
            document.getElementById('formAlerta').reset();
            document.getElementById('alertaId').value = '';
            horariosSeleccionados = [];

            // Limpiar días seleccionados
            for (let i = 0; i < 7; i++) {
                document.getElementById(`dia${i}`).checked = false;
            }

            // Limpiar usuarios seleccionados
            const usuariosSelect = document.getElementById('alertaUsuarios');
            for (let option of usuariosSelect.options) {
                option.selected = false;
            }

            actualizarListaHorarios();
            document.getElementById('modalAlerta').style.display = 'block';
        }

        function cerrarModal() {
            document.getElementById('modalAlerta').style.display = 'none';
        }

        function agregarHorario() {
            const horario = document.getElementById('nuevoHorario').value;
            if (horario && !horariosSeleccionados.includes(horario)) {
                horariosSeleccionados.push(horario);
                actualizarListaHorarios();
                document.getElementById('nuevoHorario').value = '';
            }
        }

        function eliminarHorario(horario) {
            horariosSeleccionados = horariosSeleccionados.filter(h => h !== horario);
            actualizarListaHorarios();
        }

        function actualizarListaHorarios() {
            const lista = document.getElementById('horariosLista');
            lista.innerHTML = horariosSeleccionados.map(h => `
                <div style="background: #667eea; color: white; padding: 5px 10px; border-radius: 5px; display: flex; align-items: center; gap: 5px;">
                    <span>${h}</span>
                    <span onclick="eliminarHorario('${h}')" style="cursor: pointer; font-weight: bold;">&times;</span>
                </div>
            `).join('');
        }

        async function agregarUsuarioManual() {
            const nombre = document.getElementById('nuevoUsuarioNombre').value.trim();
            const numero = document.getElementById('nuevoUsuarioNumero').value.trim();

            if (!nombre || !numero) {
                alert('Por favor completa nombre y número');
                return;
            }

            // Validar formato de número (debe incluir código de país)
            if (!numero.match(/^\+?\d{10,15}$/)) {
                alert('Número inválido. Formato: +51912345678');
                return;
            }

            // Formatear número al formato WhatsApp (con @s.whatsapp.net si no lo tiene)
            let numeroFormateado = numero.replace(/[^\d]/g, '');
            if (!numero.includes('@')) {
                numeroFormateado = numeroFormateado + '@s.whatsapp.net';
            }

            // Agregar al select
            const select = document.getElementById('alertaUsuarios');

            // Verificar si ya existe
            for (let option of select.options) {
                if (option.value === numeroFormateado) {
                    alert('Este usuario ya está en la lista');
                    return;
                }
            }

            // Guardar en el servidor
            try {
                const response = await fetch('/admin/usuarios/agregar-manual', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        numero: numeroFormateado,
                        nombre: nombre
                    })
                });

                const result = await response.json();

                if (!result.success) {
                    alert('Error guardando usuario en el servidor');
                    return;
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error de conexión al guardar usuario');
                return;
            }

            // Crear nueva opción en el select
            const option = document.createElement('option');
            option.value = numeroFormateado;
            option.text = `${nombre} (${numero})`;
            option.selected = true;
            select.add(option);

            // Limpiar inputs
            document.getElementById('nuevoUsuarioNombre').value = '';
            document.getElementById('nuevoUsuarioNumero').value = '';

            alert(`✅ Usuario agregado: ${nombre}`);
        }

        document.getElementById('formAlerta').onsubmit = function(e) {
            e.preventDefault();

            const nombre = document.getElementById('alertaNombre').value;
            const segmento = document.getElementById('alertaSegmento').value;
            const horarios = horariosSeleccionados;

            const diasSemana = [];
            for (let i = 0; i < 7; i++) {
                if (document.getElementById(`dia${i}`).checked) {
                    diasSemana.push(i);
                }
            }

            const usuariosSelect = document.getElementById('alertaUsuarios');
            const usuarios = Array.from(usuariosSelect.selectedOptions).map(opt => opt.value);

            const scoreMinimo = parseInt(document.getElementById('scoreMinimo').value);
            const maxOportunidades = parseInt(document.getElementById('maxOportunidades').value);

            if (horarios.length === 0) {
                alert('Debes agregar al menos un horario');
                return;
            }

            if (diasSemana.length === 0) {
                alert('Debes seleccionar al menos un día de la semana');
                return;
            }

            if (usuarios.length === 0) {
                alert('Debes seleccionar al menos un usuario');
                return;
            }

            const alertaId = document.getElementById('alertaId').value;

            if (alertaId) {
                // Editar alerta existente
                fetch('/admin/alertas/actualizar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        id: parseInt(alertaId),
                        datos: {
                            nombre, segmento, horarios, dias_semana: diasSemana, usuarios,
                            configuracion: { score_minimo: scoreMinimo, max_oportunidades: maxOportunidades }
                        }
                    })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Alerta actualizada');
                        location.reload();
                    } else {
                        alert('❌ Error al actualizar');
                    }
                });
            } else {
                // Crear nueva alerta
                fetch('/admin/alertas/crear', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        nombre, segmento, horarios, dias_semana: diasSemana, usuarios,
                        score_minimo: scoreMinimo, max_oportunidades: maxOportunidades
                    })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Alerta creada');
                        location.reload();
                    } else {
                        alert('❌ Error: ' + (data.error || 'No se pudo crear'));
                    }
                });
            }
        };

        function toggleAlerta(id, activo) {
            fetch('/admin/alertas/toggle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id, activo})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) location.reload();
                else alert('Error al actualizar');
            });
        }

        function eliminarAlerta(id) {
            if (!confirm('¿Eliminar esta alerta?')) return;

            fetch('/admin/alertas/eliminar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) location.reload();
                else alert('Error al eliminar');
            });
        }

        function editarAlerta(id) {
            // Buscar la alerta en los datos
            const alerta = alertasData.find(a => a.id === id);
            if (!alerta) {
                alert('Alerta no encontrada');
                return;
            }

            // Cambiar título del modal
            document.getElementById('modalTitulo').textContent = '✏️ Editar Alerta';

            // Llenar el formulario con los datos de la alerta
            document.getElementById('alertaId').value = alerta.id;
            document.getElementById('alertaNombre').value = alerta.nombre;
            document.getElementById('alertaSegmento').value = alerta.segmento;

            // Cargar horarios
            horariosSeleccionados = [...alerta.horarios];
            actualizarListaHorarios();

            // Marcar días de la semana
            for (let i = 0; i < 7; i++) {
                document.getElementById(`dia${i}`).checked = alerta.dias_semana.includes(i);
            }

            // Seleccionar usuarios
            const usuariosSelect = document.getElementById('alertaUsuarios');
            for (let option of usuariosSelect.options) {
                option.selected = alerta.usuarios.includes(option.value);
            }

            // Configuración
            document.getElementById('scoreMinimo').value = alerta.configuracion.score_minimo;
            document.getElementById('maxOportunidades').value = alerta.configuracion.max_oportunidades;

            // Mostrar modal
            document.getElementById('modalAlerta').style.display = 'block';
        }
    </script>
</body>
</html>
"""
