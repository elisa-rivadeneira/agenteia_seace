#!/usr/bin/env python3
"""
Inicializa el historial de oportunidades para un usuario nuevo
Esto evita que el primer escaneo envíe TODAS las oportunidades como "nuevas"
"""

from datetime import datetime
from database_mysql import get_connection
from seace_extractor_realtime import extraer_oportunidades_realtime

def obtener_usuario_por_numero(numero):
    """Obtiene el usuario por su número de teléfono"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nombre, numero
            FROM usuarios
            WHERE numero = %s AND activo = TRUE
        """, (numero,))

        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        return usuario
    except Exception as e:
        print(f"❌ Error al buscar usuario: {e}")
        return None

def obtener_segmentos_usuario(usuario_id):
    """Obtiene los segmentos activos de un usuario"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT segmento
            FROM usuario_segmentos
            WHERE usuario_id = %s AND activo = TRUE
        """, (usuario_id,))

        segmentos = [row['segmento'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return segmentos
    except Exception as e:
        print(f"❌ Error al obtener segmentos: {e}")
        return []

def inicializar_historial_usuario(numero_usuario, verbose=True):
    """
    Inicializa el historial de un usuario con las oportunidades actuales

    Esto marca todas las oportunidades existentes como "ya vistas"
    para que el sistema solo alerte sobre NUEVAS licitaciones que aparezcan después

    Args:
        numero_usuario: Número de WhatsApp del usuario
        verbose: Si True, muestra información detallada

    Returns:
        dict: Resultado del proceso con estadísticas
    """
    if verbose:
        print("="*80)
        print("🔧 INICIALIZACIÓN DE HISTORIAL DE USUARIO")
        print("="*80)
        print(f"\n📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    if numero_usuario.startswith('+'):
        numero_usuario = numero_usuario[1:]
    if '@' in numero_usuario:
        numero_usuario = numero_usuario.split('@')[0]

    usuario = obtener_usuario_por_numero(numero_usuario)

    if not usuario:
        if verbose:
            print(f"\n❌ Usuario {numero_usuario} no encontrado o inactivo")
        return {
            "exito": False,
            "error": "Usuario no encontrado"
        }

    if verbose:
        print(f"\n✅ Usuario encontrado:")
        print(f"   ID: {usuario['id']}")
        print(f"   Nombre: {usuario['nombre']}")

    segmentos = obtener_segmentos_usuario(usuario['id'])

    if not segmentos:
        if verbose:
            print(f"\n⚠️ Usuario no tiene segmentos configurados")
        return {
            "exito": False,
            "error": "Sin segmentos configurados"
        }

    if verbose:
        print(f"\n📊 Segmentos configurados: {len(segmentos)}")
        print(f"   {', '.join(segmentos)}")

    resultado = {
        "exito": True,
        "usuario_id": usuario['id'],
        "usuario_nombre": usuario['nombre'],
        "segmentos_procesados": 0,
        "oportunidades_insertadas": 0,
        "oportunidades_duplicadas": 0,
        "detalles_por_segmento": []
    }

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for segmento in segmentos:
            if verbose:
                print(f"\n📊 Procesando segmento {segmento}...")

            try:
                resultado_extraccion = extraer_oportunidades_realtime(segmento)

                if not resultado_extraccion or resultado_extraccion.get('total_oportunidades', 0) == 0:
                    if verbose:
                        print(f"   ⚠️ No se obtuvieron oportunidades")
                    continue

                oportunidades = resultado_extraccion.get('oportunidades', [])

                if verbose:
                    print(f"   Total encontradas: {len(oportunidades)}")

                insertadas = 0
                duplicadas = 0

                for op in oportunidades:
                    nomenclatura = op.get('nomenclatura', '')

                    if not nomenclatura:
                        continue

                    try:
                        cursor.execute("""
                            INSERT INTO historial_oportunidades (usuario_id, segmento, nomenclatura)
                            VALUES (%s, %s, %s)
                        """, (usuario['id'], segmento, nomenclatura))
                        insertadas += 1
                    except Exception:
                        duplicadas += 1

                conn.commit()

                if verbose:
                    print(f"   ✅ Insertadas: {insertadas}")
                    if duplicadas > 0:
                        print(f"   ⚠️ Duplicadas (ya existían): {duplicadas}")

                resultado['segmentos_procesados'] += 1
                resultado['oportunidades_insertadas'] += insertadas
                resultado['oportunidades_duplicadas'] += duplicadas

                resultado['detalles_por_segmento'].append({
                    "segmento": segmento,
                    "total": len(oportunidades),
                    "insertadas": insertadas,
                    "duplicadas": duplicadas
                })

            except Exception as e:
                if verbose:
                    print(f"   ❌ Error en segmento {segmento}: {e}")
                continue

        cursor.close()
        conn.close()

        if verbose:
            print("\n" + "="*80)
            print("✅ HISTORIAL INICIALIZADO")
            print("="*80)
            print(f"\n📊 Resumen:")
            print(f"   Segmentos procesados: {resultado['segmentos_procesados']}/{len(segmentos)}")
            print(f"   Oportunidades guardadas: {resultado['oportunidades_insertadas']}")
            if resultado['oportunidades_duplicadas'] > 0:
                print(f"   Duplicadas (ya existían): {resultado['oportunidades_duplicadas']}")
            print(f"\n💡 A partir de ahora, solo recibirás alertas de oportunidades NUEVAS")

        return resultado

    except Exception as e:
        if verbose:
            print(f"\n❌ Error durante la inicialización: {e}")
            import traceback
            traceback.print_exc()

        return {
            "exito": False,
            "error": str(e)
        }

def inicializar_historial_todos_usuarios():
    """
    Inicializa el historial para TODOS los usuarios activos
    Útil para hacer una inicialización masiva
    """
    print("="*80)
    print("🔧 INICIALIZACIÓN MASIVA DE HISTORIAL")
    print("="*80)

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, numero, nombre
            FROM usuarios
            WHERE activo = TRUE
        """)

        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()

        if not usuarios:
            print("\n⚠️ No hay usuarios activos")
            return

        print(f"\n👥 Usuarios activos encontrados: {len(usuarios)}")

        resultados = []

        for usuario in usuarios:
            print(f"\n{'='*80}")
            print(f"📱 Usuario: {usuario['nombre']} ({usuario['numero']})")
            print("="*80)

            resultado = inicializar_historial_usuario(usuario['numero'], verbose=True)
            resultados.append({
                "usuario": usuario['nombre'],
                "numero": usuario['numero'],
                "resultado": resultado
            })

            import time
            time.sleep(2)

        print("\n" + "="*80)
        print("✅ INICIALIZACIÓN MASIVA COMPLETADA")
        print("="*80)

        print(f"\n📊 Resumen global:")
        total_insertadas = sum(r['resultado'].get('oportunidades_insertadas', 0) for r in resultados)
        usuarios_exitosos = sum(1 for r in resultados if r['resultado'].get('exito', False))

        print(f"   Usuarios procesados: {usuarios_exitosos}/{len(usuarios)}")
        print(f"   Total oportunidades guardadas: {total_insertadas}")

    except Exception as e:
        print(f"\n❌ Error en inicialización masiva: {e}")
        import traceback
        traceback.print_exc()

def main():
    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 inicializar_historial_usuario.py <numero_usuario>")
        print("  python3 inicializar_historial_usuario.py --todos")
        print("\nEjemplos:")
        print("  python3 inicializar_historial_usuario.py 51967717179")
        print("  python3 inicializar_historial_usuario.py +51967717179")
        print("  python3 inicializar_historial_usuario.py --todos")
        print("\n💡 Propósito:")
        print("  Marca las oportunidades actuales como 'ya vistas' para que el sistema")
        print("  solo alerte sobre NUEVAS licitaciones que aparezcan después.")
        return

    if sys.argv[1] == '--todos':
        inicializar_historial_todos_usuarios()
    else:
        numero_usuario = sys.argv[1]
        inicializar_historial_usuario(numero_usuario, verbose=True)

if __name__ == "__main__":
    main()
