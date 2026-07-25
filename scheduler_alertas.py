#!/usr/bin/env python3
"""
Sistema de Alertas Automáticas SEACE
Escanea a las 10am y 7pm, detecta nuevas oportunidades y notifica por WhatsApp
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
from alertas_manager import cargar_config_alertas, obtener_destinatarios_activos
from config_paths import HISTORIAL_OPORTUNIDADES_FILE

class AlertasAutomaticas:
    def __init__(self):
        self.whatsapp = WhatsAppNotifier()
        self.agente_ia = AgenteIASEACE()
        self.historial_file = HISTORIAL_OPORTUNIDADES_FILE
        self.oportunidades_vistas = self._cargar_historial()

        print("✅ Sistema de alertas automáticas inicializado")
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

    def ejecutar_escaneo(self):
        """Ejecuta el escaneo y envía alertas de nuevas oportunidades"""
        hora_actual = datetime.now().strftime('%H:%M:%S')
        print(f"\n{'='*80}")
        print(f"🔍 ESCANEO AUTOMÁTICO SEACE - {hora_actual}")
        print(f"{'='*80}")

        try:
            config = cargar_config_alertas()
            destinatarios = obtener_destinatarios_activos()
            score_minimo = config.get('configuracion', {}).get('score_minimo', 30)
            max_ops = config.get('configuracion', {}).get('max_oportunidades_por_alerta', 5)

            print(f"📱 Destinatarios activos: {len(destinatarios)}")
            print(f"📊 Score mínimo: {score_minimo}%")
            print(f"📈 Máx. oportunidades: {max_ops}")

            if not destinatarios:
                print("⚠️ No hay destinatarios activos configurados")
                return

            resultado = extraer_oportunidades_realtime()

            if not resultado or resultado.get('total_oportunidades', 0) == 0:
                print("⚠️ No se obtuvieron oportunidades del escaneo")
                return

            oportunidades = resultado.get('oportunidades', [])
            print(f"📊 Total oportunidades encontradas: {len(oportunidades)}")

            nuevas = self.detectar_nuevas_oportunidades(oportunidades)
            print(f"🆕 Oportunidades nuevas: {len(nuevas)}")

            if not nuevas:
                print("✅ No hay oportunidades nuevas en este escaneo")
                mensaje_resumen = f"""📊 *Escaneo SEACE completado*
Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Total encontradas: {len(oportunidades)}
Nuevas: 0

_No hay nuevas oportunidades desde el último escaneo_"""

                for destinatario in destinatarios:
                    self.whatsapp.send_message(mensaje_resumen, destinatario)
                    time.sleep(1)
                return

            nuevas_relevantes = [op for op in nuevas if op.get('score_compatibilidad', 0) >= score_minimo]
            print(f"⭐ Nuevas relevantes (≥{score_minimo}%): {len(nuevas_relevantes)}")

            mensaje_inicial = f"""🔔 *ALERTA AUTOMÁTICA SEACE*
Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}

*¡Se encontraron {len(nuevas)} nuevas oportunidades!*

{len(nuevas_relevantes)} con alta compatibilidad (≥{score_minimo}%)

Te enviaré los detalles de las más importantes..."""

            for destinatario in destinatarios:
                self.whatsapp.send_message(mensaje_inicial, destinatario)
                time.sleep(1)

            time.sleep(2)

            if nuevas_relevantes:
                for i, op in enumerate(nuevas_relevantes[:max_ops], 1):
                    print(f"📤 Enviando oportunidad {i}/{min(max_ops, len(nuevas_relevantes))}")
                    mensaje = self.formato_alerta_whatsapp(op)

                    for destinatario in destinatarios:
                        self.whatsapp.send_message(mensaje, destinatario)
                        time.sleep(1)

                    time.sleep(2)

                if len(nuevas_relevantes) > max_ops:
                    mensaje_extra = f"""
_Hay {len(nuevas_relevantes) - max_ops} oportunidades relevantes adicionales._

