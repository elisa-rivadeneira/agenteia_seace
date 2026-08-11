#!/usr/bin/env python3
"""
Monitor de nuevas oportunidades SEACE - Sistema de alertas en tiempo real
Detecta cuando aparecen NUEVAS licitaciones y alerta a los usuarios
"""

import schedule
import time
from datetime import datetime
from typing import List, Dict
from database_mysql import get_connection, obtener_usuario_por_numero
from seace_extractor_realtime import extraer_oportunidades_realtime
from whatsapp_notifier import WhatsAppNotifier

class MonitorNuevasOportunidades:
    def __init__(self):
        self.whatsapp = WhatsAppNotifier()
        print("✅ Monitor de nuevas oportunidades inicializado")

    def obtener_usuarios_activos_con_alertas_realtime(self):
        """
        Obtiene todos los usuarios que tienen alertas en tiempo real activas
        Y QUE YA HAYAN INICIALIZADO SU HISTORIAL (ejecutado /init)
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    u.id,
                    u.numero,
                    u.nombre,
                    c.score_minimo,
                    c.max_oportunidades_alerta,
                    COUNT(DISTINCT h.id) as tiene_historial
                FROM usuarios u
                INNER JOIN usuario_configuracion c ON u.id = c.usuario_id
                LEFT JOIN historial_oportunidades h ON u.id = h.usuario_id
                WHERE u.activo = TRUE
                  AND c.alertas_realtime_activas = TRUE
                GROUP BY u.id, u.numero, u.nombre, c.score_minimo, c.max_oportunidades_alerta
                HAVING tiene_historial > 0
            """)

            usuarios = cursor.fetchall()
            cursor.close()
            conn.close()

            return usuarios

        except Exception as e:
            print(f"❌ Error al obtener usuarios: {e}")
            return []

    def obtener_segmentos_usuario(self, usuario_id):
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

    def detectar_nuevas_oportunidades_usuario(self, usuario_id, segmento):
        """
        Detecta oportunidades NUEVAS para un usuario en un segmento específico
        Compara con historial_oportunidades en MySQL
        """
        try:
            resultado = extraer_oportunidades_realtime(segmento)

            if not resultado or resultado.get('total_oportunidades', 0) == 0:
                return []

            oportunidades = resultado.get('oportunidades', [])

            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            oportunidades_nuevas = []

            for op in oportunidades:
                nomenclatura = op.get('nomenclatura', '')
                if not nomenclatura:
                    continue

                cursor.execute("""
                    SELECT id FROM historial_oportunidades
                    WHERE usuario_id = %s
                      AND segmento = %s
                      AND nomenclatura = %s
                """, (usuario_id, segmento, nomenclatura))

                ya_vista = cursor.fetchone()

                if not ya_vista:
                    oportunidades_nuevas.append(op)

                    cursor.execute("""
                        INSERT INTO historial_oportunidades (usuario_id, segmento, nomenclatura)
                        VALUES (%s, %s, %s)
                    """, (usuario_id, segmento, nomenclatura))

            conn.commit()
            cursor.close()
            conn.close()

            return oportunidades_nuevas

        except Exception as e:
            print(f"❌ Error detectando nuevas oportunidades: {e}")
            import traceback
            traceback.print_exc()
            return []

    def formato_alerta_nueva_oportunidad(self, oportunidad: Dict) -> str:
        """Formatea una nueva oportunidad para WhatsApp"""
        score = oportunidad.get('score_compatibilidad', 0)
        emoji_score = "🌟" if score >= 70 else "✅" if score >= 50 else "📌"

        mensaje = f"""🚨 *NUEVA LICITACIÓN DETECTADA*

{emoji_score} *Score de compatibilidad: {score}%*

*Entidad:*
{oportunidad.get('entidad', 'N/A')}

*Descripción:*
{oportunidad.get('descripcion_item', 'N/A')[:200]}

📅 *Fechas importantes:*
• Inicio consultas: {oportunidad.get('fecha_inicio', 'N/A')}
• Fin consultas: {oportunidad.get('fecha_fin', 'N/A')}
• Presentación propuestas: {oportunidad.get('fecha_presentacion', 'N/A')}

🔗 *Ver en SEACE:*
{oportunidad.get('url_seace', 'N/A')}

*Nomenclatura:* {oportunidad.get('nomenclatura', 'N/A')}
"""
        return mensaje.strip()

    def escanear_y_alertar(self):
        """
        Función principal que escanea SEACE y alerta a usuarios con nuevas oportunidades
        """
        print("\n" + "="*80)
        print(f"🔍 ESCANEANDO NUEVAS OPORTUNIDADES - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("="*80)

        usuarios = self.obtener_usuarios_activos_con_alertas_realtime()

        if not usuarios:
            print("⚠️ No hay usuarios con alertas activas Y historial inicializado")
            print("💡 Los usuarios deben ejecutar /init primero para recibir alertas")
            return

        print(f"👥 Usuarios a monitorear (con historial inicializado): {len(usuarios)}")

        for usuario in usuarios:
            usuario_id = usuario['id']
            numero = usuario['numero']
            nombre = usuario['nombre']
            score_minimo = usuario.get('score_minimo', 30)
            max_ops = usuario.get('max_oportunidades_alerta', 5)

            print(f"\n📱 Usuario: {nombre} ({numero})")

            segmentos = self.obtener_segmentos_usuario(usuario_id)

            if not segmentos:
                print(f"   ⚠️ Sin segmentos configurados")
                continue

            print(f"   📊 Segmentos: {', '.join(segmentos)}")

            todas_nuevas = []

            for segmento in segmentos:
                print(f"   🔍 Escaneando segmento {segmento}...")

                nuevas = self.detectar_nuevas_oportunidades_usuario(usuario_id, segmento)

                if nuevas:
                    print(f"   🆕 {len(nuevas)} nuevas en segmento {segmento}")

                    nuevas_relevantes = [
                        op for op in nuevas
                        if op.get('score_compatibilidad', 0) >= score_minimo
                    ]

                    todas_nuevas.extend(nuevas_relevantes)

            if not todas_nuevas:
                print(f"   ✅ Sin oportunidades nuevas relevantes (score ≥{score_minimo}%)")
                continue

            print(f"   🚨 TOTAL NUEVAS RELEVANTES: {len(todas_nuevas)}")

            todas_nuevas_ordenadas = sorted(
                todas_nuevas,
                key=lambda x: x.get('score_compatibilidad', 0),
                reverse=True
            )[:max_ops]

            print(f"   📤 Enviando {len(todas_nuevas_ordenadas)} alertas...")

            mensaje_inicial = f"""🔔 *NUEVAS LICITACIONES DETECTADAS*

Se detectaron *{len(todas_nuevas)}* nuevas oportunidades que cumplen tus criterios (score ≥{score_minimo}%)

Te envío las {len(todas_nuevas_ordenadas)} más relevantes:"""

            self.whatsapp.send_message(mensaje_inicial, numero)
            time.sleep(2)

            for i, op in enumerate(todas_nuevas_ordenadas, 1):
                mensaje = self.formato_alerta_nueva_oportunidad(op)
                print(f"   📤 Enviando {i}/{len(todas_nuevas_ordenadas)}: {op.get('nomenclatura', 'N/A')}")
                self.whatsapp.send_message(mensaje, numero)
                time.sleep(2)

            print(f"   ✅ Alertas enviadas a {nombre}")

        print("\n" + "="*80)
        print("✅ ESCANEO COMPLETADO")
        print("="*80)

    def iniciar_monitor(self, intervalo_minutos=30):
        """
        Inicia el monitor con un intervalo específico

        Args:
            intervalo_minutos: Cada cuántos minutos escanear (default: 30)
        """
        print("="*80)
        print(" MONITOR DE NUEVAS OPORTUNIDADES SEACE")
        print("="*80)
        print(f"\n📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        print(f"⏰ Hora actual: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🔄 Intervalo: Cada {intervalo_minutos} minutos")

        schedule.every(intervalo_minutos).minutes.do(self.escanear_y_alertar)

        print("\n⚡ Monitor iniciado - Esperando nuevas oportunidades...")
        print("   Presiona Ctrl+C para detener\n")

        self.escanear_y_alertar()

        while True:
            schedule.run_pending()
            time.sleep(30)

def main():
    """Función principal"""
    import sys

    monitor = MonitorNuevasOportunidades()

    test_mode = '--test' in sys.argv

    if test_mode:
        print("\n🧪 Modo TEST - Ejecutando escaneo único...")
        monitor.escanear_y_alertar()
        print("\nTest completado.")
        return

    intervalo = 30
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        intervalo = int(sys.argv[1])

    try:
        monitor.iniciar_monitor(intervalo_minutos=intervalo)
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitor detenido")
        print("✅ Historial guardado en MySQL")

if __name__ == "__main__":
    main()
