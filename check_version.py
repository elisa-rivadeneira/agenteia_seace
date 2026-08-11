#!/usr/bin/env python3
"""
Script para verificar qué versión del código está en ejecución
"""

print("=" * 80)
print("🔍 VERIFICACIÓN DE VERSIÓN DEL CÓDIGO")
print("=" * 80)

# Verificar agente_ia.py
print("\n1️⃣ Verificando agente_ia.py...")
try:
    with open('agente_ia.py', 'r') as f:
        contenido = f.read()
        if "VERSION 2026-08-11 08:30" in contenido:
            print("   ✅ Contiene banner de versión 2026-08-11 08:30")
        else:
            print("   ❌ NO contiene banner de versión")

        if "from database_mysql import" in contenido:
            print("   ✅ Importa de database_mysql (CORRECTO)")
        elif "from database_manager import" in contenido:
            print("   ❌ Importa de database_manager (INCORRECTO - código viejo)")
        else:
            print("   ⚠️ No se encontró import de database")
except Exception as e:
    print(f"   ❌ Error leyendo archivo: {e}")

# Verificar si database_mysql.py existe
print("\n2️⃣ Verificando database_mysql.py...")
try:
    with open('database_mysql.py', 'r') as f:
        contenido = f.read()
        print(f"   ✅ Archivo existe ({len(contenido)} caracteres)")
except Exception as e:
    print(f"   ❌ Archivo NO existe: {e}")

# Verificar variables de entorno
print("\n3️⃣ Verificando variables de entorno...")
import os
print(f"   PYTHONUNBUFFERED: {os.getenv('PYTHONUNBUFFERED', 'NO CONFIGURADO')}")
print(f"   PYTHONDONTWRITEBYTECODE: {os.getenv('PYTHONDONTWRITEBYTECODE', 'NO CONFIGURADO')}")
print(f"   DB_HOST: {os.getenv('DB_HOST', 'NO CONFIGURADO')}")

# Verificar archivos .pyc
print("\n4️⃣ Verificando archivos .pyc...")
import glob
pyc_files = glob.glob('**/*.pyc', recursive=True)
pycache_dirs = glob.glob('**/__pycache__', recursive=True)
print(f"   Archivos .pyc: {len(pyc_files)}")
print(f"   Directorios __pycache__: {len(pycache_dirs)}")
if pyc_files:
    print("   ⚠️ ADVERTENCIA: Existen archivos .pyc (puede ser cache viejo)")
    for f in pyc_files[:5]:
        print(f"      - {f}")

# Test de conexión a MySQL
print("\n5️⃣ Test de conexión a MySQL...")
try:
    from database_mysql import obtener_usuario_por_numero, obtener_segmentos_usuario
    usuario = obtener_usuario_por_numero("51967717179")
    if usuario:
        print(f"   ✅ Usuario encontrado: {usuario.get('nombre')}")
        print(f"   ID: {usuario.get('id')}")
        segmentos = obtener_segmentos_usuario(usuario['id'])
        print(f"   Segmentos: {segmentos}")
    else:
        print("   ❌ Usuario NO encontrado en MySQL")
except Exception as e:
    print(f"   ❌ Error conectando a MySQL: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ Verificación completada")
print("=" * 80)