Envía */escanear* para ver el análisis completo con la IA."""

                    for destinatario in destinatarios:
                        self.whatsapp.send_message(mensaje_extra, destinatario)
                        time.sleep(1)
            else:
                mensaje_sin_relevantes = f"""_Las nuevas oportunidades tienen baja compatibilidad (<{score_minimo}%)_

Envía */escanear* para ver el análisis completo."""

                for destinatario in destinatarios:
                    self.whatsapp.send_message(mensaje_sin_relevantes, destinatario)
                    time.sleep(1)

            print(f"✅ Alertas enviadas a {len(destinatarios)} destinatario(s)")

        except Exception as e:
            print(f"❌ Error en escaneo automático: {e}")
            import traceback
            traceback.print_exc()

            mensaje_error = f"""⚠️ *Error en escaneo automático*
Hora: {datetime.now().strftime('%H:%M')}

El sistema encontró un error. Por favor revisa los logs."""

            try:
                self.whatsapp.send_message(mensaje_error, self.usuario_numero)
            except:
                pass

    def configurar_horarios(self):
        """Configura los horarios de escaneo desde la configuración"""
        config = cargar_config_alertas()
        horarios_activos = [
            h for h in config.get('horarios', [])
            if h.get('activo', False)
        ]

        if not horarios_activos:
            print("⚠️ No hay horarios activos configurados. Usando horarios por defecto.")
            schedule.every().day.at("10:00").do(self.ejecutar_escaneo)
            schedule.every().day.at("19:00").do(self.ejecutar_escaneo)
            horarios_activos = [
                {'hora': '10:00', 'descripcion': 'Escaneo matutino'},
                {'hora': '19:00', 'descripcion': 'Escaneo vespertino'}
            ]
        else:
            for horario in horarios_activos:
                hora = horario.get('hora', '')
                schedule.every().day.at(hora).do(self.ejecutar_escaneo)

        print("\n⏰ Horarios de alerta configurados:")
        for h in horarios_activos:
            print(f"   • {h['hora']} - {h.get('descripcion', 'Alerta automática')}")

        print("\n⚡ Esperando próximo escaneo...")
        print(f"   Próximo: {self._calcular_proximo_escaneo()}")

    def _calcular_proximo_escaneo(self) -> str:
        """Calcula cuándo será el próximo escaneo"""
        ahora = datetime.now()
        hora_actual = ahora.hour
        minuto_actual = ahora.minute

        if hora_actual < 10:
            proximo = ahora.replace(hour=10, minute=0, second=0)
        elif hora_actual < 19:
            proximo = ahora.replace(hour=19, minute=0, second=0)
        else:
            proximo = (ahora + timedelta(days=1)).replace(hour=10, minute=0, second=0)

        diferencia = proximo - ahora
        horas = int(diferencia.total_seconds() // 3600)
        minutos = int((diferencia.total_seconds() % 3600) // 60)

        return f"{proximo.strftime('%d/%m %H:%M')} (en {horas}h {minutos}m)"

    def iniciar(self):
        """Inicia el sistema de alertas"""
        print("="*80)
        print(" SISTEMA DE ALERTAS AUTOMÁTICAS SEACE")
        print("="*80)
        print(f"\n📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        print(f"⏰ Hora actual: {datetime.now().strftime('%H:%M:%S')}")

        self.configurar_horarios()

        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """Función principal"""
    alertas = AlertasAutomaticas()

    print("\n¿Deseas ejecutar un escaneo de prueba ahora? (s/n): ", end="")
    respuesta = input().strip().lower()

    if respuesta == 's':
        print("\n🧪 Ejecutando escaneo de prueba...")
        alertas.ejecutar_escaneo()
        print("\n" + "="*80)

    print("\n🚀 Iniciando servicio de alertas automáticas...")
    print("   Presiona Ctrl+C para detener\n")

    try:
        alertas.iniciar()
    except KeyboardInterrupt:
        print("\n\n⏹️ Sistema de alertas detenido")
        print("✅ Historial guardado")

if __name__ == "__main__":
    main()
