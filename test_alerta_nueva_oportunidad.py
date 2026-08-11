#!/usr/bin/env python3
"""
Script de prueba para el sistema de alertas de NUEVAS oportunidades
Simula la detección en tiempo real cuando aparece una licitación nueva
"""

from datetime import datetime
import sys
import os
from database_mysql import get_connection, inicializar_bd

def limpiar_historial_usuario(usuario_id):
    """
    Limpia el historial de oportunidades vistas de un usuario
    Esto simula un estado "limpio" para detectar TODAS como nuevas
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM historial_oportunidades
            WHERE usuario_id = %s
        """, (usuario_id,))

        filas_eliminadas = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        return filas_eliminadas
    except Exception as e:
        print(f"❌ Error al limpiar historial: {e}")
        return 0

def obtener_usuario_por_numero(numero):
    """Obtiene el ID del usuario por su número de teléfono"""
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

def test_deteccion_nuevas_oportunidades(numero_usuario, segmento, limpiar=False):
    """
    Testea la detección de oportunidades nuevas

    Args:
        numero_usuario: Número de WhatsApp del usuario
        segmento: Segmento SEACE a escanear
        limpiar: Si True, limpia el historial antes (todas serán "nuevas")
    """
    print("="*80)
    print("🧪 TEST: DETECCIÓN DE NUEVAS OPORTUNIDADES")
    print("="*80)
    print(f"\n📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    usuario = obtener_usuario_por_numero(numero_usuario)

    if not usuario:
        print(f"\n❌ Usuario {numero_usuario} no encontrado o inactivo")
        print("\nVerifica que el usuario existe en la base de datos:")
        print("SELECT * FROM usuarios WHERE numero = '{}'".format(numero_usuario))
        return

    print(f"\n✅ Usuario encontrado:")
    print(f"   ID: {usuario['id']}")
    print(f"   Nombre: {usuario['nombre']}")
    print(f"   Número: {usuario['numero']}")

    if limpiar:
        print(f"\n🧹 Limpiando historial para simular oportunidades nuevas...")
        eliminadas = limpiar_historial_usuario(usuario['id'])
        print(f"   Historial eliminado: {eliminadas} registros")

    print(f"\n📊 Segmento a escanear: {segmento}")
    print("\n" + "="*80)
    print("🔍 EJECUTANDO ESCANEO")
    print("="*80)

    from seace_extractor_realtime import extraer_oportunidades_realtime
    from whatsapp_notifier import WhatsAppNotifier

    resultado = extraer_oportunidades_realtime(segmento)

    if not resultado or resultado.get('total_oportunidades', 0) == 0:
        print("\n❌ No se obtuvieron oportunidades del escaneo")
        return

    oportunidades = resultado.get('oportunidades', [])
    print(f"\n📊 Total oportunidades escaneadas: {len(oportunidades)}")

    score_minimo = 30
    oportunidades_relevantes = [
        op for op in oportunidades
        if op.get('score_compatibilidad', 0) >= score_minimo
    ]

    print(f"⭐ Oportunidades relevantes (score ≥{score_minimo}%): {len(oportunidades_relevantes)}")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        oportunidades_nuevas = []
        oportunidades_ya_vistas = []

        for op in oportunidades_relevantes:
            nomenclatura = op.get('nomenclatura', '')

            if not nomenclatura:
                continue

            cursor.execute("""
                SELECT id FROM historial_oportunidades
                WHERE usuario_id = %s
                  AND segmento = %s
                  AND nomenclatura = %s
            """, (usuario['id'], segmento, nomenclatura))

            ya_vista = cursor.fetchone()

            if ya_vista:
                oportunidades_ya_vistas.append(op)
            else:
                oportunidades_nuevas.append(op)

                cursor.execute("""
                    INSERT INTO historial_oportunidades (usuario_id, segmento, nomenclatura)
                    VALUES (%s, %s, %s)
                """, (usuario['id'], segmento, nomenclatura))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n📋 Resultado de la detección:")
        print(f"   🆕 Nuevas (no vistas antes): {len(oportunidades_nuevas)}")
        print(f"   👁️ Ya vistas: {len(oportunidades_ya_vistas)}")

        if not oportunidades_nuevas:
            print("\n⚠️ No hay oportunidades NUEVAS para alertar")
            print("   Todas las oportunidades relevantes ya fueron vistas anteriormente")
            print("\n💡 Para simular detección de nuevas:")
            print(f"   python3 {sys.argv[0]} {numero_usuario} {segmento} --limpiar")
            return

        print("\n" + "="*80)
        print(f"🚨 ENVIANDO ALERTAS DE {len(oportunidades_nuevas)} OPORTUNIDADES NUEVAS")
        print("="*80)

        whatsapp = WhatsAppNotifier()

        mensaje_inicial = f"""🚨 *NUEVAS OPORTUNIDADES DETECTADAS*
📊 Segmento: {segmento}
Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}

🆕 Se detectaron *{len(oportunidades_nuevas)} oportunidades nuevas* que no habías visto antes

Te las envío a continuación..."""

        print(f"\n📤 Enviando mensaje inicial...")
        whatsapp.send_message(mensaje_inicial, numero_usuario)

        import time
        time.sleep(2)

        for i, op in enumerate(oportunidades_nuevas, 1):
            score = op.get('score_compatibilidad', 0)
            emoji_score = "🌟" if score >= 70 else "✅" if score >= 50 else "📌"

            mensaje = f"""🚨 *NUEVA OPORTUNIDAD #{i}*

{emoji_score} *Score de compatibilidad: {score}%*

*Entidad:*
{op.get('entidad', 'N/A')}

*Descripción:*
{op.get('descripcion_item', 'N/A')[:200]}

📅 *Fechas importantes:*
• Inicio consultas: {op.get('fecha_inicio', 'N/A')}
• Fin consultas: {op.get('fecha_fin', 'N/A')}
• Presentación propuestas: {op.get('fecha_presentacion', 'N/A')}

🔗 *Ver en SEACE:*
{op.get('url_seace', 'N/A')}

*Nomenclatura:* {op.get('nomenclatura', 'N/A')}"""

            print(f"📤 Enviando oportunidad {i}/{len(oportunidades_nuevas)}: {op.get('nomenclatura', 'N/A')}")
            whatsapp.send_message(mensaje, numero_usuario)
            time.sleep(2)

        print("\n" + "="*80)
        print("✅ TEST COMPLETADO")
        print("="*80)
        print(f"\n📱 Verifica tu WhatsApp: {numero_usuario}")
        print(f"📊 Alertas enviadas: {len(oportunidades_nuevas)}")
        print(f"📝 Historial actualizado: {len(oportunidades_nuevas)} nuevos registros")

    except Exception as e:
        print(f"\n❌ Error durante la detección: {e}")
        import traceback
        traceback.print_exc()

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 test_alerta_nueva_oportunidad.py <numero_usuario> <segmento> [--limpiar]")
        print("\nEjemplo:")
        print("  python3 test_alerta_nueva_oportunidad.py 51967717179 86")
        print("  python3 test_alerta_nueva_oportunidad.py 51967717179 86 --limpiar")
        print("\nOpciones:")
        print("  --limpiar    Limpia el historial antes (todas las oportunidades serán detectadas como nuevas)")
        return

    numero_usuario = sys.argv[1]

    if numero_usuario.startswith('+'):
        numero_usuario = numero_usuario[1:]
    if '@' in numero_usuario:
        numero_usuario = numero_usuario.split('@')[0]

    segmento = sys.argv[2]

    limpiar = '--limpiar' in sys.argv

    test_deteccion_nuevas_oportunidades(numero_usuario, segmento, limpiar)

if __name__ == "__main__":
    main()
