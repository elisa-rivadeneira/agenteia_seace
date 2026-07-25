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
    <title>Admin Login - SEACE Bot</title>
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
        <h1>🤖 SEACE Bot - Dashboard</h1>
        <div class="header-links">
            <a href="/admin/usuarios">👥 Usuarios</a>
            <a href="/admin/alertas">⏰ Alertas</a>
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
        <h1>👥 Gestión de Usuarios</h1>
        <div class="header-links">
            <a href="/admin">← Dashboard</a>
            <a href="/admin/alertas">⏰ Alertas</a>
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
                            <span class="badge {% if usuario.activo %}badge-active{% else %}badge-inactive{% endif %}">
                                {% if usuario.activo %}ACTIVO{% else %}INACTIVO{% endif %}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 12px;"
                                    onclick="toggleUsuario('{{ usuario.numero }}', {{ 'false' if usuario.activo else 'true' }})">
                                {% if usuario.activo %}Desactivar{% else %}Activar{% endif %}
                            </button>
                            <button class="btn btn-danger" style="padding: 5px 10px; font-size: 12px;"
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
    </script>
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
        <h1>⏰ Gestión de Alertas</h1>
        <div class="header-links">
            <a href="/admin">← Dashboard</a>
            <a href="/admin/usuarios">👥 Usuarios</a>
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
