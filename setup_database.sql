-- Script SQL para inicializar base de datos SEACE Monitor
-- Ejecutar con: mysql -u root -p123456 < setup_database.sql

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS seace_monitor
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE seace_monitor;

-- Tabla de usuarios
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de segmentos por usuario
CREATE TABLE IF NOT EXISTS usuario_segmentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    segmento VARCHAR(10) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE KEY unique_usuario_segmento (usuario_id, segmento),
    INDEX idx_usuario_activo (usuario_id, activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de historial de oportunidades vistas
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de configuración de usuario
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar usuarios de ejemplo (actualiza los que teníamos)
INSERT INTO usuarios (numero, nombre, email, activo) VALUES
('51967717179', 'Elisa Rivadaneira', '', TRUE),
('51999888777', 'Carlos Mendoza', '', TRUE),
('51988776655', 'Ana Torres', '', TRUE)
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

SELECT '✅ Base de datos seace_monitor creada correctamente' AS status;
SELECT CONCAT('📊 Total usuarios: ', COUNT(*)) AS info FROM usuarios;
