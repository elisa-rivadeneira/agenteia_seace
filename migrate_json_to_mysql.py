import json
import os
from database_mysql import agregar_usuario, obtener_usuarios

def migrar_usuarios():
    usuarios_file = 'usuarios.json'

    if not os.path.exists(usuarios_file):
        print(f"❌ No se encontró {usuarios_file}")
        return False

    with open(usuarios_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    usuarios = data.get('usuarios', [])

    print(f"📋 Migrando {len(usuarios)} usuarios desde JSON a MySQL...")

    for usuario in usuarios:
        numero = usuario.get('numero')
        nombre = usuario.get('nombre')
        email = usuario.get('email', '')
        segmentos = usuario.get('segmentos', [])

        if agregar_usuario(numero, nombre, email, segmentos):
            print(f"  ✅ {nombre} ({numero}) - Segmentos: {segmentos}")
        else:
            print(f"  ❌ Error al migrar {nombre}")

    print("\n✅ Migración completada!")
    print("\n📊 Verificando usuarios en MySQL:")
    usuarios_mysql = obtener_usuarios()
    for u in usuarios_mysql:
        print(f"  - {u['nombre']} ({u['numero']}): Segmentos {u['segmentos']}")

    return True

if __name__ == "__main__":
    migrar_usuarios()
