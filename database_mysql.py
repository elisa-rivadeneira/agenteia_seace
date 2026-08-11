import mysql.connector
from mysql.connector import pooling, Error
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME', 'seace_monitor'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'pool_name': 'seace_pool',
    'pool_size': 5,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

print("="*80)
print("🔧 DATABASE_MYSQL.PY - Configuración MySQL")
print("="*80)
print(f"Host: {DB_CONFIG['host']}")
print(f"Port: {DB_CONFIG['port']}")
print(f"Database: {DB_CONFIG['database']}")
print(f"User: {DB_CONFIG['user']}")
print(f"Password: {'***' if DB_CONFIG['password'] else '(vacío)'}")
print("="*80)

connection_pool = None

def get_connection():
    global connection_pool
    if connection_pool is None:
        try:
            print(f"🔧 [MySQL] Intentando conectar a: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
            print(f"🔧 [MySQL] Usuario: {DB_CONFIG['user']}")
            connection_pool = pooling.MySQLConnectionPool(**DB_CONFIG)
            print(f"✅ [MySQL] Connection pool creado correctamente")
        except Exception as e:
            print(f"❌ [MySQL] Error al crear connection pool: {e}")
            raise
    return connection_pool.get_connection()

def inicializar_bd():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero VARCHAR(20) UNIQUE NOT NULL,
                nombre VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                activo BOOLEAN DEFAULT TRUE,
                palabras_clave_custom JSON,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_numero (numero),
                INDEX idx_activo (activo)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario_segmentos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                segmento VARCHAR(10) NOT NULL,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                UNIQUE KEY unique_usuario_segmento (usuario_id, segmento),
                INDEX idx_usuario_activo (usuario_id, activo)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_oportunidades (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                segmento VARCHAR(10) NOT NULL,
                nomenclatura VARCHAR(100) NOT NULL,
                fecha_visto TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                UNIQUE KEY unique_historial (usuario_id, segmento, nomenclatura),
                INDEX idx_usuario_segmento (usuario_id, segmento),
                INDEX idx_nomenclatura (nomenclatura)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario_configuracion (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                alertas_realtime_activas BOOLEAN DEFAULT TRUE,
                alertas_programadas_activas BOOLEAN DEFAULT FALSE,
                score_minimo INT DEFAULT 30,
                max_oportunidades_alerta INT DEFAULT 5,
                horarios_alertas JSON,
                dias_semana JSON,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                UNIQUE KEY unique_config (usuario_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tablas creadas correctamente")
        return True

    except Error as e:
        print(f"❌ Error al inicializar BD: {e}")
        return False

def agregar_usuario(numero: str, nombre: str, email: str = "", segmentos: List[str] = None) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usuarios (numero, nombre, email)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE nombre = %s, email = %s
        """, (numero, nombre, email, nombre, email))

        usuario_id = cursor.lastrowid
        if usuario_id == 0:
            cursor.execute("SELECT id FROM usuarios WHERE numero = %s", (numero,))
            usuario_id = cursor.fetchone()[0]

        if segmentos:
            for seg in segmentos:
                cursor.execute("""
                    INSERT INTO usuario_segmentos (usuario_id, segmento, activo)
                    VALUES (%s, %s, TRUE)
                    ON DUPLICATE KEY UPDATE activo = TRUE
                """, (usuario_id, seg))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Error as e:
        print(f"❌ Error al agregar usuario: {e}")
        return False

def obtener_usuarios(solo_activos: bool = True) -> List[Dict]:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM usuarios"
        if solo_activos:
            query += " WHERE activo = TRUE"

        cursor.execute(query)
        usuarios = cursor.fetchall()

        for usuario in usuarios:
            cursor.execute("""
                SELECT segmento FROM usuario_segmentos
                WHERE usuario_id = %s AND activo = TRUE
            """, (usuario['id'],))
            segmentos = [row['segmento'] for row in cursor.fetchall()]
            usuario['segmentos'] = segmentos

            if usuario.get('palabras_clave_custom'):
                usuario['palabras_clave_custom'] = json.loads(usuario['palabras_clave_custom'])

        cursor.close()
        conn.close()
        return usuarios

    except Error as e:
        print(f"❌ Error al obtener usuarios: {e}")
        return []

def configurar_segmentos_usuario(numero: str, segmentos: List[str]) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE numero = %s", (numero,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            conn.close()
            return False

        usuario_id = result[0]

        cursor.execute("UPDATE usuario_segmentos SET activo = FALSE WHERE usuario_id = %s", (usuario_id,))

        for seg in segmentos:
            cursor.execute("""
                INSERT INTO usuario_segmentos (usuario_id, segmento, activo)
                VALUES (%s, %s, TRUE)
                ON DUPLICATE KEY UPDATE activo = TRUE
            """, (usuario_id, seg))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Error as e:
        print(f"❌ Error al configurar segmentos: {e}")
        return False

def marcar_oportunidad_vista(usuario_id: int, segmento: str, nomenclatura: str) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT IGNORE INTO historial_oportunidades (usuario_id, segmento, nomenclatura)
            VALUES (%s, %s, %s)
        """, (usuario_id, segmento, nomenclatura))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Error as e:
        print(f"❌ Error al marcar oportunidad vista: {e}")
        return False

def obtener_oportunidades_vistas(usuario_id: int, segmento: str) -> List[str]:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT nomenclatura FROM historial_oportunidades
            WHERE usuario_id = %s AND segmento = %s
        """, (usuario_id, segmento))

        nomenclaturas = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        return nomenclaturas

    except Error as e:
        print(f"❌ Error al obtener oportunidades vistas: {e}")
        return []

def limpiar_historial_antiguo(dias: int = 90):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM historial_oportunidades
            WHERE fecha_visto < DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (dias,))

        rows_deleted = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        print(f"🗑️ Eliminadas {rows_deleted} oportunidades antiguas del historial")
        return True

    except Error as e:
        print(f"❌ Error al limpiar historial: {e}")
        return False

def obtener_configuracion_usuario(numero: str) -> Dict:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM usuarios WHERE numero = %s", (numero,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            conn.close()
            return None

        usuario_id = result['id']

        cursor.execute("""
            SELECT alertas_realtime_activas, alertas_programadas_activas,
                   score_minimo, max_oportunidades_alerta, horarios_alertas, dias_semana
            FROM usuario_configuracion
            WHERE usuario_id = %s
        """, (usuario_id,))

        config = cursor.fetchone()
        cursor.close()
        conn.close()

        if not config:
            return {
                'alertas_realtime_activas': True,
                'alertas_programadas_activas': False,
                'score_minimo': 30,
                'max_oportunidades_alerta': 5,
                'horarios_alertas': ['10:00', '19:00'],
                'dias_semana': ['L', 'M', 'X', 'J', 'V']
            }

        if config.get('horarios_alertas'):
            config['horarios_alertas'] = json.loads(config['horarios_alertas'])
        else:
            config['horarios_alertas'] = ['10:00', '19:00']

        if config.get('dias_semana'):
            config['dias_semana'] = json.loads(config['dias_semana'])
        else:
            config['dias_semana'] = ['L', 'M', 'X', 'J', 'V']

        return config

    except Error as e:
        print(f"❌ Error al obtener configuración: {e}")
        return None

def guardar_configuracion_usuario(numero: str, config: Dict) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE numero = %s", (numero,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            conn.close()
            return False

        usuario_id = result[0]

        horarios_json = json.dumps(config.get('horarios_alertas', ['10:00', '19:00']))
        dias_json = json.dumps(config.get('dias_semana', ['L', 'M', 'X', 'J', 'V']))

        cursor.execute("""
            INSERT INTO usuario_configuracion
            (usuario_id, alertas_realtime_activas, alertas_programadas_activas,
             score_minimo, max_oportunidades_alerta, horarios_alertas, dias_semana)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                alertas_realtime_activas = %s,
                alertas_programadas_activas = %s,
                score_minimo = %s,
                max_oportunidades_alerta = %s,
                horarios_alertas = %s,
                dias_semana = %s
        """, (usuario_id,
              config.get('alertas_realtime_activas', True),
              config.get('alertas_programadas_activas', False),
              config.get('score_minimo', 30),
              config.get('max_oportunidades_alerta', 5),
              horarios_json, dias_json,
              config.get('alertas_realtime_activas', True),
              config.get('alertas_programadas_activas', False),
              config.get('score_minimo', 30),
              config.get('max_oportunidades_alerta', 5),
              horarios_json, dias_json))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Error as e:
        print(f"❌ Error al guardar configuración: {e}")
        return False

def obtener_empresa_usuario(numero: str) -> Dict:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT palabras_clave_custom FROM usuarios WHERE numero = %s", (numero,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result or not result['palabras_clave_custom']:
            return None

        empresa = json.loads(result['palabras_clave_custom'])
        return empresa

    except Error as e:
        print(f"❌ Error al obtener empresa: {e}")
        return None

def guardar_empresa_usuario(numero: str, empresa: Dict) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        empresa_json = json.dumps(empresa, ensure_ascii=False)

        cursor.execute("""
            UPDATE usuarios SET palabras_clave_custom = %s WHERE numero = %s
        """, (empresa_json, numero))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Error as e:
        print(f"❌ Error al guardar empresa: {e}")
        return False

def obtener_usuario_por_numero(numero: str) -> Optional[Dict]:
    try:
        print(f"🔍 [MySQL] Buscando usuario con número: {numero}")
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE numero = %s", (numero,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario:
            print(f"✅ [MySQL] Usuario encontrado: ID={usuario['id']}, nombre={usuario['nombre']}")
        else:
            print(f"⚠️ [MySQL] Usuario NO encontrado para número: {numero}")

        return usuario
    except Error as e:
        print(f"❌ [MySQL] Error al obtener usuario: {e}")
        import traceback
        traceback.print_exc()
        return None

def obtener_segmentos_usuario(usuario_id: int) -> List[str]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT segmento FROM usuario_segmentos
            WHERE usuario_id = %s AND activo = TRUE
        """, (usuario_id,))
        segmentos = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return segmentos
    except Error as e:
        print(f"❌ Error al obtener segmentos: {e}")
        return []

def configurar_segmentos_usuario_por_id(usuario_id: int, segmentos: List[str]) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE usuario_segmentos SET activo = FALSE WHERE usuario_id = %s", (usuario_id,))

        for seg in segmentos:
            cursor.execute("""
                INSERT INTO usuario_segmentos (usuario_id, segmento, activo)
                VALUES (%s, %s, TRUE)
                ON DUPLICATE KEY UPDATE activo = TRUE
            """, (usuario_id, seg))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"❌ Error al configurar segmentos: {e}")
        return False

def obtener_empresa_usuario_por_id(usuario_id: int) -> Optional[Dict]:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT palabras_clave_custom FROM usuarios WHERE id = %s", (usuario_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result or not result['palabras_clave_custom']:
            return None

        empresa = json.loads(result['palabras_clave_custom'])
        return empresa
    except Error as e:
        print(f"❌ Error al obtener empresa: {e}")
        return None

def obtener_configuracion_usuario_por_id(usuario_id: int) -> Optional[Dict]:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT alertas_realtime_activas, alertas_programadas_activas,
                   score_minimo, max_oportunidades_alerta, horarios_alertas, dias_semana
            FROM usuario_configuracion
            WHERE usuario_id = %s
        """, (usuario_id,))

        config = cursor.fetchone()
        cursor.close()
        conn.close()

        if not config:
            return {
                'alertas_realtime_activas': True,
                'alertas_programadas_activas': False,
                'score_minimo': 30,
                'max_oportunidades_alerta': 5,
                'horarios_alertas': ['10:00', '19:00'],
                'dias_semana': ['L', 'M', 'X', 'J', 'V']
            }

        if config.get('horarios_alertas'):
            config['horarios_alertas'] = json.loads(config['horarios_alertas'])
        else:
            config['horarios_alertas'] = ['10:00', '19:00']

        if config.get('dias_semana'):
            config['dias_semana'] = json.loads(config['dias_semana'])
        else:
            config['dias_semana'] = ['L', 'M', 'X', 'J', 'V']

        return config
    except Error as e:
        print(f"❌ Error al obtener configuración: {e}")
        return None

def actualizar_empresa_usuario(usuario_id: int, nombre_empresa: str = None, palabras_clave: Dict = None) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if palabras_clave:
            palabras_json = json.dumps(palabras_clave, ensure_ascii=False)
            cursor.execute("""
                UPDATE usuarios SET palabras_clave_custom = %s WHERE id = %s
            """, (palabras_json, usuario_id))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"❌ Error al actualizar empresa: {e}")
        return False

def actualizar_configuracion_usuario(usuario_id: int, **kwargs) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        campos = []
        valores = []

        if 'alertas_realtime_activas' in kwargs:
            campos.append("alertas_realtime_activas = %s")
            valores.append(kwargs['alertas_realtime_activas'])

        if 'alertas_programadas_activas' in kwargs:
            campos.append("alertas_programadas_activas = %s")
            valores.append(kwargs['alertas_programadas_activas'])

        if 'score_minimo' in kwargs:
            campos.append("score_minimo = %s")
            valores.append(kwargs['score_minimo'])

        if 'max_oportunidades_alerta' in kwargs:
            campos.append("max_oportunidades_alerta = %s")
            valores.append(kwargs['max_oportunidades_alerta'])

        if 'horarios_alertas' in kwargs:
            campos.append("horarios_alertas = %s")
            valores.append(json.dumps(kwargs['horarios_alertas']))

        if 'dias_semana' in kwargs:
            campos.append("dias_semana = %s")
            valores.append(json.dumps(kwargs['dias_semana']))

        if not campos:
            return True

        valores.append(usuario_id)
        query = f"UPDATE usuario_configuracion SET {', '.join(campos)} WHERE usuario_id = %s"

        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"❌ Error al actualizar configuración: {e}")
        return False

# ===== CATÁLOGO DE SEGMENTOS =====

# Catálogo de segmentos SEACE
SEGMENTOS_SEACE = {
    "43": "Tecnologías de la Información",
    "80": "Servicios profesionales y consultoría",
    "81": "Investigación y desarrollo",
    "72": "Arquitectura e ingeniería",
    "42": "Equipos médicos y laboratorio",
    "44": "Equipos de oficina y computación",
    "45": "Equipos de telecomunicaciones",
    "76": "Servicios de limpieza",
    "77": "Servicios de seguridad",
    "78": "Servicios de mantenimiento",
    "86": "Educación y formación"
}

def obtener_nombre_segmento(codigo: str) -> str:
    """Obtiene el nombre de un segmento por su código"""
    return SEGMENTOS_SEACE.get(codigo, f"Segmento {codigo}")

if __name__ == "__main__":
    print("🔧 Inicializando base de datos...")
    inicializar_bd()
    print("\n📊 Usuarios actuales:")
    usuarios = obtener_usuarios()
    for u in usuarios:
        print(f"  - {u['nombre']} ({u['numero']}): Segmentos {u['segmentos']}")
