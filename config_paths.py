#!/usr/bin/env python3
"""
Gestión de rutas para archivos persistentes
Permite usar /data en producción (volumen Docker) o local en desarrollo
"""

import os
from pathlib import Path

# Detectar si estamos en producción (Docker) o desarrollo (local)
IS_PRODUCTION = os.getenv('FLASK_ENV', 'development') == 'production'

# Directorio base para datos persistentes
if IS_PRODUCTION:
    DATA_DIR = Path('/data')
else:
    DATA_DIR = Path(__file__).parent

# Crear directorio si no existe
DATA_DIR.mkdir(exist_ok=True)

# Archivos críticos que deben persistir
CONVERSACIONES_FILE = DATA_DIR / 'conversaciones_log.json'
ALERTAS_CONFIG_FILE = DATA_DIR / 'alertas_config.json'
HISTORIAL_OPORTUNIDADES_FILE = DATA_DIR / 'historial_oportunidades.json'

# Configuración de empresa (puede estar en código o en volumen)
CONFIG_EMPRESA_FILE = DATA_DIR / 'config_empresa.json'

# Crear archivos por defecto si no existen
def inicializar_archivos():
    """Crea archivos por defecto si no existen"""
    import json

    # Conversaciones
    if not CONVERSACIONES_FILE.exists():
        with open(CONVERSACIONES_FILE, 'w', encoding='utf-8') as f:
            json.dump({"conversaciones": {}}, f, ensure_ascii=False, indent=2)
        print(f"✅ Creado: {CONVERSACIONES_FILE}")

    # Alertas config
    if not ALERTAS_CONFIG_FILE.exists():
        config_default = {
            "horarios": [
                {"hora": "10:00", "activo": True, "descripcion": "Escaneo matutino"},
                {"hora": "19:00", "activo": True, "descripcion": "Escaneo vespertino"}
            ],
            "destinatarios": [],
            "configuracion": {
                "score_minimo": 30,
                "max_oportunidades_por_alerta": 5,
                "enviar_resumen": True,
                "enviar_detalles": True
            }
        }
        with open(ALERTAS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_default, f, ensure_ascii=False, indent=2)
        print(f"✅ Creado: {ALERTAS_CONFIG_FILE}")

    # Historial oportunidades
    if not HISTORIAL_OPORTUNIDADES_FILE.exists():
        with open(HISTORIAL_OPORTUNIDADES_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "ultima_actualizacion": "",
                "nomenclaturas_vistas": [],
                "total_vistas": 0
            }, f, ensure_ascii=False, indent=2)
        print(f"✅ Creado: {HISTORIAL_OPORTUNIDADES_FILE}")

# Ejecutar al importar
if __name__ != "__main__":
    inicializar_archivos()

def get_data_path(filename: str) -> Path:
    """Obtiene la ruta completa para un archivo en el directorio de datos"""
    return DATA_DIR / filename

print(f"📁 Directorio de datos: {DATA_DIR}")
print(f"🔧 Modo: {'PRODUCCIÓN' if IS_PRODUCTION else 'DESARROLLO'}")
