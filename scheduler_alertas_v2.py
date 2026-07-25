#!/usr/bin/env python3
"""
Sistema de Alertas Automáticas SEACE v2.0
Lee alertas desde la base de datos y ejecuta según configuración
"""

import schedule
import time
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Set
from seace_extractor_realtime import extraer_oportunidades_realtime
from whatsapp_notifier import WhatsAppNotifier
from agente_ia import AgenteIASEACE
from database_manager import cargar_alertas, obtener_usuario, registrar_ejecucion_alerta
from config_paths import HISTORIAL_OPORTUNIDADES_FILE

class SchedulerAlertasV2:
    def __init__(self):
        self.whatsapp = WhatsAppNotifier()
        self.agente_ia = AgenteIASEACE()
        self.historial_file = HISTORIAL_OPORTUNIDADES_FILE
        self.oportunidades_vistas = self._cargar_historial()

        print("✅ Sistema de alertas V2 inicializado")
        print(f"📁 Historial: {self.historial_file}")

    def _cargar_historial(self) -> Set[str]:
        """Carga el historial de oportunidades ya vistas"""
        if self.historial_file.exists():
            try:
                with open(self.historial_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('nomenclaturas_vistas', []))
            except:
                return set()
        return set()

    def _guardar_historial(self, nomenclaturas: Set[str]):
        """Guarda el historial de oportunidades vistas"""
        data = {
            'ultima_actualizacion': datetime.now().isoformat(),
            'nomenclaturas_vistas': list(nomenclaturas),
            'total_vistas': len(nomenclaturas)
        }
        with open(self.historial_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def detectar_nuevas_oportunidades(self, oportunidades: List[Dict]) -> List[Dict]:
        """Detecta oportunidades nuevas que no hemos visto antes"""
        nuevas = []

        for op in oportunidades:
            nomenclatura = op.get('nomenclatura', '')
            if nomenclatura and nomenclatura not in self.oportunidades_vistas:
                nuevas.append(op)
                self.oportunidades_vistas.add(nomenclatura)

        if nuevas:
            self._guardar_historial(self.oportunidades_vistas)

        return nuevas

    def formato_alerta_whatsapp(self, oportunidad: Dict) -> str:
        """Formatea una oportunidad nueva para WhatsApp"""
        score = oportunidad.get('score_compatibilidad', 0)
        emoji_score = "🌟" if score >= 70 else "✅" if score >= 50 else "📌"

        mensaje = f"""🚨 *NUEVA OPORTUNIDAD SEACE*

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

    def ejecutar_alerta(self, alerta: Dict):
        """Ejecuta una alerta específica"""
        alerta_id = alerta.get('id')
        nombre_alerta = alerta.get('nombre', 'Sin nombre')
        segmento = alerta.get('segmento', '43')
        usuarios = alerta.get('usuarios', [])
        config = alerta.get('configuracion', {})
        score_minimo = config.get('score_minimo', 30)
        max_ops = config.get('max_oportunidades', 5)

        hora_actual = datetime.now().strftime('%H:%M:%S')
        print(f"\n{'='*80}")
        print(f"🔍 EJECUTANDO ALERTA: {nombre_alerta}")
        print(f"⏰ Hora: {hora_actual}")
        print(f"📊 Segmento: {segmento}")
        print(f"{'='*80}")

        if not usuarios:
            print("⚠️ No hay usuarios asignados a esta alerta")
            return

        print(f"📱 Destinatarios: {len(usuarios)}")
        print(f"📊 Score mínimo: {score_minimo}%")
        print(f"📈 Máx. oportunidades: {max_ops}")

        try:
            # Extraer oportunidades
            resultado = extraer_oportunidades_realtime()

            if not resultado or resultado.get('total_oportunidades', 0) == 0:
                print("⚠️ No se obtuvieron oportunidades del escaneo")
                return

            oportunidades = resultado.get('oportunidades', [])
            print(f"📊 Total oportunidades encontradas: {len(oportunidades)}")

            # Detectar nuevas
            nuevas = self.detectar_nuevas_oportunidades(oportunidades)
            print(f"🆕 Oportunidades nuevas: {len(nuevas)}")

            if not nuevas:
                print("✅ No hay oportunidades nuevas en este escaneo")
                mensaje_resumen = f"""📊 *Escaneo SEACE - {nombre_alerta}*
Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Total encontradas: {len(oportunidades)}
Nuevas: 0

_No hay nuevas oportunidades desde el último escaneo_"""

                # Enviar a todos los usuarios de la alerta
                for numero_usuario in usuarios:
                    usuario = obtener_usuario(numero_usuario)
                    if usuario and usuario.get('activo', False):
                        self.whatsapp.send_message(mensaje_resumen, numero_usuario)
                        time.sleep(1)

                # Registrar ejecución
                registrar_ejecucion_alerta(alerta_id)
                return

            # Filtrar por score
            nuevas_relevantes = [op for op in nuevas if op.get('score_compatibilidad', 0) >= score_minimo]
            print(f"⭐ Nuevas relevantes (≥{score_minimo}%): {len(nuevas_relevantes)}")

            # Mensaje inicial
            mensaje_inicial = f"""🔔 *ALERTA AUTOMÁTICA SEACE*
📋 {nombre_alerta}
Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}

*¡Se encontraron {len(nuevas)} nuevas oportunidades!*

{len(nuevas_relevantes)} con alta compatibilidad (≥{score_minimo}%)

