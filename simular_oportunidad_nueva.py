#!/usr/bin/env python3
"""
Simula una oportunidad nueva borrándola del historial
Útil para testing del sistema de alertas
"""

from database_mysql import get_connection, obtener_usuario_por_numero
import sys

def simular_oportunidad_nueva(numero_usuario, cantidad=1):
    """
    Borra N oportunidades del historial de un usuario para simular que son nuevas

    Args:
        numero_usuario: Número de WhatsApp del usuario
        cantidad: Cuántas oportunidades borrar (default: 1)
    """
    try:
        # Normalizar número
        if '@' in numero_usuario:
            numero_usuario = numero_usuario.split('@')[0]
        if numero_usuario.startswith('+'):
            numero_usuario = numero_usuario[1:]

        from database_mysql import obtener_usuario_por_numero
        usuario = obtener_usuario_por_numero(numero_usuario)

        if not usuario:
            print(f"❌ Usuario {numero_usuario} no encontrado")
            return

        print("="*80)
        print(f"🧪 SIMULANDO {cantidad} OPORTUNIDAD(ES) NUEVA(S)")
        print("="*80)
        print(f"\n👤 Usuario: {usuario['nombre']} ({usuario['numero']})")

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener oportunidades aleatorias del historial
        cursor.execute("""
            SELECT h.id, h.nomenclatura, h.segmento, h.fecha_visto
            FROM historial_oportunidades h
            WHERE h.usuario_id = %s
            ORDER BY RAND()
            LIMIT %s
        """, (usuario['id'], cantidad))

        oportunidades = cursor.fetchall()

        if not oportunidades:
            print("\n⚠️ Este usuario no tiene historial de oportunidades")
            cursor.close()
            conn.close()
            return

        print(f"\n📋 Oportunidades que se simularán como NUEVAS:\n")

        for i, op in enumerate(oportunidades, 1):
            print(f"{i}. {op['nomenclatura']} (Segmento {op['segmento']})")
            print(f"   Visto: {op['fecha_visto']}")

        # Confirmar
        confirmar = input(f"\n¿Borrar estas {cantidad} oportunidad(es) del historial? (s/n): ").lower()

        if confirmar != 's':
            print("❌ Cancelado")
            cursor.close()
            conn.close()
            return

        # Borrar del historial
        ids_borrar = [op['id'] for op in oportunidades]
        placeholders = ','.join(['%s'] * len(ids_borrar))

        cursor.execute(f"""
            DELETE FROM historial_oportunidades
            WHERE id IN ({placeholders})
        """, ids_borrar)

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n✅ {len(oportunidades)} oportunidad(es) borradas del historial")
        print("\n" + "="*80)
        print("🚀 SIGUIENTE PASO")
        print("="*80)
        print("\nEjecuta el monitor para detectar estas oportunidades como 'nuevas':")
        print(f"\n  python3 monitor_nuevas_oportunidades.py --test")
        print("\nO en producción (Docker):")
        print(f"\n  docker exec -it [container_id] python3 monitor_nuevas_oportunidades.py --test")
        print("\n📱 Deberías recibir alerta(s) en WhatsApp con estas oportunidades\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 simular_oportunidad_nueva.py <numero_usuario> [cantidad]")
        print("\nEjemplo:")
        print("  python3 simular_oportunidad_nueva.py 51967717179")
        print("  python3 simular_oportunidad_nueva.py 51967717179 5")
        print("\n💡 Esto borrará oportunidades del historial para simular que son nuevas")
        return

    numero_usuario = sys.argv[1]
    cantidad = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    simular_oportunidad_nueva(numero_usuario, cantidad)

if __name__ == "__main__":
    main()