Te enviaré los detalles de las más importantes..."""

            # Enviar a todos los usuarios
            for numero_usuario in usuarios:
                usuario = obtener_usuario(numero_usuario)
                if usuario and usuario.get('activo', False):
                    print(f"📤 Enviando a {usuario.get('nombre', numero_usuario)}")
                    self.whatsapp.send_message(mensaje_inicial, numero_usuario)
                    time.sleep(1)

            time.sleep(2)

            # Enviar detalles de oportunidades relevantes
            if nuevas_relevantes:
                for i, op in enumerate(nuevas_relevantes[:max_ops], 1):
                    print(f"📤 Enviando oportunidad {i}/{min(max_ops, len(nuevas_relevantes))}")
                    mensaje = self.formato_alerta_whatsapp(op)

                    for numero_usuario in usuarios:
                        usuario = obtener_usuario(numero_usuario)
                        if usuario and usuario.get('activo', False):
                            self.whatsapp.send_message(mensaje, numero_usuario)
                            time.sleep(1)

                    time.sleep(2)

                if len(nuevas_relevantes) > max_ops:
                    mensaje_extra = f"""
_Hay {len(nuevas_relevantes) - max_ops} oportunidades relevantes adicionales._

Envía */escanear* para ver el análisis completo con la IA."""

                    for numero_usuario in usuarios:
                        usuario = obtener_usuario(numero_usuario)
                        if usuario and usuario.get('activo', False):
                            self.whatsapp.send_message(mensaje_extra, numero_usuario)
                            time.sleep(1)
            else:
                mensaje_sin_relevantes = f"""_Las nuevas oportunidades tienen baja compatibilidad (<{score_minimo}%)_

Envía */escanear* para ver el análisis completo."""

                for numero_usuario in usuarios:
                    usuario = obtener_usuario(numero_usuario)
                    if usuario and usuario.get('activo', False):
                        self.whatsapp.send_message(mensaje_sin_relevantes, numero_usuario)
                        time.sleep(1)

            print(f"✅ Alerta '{nombre_alerta}' ejecutada para {len(usuarios)} usuario(s)")

            # Registrar ejecución
            registrar_ejecucion_alerta(alerta_id)

        except Exception as e:
            print(f"❌ Error ejecutando alerta '{nombre_alerta}': {e}")
            import traceback
            traceback.print_exc()

    def verificar_y_ejecutar_alertas(self):
        """Verifica y ejecuta alertas que correspondan a la hora actual"""
        ahora = datetime.now()
        hora_actual = ahora.strftime('%H:%M')
        dia_semana = ahora.weekday()  # 0=Lunes, 6=Domingo

        print(f"\n⏰ Verificando alertas - {hora_actual} - Día {dia_semana}")

        # Cargar alertas activas
        alertas = cargar_alertas()
        alertas_activas = [a for a in alertas if a.get('activo', False)]

        print(f"📋 Total alertas: {len(alertas)} | Activas: {len(alertas_activas)}")

        # Verificar cada alerta
        for alerta in alertas_activas:
            horarios = alerta.get('horarios', [])
            dias_semana = alerta.get('dias_semana', [])

            # Verificar si corresponde ejecutar ahora
            if hora_actual in horarios and dia_semana in dias_semana:
                print(f"✅ Ejecutando alerta: {alerta.get('nombre')}")
                self.ejecutar_alerta(alerta)

    def configurar_scheduler(self):
        """Configura el scheduler para verificar alertas cada minuto"""
        # Ejecutar verificación cada minuto
        schedule.every().minute.do(self.verificar_y_ejecutar_alertas)

        print("\n⏰ Scheduler configurado:")
        print("   • Verificación cada minuto")
        print("   • Ejecuta alertas según horarios y días configurados")

        # Mostrar próximas alertas
        self._mostrar_proximas_alertas()

    def _mostrar_proximas_alertas(self):
        """Muestra las próximas alertas programadas"""
        alertas = cargar_alertas()
        alertas_activas = [a for a in alertas if a.get('activo', False)]

        if not alertas_activas:
            print("\n⚠️ No hay alertas activas configuradas")
            return

        print(f"\n📋 Alertas activas: {len(alertas_activas)}")
        for alerta in alertas_activas:
            nombre = alerta.get('nombre', 'Sin nombre')
            horarios = alerta.get('horarios', [])
            dias = alerta.get('dias_semana', [])
            dias_nombres = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
            dias_str = ','.join([dias_nombres[d] for d in dias])

            print(f"   • {nombre}")
            print(f"     Horarios: {', '.join(horarios)}")
            print(f"     Días: {dias_str}")

    def iniciar(self):
        """Inicia el sistema de alertas"""
        print("="*80)
        print(" SISTEMA DE ALERTAS AUTOMÁTICAS SEACE V2")
        print("="*80)
        print(f"\n📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        print(f"⏰ Hora actual: {datetime.now().strftime('%H:%M:%S')}")

        self.configurar_scheduler()

        print("\n⚡ Sistema iniciado - Esperando próximas alertas...")
        print("   Presiona Ctrl+C para detener\n")

        while True:
            schedule.run_pending()
            time.sleep(30)  # Verificar cada 30 segundos

def main():
    """Función principal"""
    import sys

    scheduler = SchedulerAlertasV2()

    # Verificar si se pasa --test como argumento
    test_mode = '--test' in sys.argv

    if test_mode:
        print("\n🧪 Ejecutando test de alertas...")
        scheduler.verificar_y_ejecutar_alertas()
        print("\n" + "="*80)
        print("Test completado. Iniciando servicio...")

    print("\n🚀 Iniciando servicio de alertas...")

    try:
        scheduler.iniciar()
    except KeyboardInterrupt:
        print("\n\n⏹️ Sistema de alertas detenido")
        print("✅ Historial guardado")

if __name__ == "__main__":
    main()
