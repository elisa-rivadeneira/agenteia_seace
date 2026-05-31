#!/usr/bin/env python3
"""
AGENTE WHATSAPP SEACE - Sistema conversacional inteligente
Permite controlar el monitoreo SEACE por WhatsApp
"""

import json
import time
import subprocess
import threading
from datetime import datetime, timedelta
from whatsapp_notifier import WhatsAppNotifier
import os

# Importar el nuevo sistema directo
try:
    from whatsapp_directo_real import WhatsAppDirectoReal
    DIRECTO_DISPONIBLE = True
except ImportError:
    DIRECTO_DISPONIBLE = False

class AgenteWhatsAppSEACE:
    def __init__(self):
        """Inicializa el agente conversacional"""
        self.notifier = WhatsAppNotifier()
        self.comandos = {
            '/escanear': self.comando_escanear,
            '/reporte': self.comando_reporte,
            '/estado': self.comando_estado,
            '/urgentes': self.comando_urgentes,
            '/config': self.comando_config,
            '/ayuda': self.comando_ayuda,
            '/inicio': self.comando_inicio,
            '/parar': self.comando_parar,
            '/estadisticas': self.comando_estadisticas,
            '/filtrar': self.comando_filtrar
        }

        self.estado_monitor = {
            'activo': True,
            'ultimo_escaneo': None,
            'total_oportunidades': 0,
            'oportunidades_relevantes': 0,
            'alertas_enviadas': 0
        }

        # Sistema de memoria de conversaciones (simple)
        self.conversaciones = []

        print("🤖 Agente WhatsApp SEACE inicializado")

    def comando_inicio(self, args=""):
        """Comando de bienvenida"""
        return f"""🤖 *AGENTE SEACE ACTIVADO*

¡Hola! Soy tu asistente inteligente para monitoreo SEACE.

📊 *SISTEMA ACTUAL:*
• Estado: {'🟢 ACTIVO' if self.estado_monitor['activo'] else '🔴 INACTIVO'}
• Empresa: {self.notifier.empresa[:30]}...
• Segmento: 43 - Tecnologías de la Información

🎯 *COMANDOS DISPONIBLES:*
• /escanear - Buscar oportunidades ahora
• /reporte - Reporte completo actual
• /urgentes - Solo oportunidades urgentes
• /estado - Estado del sistema
• /estadisticas - Métricas del monitor
• /config - Configuración actual
• /ayuda - Lista completa de comandos

_Escribe cualquier comando para comenzar_"""

    def comando_escanear(self, args=""):
        """Ejecuta escaneo inmediato"""
        try:
            # Ejecutar extractor
            resultado = subprocess.run(
                ['python3', 'seace_extractor_multipagina.py'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )

            if resultado.returncode == 0:
                # Cargar resultados
                archivos_json = [f for f in os.listdir('.') if f.startswith('seace_todas_oportunidades_') and f.endswith('.json')]
                if archivos_json:
                    archivo_mas_reciente = max(archivos_json, key=os.path.getctime)

                    with open(archivo_mas_reciente, 'r') as f:
                        data = json.load(f)

                    total = data.get('total_oportunidades', 0)
                    relevantes = len([op for op in data.get('oportunidades', []) if op.get('score_compatibilidad', 0) >= 25])

                    self.estado_monitor['ultimo_escaneo'] = datetime.now()
                    self.estado_monitor['total_oportunidades'] = total
                    self.estado_monitor['oportunidades_relevantes'] = relevantes

                    return f"""✅ *ESCANEO COMPLETADO*

🔍 *RESULTADOS:*
• Total encontradas: {total}
• Relevantes (≥25%): {relevantes}
• Archivo: {archivo_mas_reciente}

⏰ Escaneo: {datetime.now().strftime('%H:%M:%S')}

_Usa /reporte para ver detalles completos_"""
                else:
                    return "⚠️ Escaneo completado pero no se encontró archivo de resultados"
            else:
                return f"❌ Error en escaneo:\n{resultado.stderr[:200]}"

        except subprocess.TimeoutExpired:
            return "⏳ Escaneo en proceso... Puede tardar unos minutos. Usa /estado para verificar."
        except Exception as e:
            return f"❌ Error ejecutando escaneo: {str(e)[:100]}"

    def comando_reporte(self, args=""):
        """Genera reporte completo"""
        try:
            # Buscar archivo más reciente
            archivos_json = [f for f in os.listdir('.') if f.startswith('seace_todas_oportunidades_') and f.endswith('.json')]
            if not archivos_json:
                return "❌ No hay datos disponibles. Usa /escanear primero."

            archivo_mas_reciente = max(archivos_json, key=os.path.getctime)

            with open(archivo_mas_reciente, 'r') as f:
                data = json.load(f)

            oportunidades = data.get('oportunidades', [])
            total = len(oportunidades)
            relevantes = [op for op in oportunidades if op.get('score_compatibilidad', 0) >= 25]
            urgentes = [op for op in oportunidades if self._es_urgente(op.get('fecha_fin', ''))]

            # Top 5 más relevantes
            top_5 = oportunidades[:5]

            reporte = f"""📊 *REPORTE COMPLETO SEACE*
{datetime.now().strftime('%d/%m/%Y %H:%M')}

🎯 *RESUMEN EJECUTIVO:*
• Total oportunidades: {total}
• Relevantes (≥25%): {len(relevantes)}
• Urgentes (≤7 días): {len(urgentes)}

🏆 *TOP 5 MÁS COMPATIBLES:*
"""

            for i, op in enumerate(top_5, 1):
                entidad = op.get('entidad', 'N/A')[:25] + "..." if len(op.get('entidad', '')) > 25 else op.get('entidad', 'N/A')
                score = op.get('score_compatibilidad', 0)
                fecha = op.get('fecha_fin', 'N/A')[:10]

                reporte += f"{i}. {entidad}\n   Score: {score}% | Vence: {fecha}\n"

            reporte += f"\n📁 Archivo: {archivo_mas_reciente[:30]}..."
            reporte += f"\n⏰ Generado: {datetime.now().strftime('%H:%M:%S')}"

            return reporte

        except Exception as e:
            return f"❌ Error generando reporte: {str(e)[:100]}"

    def comando_urgentes(self, args=""):
        """Muestra solo oportunidades urgentes"""
        try:
            archivos_json = [f for f in os.listdir('.') if f.startswith('seace_todas_oportunidades_') and f.endswith('.json')]
            if not archivos_json:
                return "❌ No hay datos. Usa /escanear primero."

            archivo_mas_reciente = max(archivos_json, key=os.path.getctime)

            with open(archivo_mas_reciente, 'r') as f:
                data = json.load(f)

            oportunidades = data.get('oportunidades', [])
            urgentes = [op for op in oportunidades if self._es_urgente(op.get('fecha_fin', ''))]

            if not urgentes:
                return "✅ No hay oportunidades urgentes (que venzan en 7 días)"

            reporte = f"🚨 *OPORTUNIDADES URGENTES*\n(Vencen en ≤ 7 días)\n\n"

            for i, op in enumerate(urgentes[:10], 1):  # Máximo 10
                entidad = op.get('entidad', 'N/A')[:30]
                fecha = op.get('fecha_fin', 'N/A')[:10]
                score = op.get('score_compatibilidad', 0)

                dias_restantes = self._calcular_dias_restantes(op.get('fecha_fin', ''))

                reporte += f"{i}. *{entidad}*\n"
                reporte += f"   📅 Vence: {fecha} ({dias_restantes} días)\n"
                reporte += f"   📊 Score: {score}%\n\n"

            return reporte + f"Total urgentes: {len(urgentes)}"

        except Exception as e:
            return f"❌ Error: {str(e)[:100]}"

    def comando_estado(self, args=""):
        """Muestra estado del sistema"""
        ultimo_escaneo = self.estado_monitor.get('ultimo_escaneo')
        if ultimo_escaneo:
            tiempo_transcurrido = datetime.now() - ultimo_escaneo
            tiempo_str = f"{int(tiempo_transcurrido.total_seconds() / 60)} minutos"
        else:
            tiempo_str = "Nunca"

        return f"""🖥️ *ESTADO DEL SISTEMA*

🔄 *MONITOR:*
• Estado: {'🟢 ACTIVO' if self.estado_monitor['activo'] else '🔴 INACTIVO'}
• Último escaneo: {tiempo_str}
• Total encontradas: {self.estado_monitor['total_oportunidades']}
• Relevantes: {self.estado_monitor['oportunidades_relevantes']}

📱 *WHATSAPP:*
• Conexión: ✅ Funcionando
• Alertas enviadas: {self.estado_monitor['alertas_enviadas']}

⚙️ *CONFIGURACIÓN:*
• Segmento: 43 (TI)
• Intervalo: 30 minutos
• Empresa: {self.notifier.empresa[:20]}...

⏰ Estado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""

    def comando_estadisticas(self, args=""):
        """Muestra estadísticas detalladas"""
        try:
            # Buscar todos los archivos de resultados
            archivos_json = [f for f in os.listdir('.') if f.startswith('seace_todas_oportunidades_') and f.endswith('.json')]

            if not archivos_json:
                return "❌ No hay estadísticas disponibles"

            total_escaneos = len(archivos_json)
            archivo_mas_reciente = max(archivos_json, key=os.path.getctime)

            with open(archivo_mas_reciente, 'r') as f:
                data = json.load(f)

            oportunidades = data.get('oportunidades', [])

            # Análisis estadístico
            scores = [op.get('score_compatibilidad', 0) for op in oportunidades]
            score_promedio = sum(scores) / len(scores) if scores else 0

            # Entidades más frecuentes
            entidades = {}
            for op in oportunidades:
                entidad = op.get('entidad', 'N/A')
                entidades[entidad] = entidades.get(entidad, 0) + 1

            top_entidades = sorted(entidades.items(), key=lambda x: x[1], reverse=True)[:3]

            return f"""📈 *ESTADÍSTICAS DEL SISTEMA*

📊 *MÉTRICAS GENERALES:*
• Total escaneos realizados: {total_escaneos}
• Oportunidades en último escaneo: {len(oportunidades)}
• Score promedio: {score_promedio:.1f}%

🏢 *TOP ENTIDADES ACTIVAS:*
{chr(10).join([f'• {entidad[:25]}: {cantidad} procesos' for entidad, cantidad in top_entidades])}

⚡ *RENDIMIENTO:*
• Compatibilidad alta (≥50%): {len([s for s in scores if s >= 50])}
• Compatibilidad media (25-49%): {len([s for s in scores if 25 <= s < 50])}
• Compatibilidad baja (<25%): {len([s for s in scores if s < 25])}

📅 Último análisis: {datetime.now().strftime('%H:%M:%S')}"""

        except Exception as e:
            return f"❌ Error generando estadísticas: {str(e)[:100]}"

    def comando_config(self, args=""):
        """Muestra configuración actual"""
        try:
            with open('config_empresa.json', 'r') as f:
                config = json.load(f)

            empresa = config.get('empresa', {})
            notif = config.get('notificaciones', {})
            monitor = config.get('monitoreo', {})

            return f"""⚙️ *CONFIGURACIÓN ACTUAL*

🏢 *EMPRESA:*
• Nombre: {empresa.get('nombre', 'N/A')[:30]}...
• RUC: {empresa.get('ruc', 'N/A')}
• Palabras clave: {len(empresa.get('palabras_clave_positivas', []))} configuradas

📱 *NOTIFICACIONES:*
• WhatsApp: {notif.get('whatsapp', 'N/A')}
• Email: {notif.get('email', 'N/A')}

🔍 *MONITOREO:*
• Intervalo: {monitor.get('intervalo_minutos', 'N/A')} minutos
• Horario: {monitor.get('horario_inicio', 'N/A')} - {monitor.get('horario_fin', 'N/A')}
• Score mínimo: {monitor.get('score_minimo_alerta', 'N/A')}%

💰 *FILTROS:*
• Monto mínimo: S/. {empresa.get('monto_minimo', 'N/A'):,}
• Monto máximo: S/. {empresa.get('monto_maximo', 'N/A'):,}"""

        except Exception as e:
            return f"❌ Error cargando configuración: {str(e)[:100]}"

    def comando_ayuda(self, args=""):
        """Muestra ayuda completa"""
        return """📚 *GUÍA COMPLETA DEL AGENTE*

🎯 *COMANDOS PRINCIPALES:*
• `/escanear` - Buscar oportunidades ahora
• `/reporte` - Reporte completo actual
• `/urgentes` - Solo oportunidades urgentes
• `/estado` - Estado del sistema

📊 *ANÁLISIS:*
• `/estadisticas` - Métricas detalladas
• `/filtrar [score]` - Filtrar por score mínimo

⚙️ *SISTEMA:*
• `/config` - Ver configuración
• `/inicio` - Reiniciar agente
• `/ayuda` - Esta ayuda

💡 *TIPS:*
• Escribe cualquier texto para consulta libre
• Los reportes se actualizan automáticamente
• Puedes usar comandos en cualquier momento
• El sistema funciona 24/7

🤖 *EJEMPLOS:*
• "/urgentes" → Oportunidades que vencen pronto
• "/filtrar 50" → Solo oportunidades >50% score
• "¿Cuántas oportunidades hay?" → Consulta libre

_¿Tienes alguna pregunta específica?_"""

    def comando_filtrar(self, args=""):
        """Filtra oportunidades por score"""
        try:
            if not args:
                return "❓ Uso: /filtrar [score_minimo]\nEjemplo: /filtrar 30"

            score_min = int(args.strip())

            archivos_json = [f for f in os.listdir('.') if f.startswith('seace_todas_oportunidades_') and f.endswith('.json')]
            if not archivos_json:
                return "❌ No hay datos. Usa /escanear primero."

            archivo_mas_reciente = max(archivos_json, key=os.path.getctime)

            with open(archivo_mas_reciente, 'r') as f:
                data = json.load(f)

            oportunidades = data.get('oportunidades', [])
            filtradas = [op for op in oportunidades if op.get('score_compatibilidad', 0) >= score_min]

            if not filtradas:
                return f"❌ No hay oportunidades con score ≥ {score_min}%"

            reporte = f"🔍 *FILTRADO POR SCORE ≥ {score_min}%*\n\n"

            for i, op in enumerate(filtradas[:8], 1):  # Máximo 8
                entidad = op.get('entidad', 'N/A')[:25]
                score = op.get('score_compatibilidad', 0)
                fecha = op.get('fecha_fin', 'N/A')[:10]

                reporte += f"{i}. *{entidad}*\n"
                reporte += f"   📊 Score: {score}% | 📅 {fecha}\n\n"

            return reporte + f"Encontradas: {len(filtradas)}"

        except ValueError:
            return "❌ Score debe ser un número. Ejemplo: /filtrar 30"
        except Exception as e:
            return f"❌ Error: {str(e)[:100]}"

    def comando_parar(self, args=""):
        """Para el sistema"""
        self.estado_monitor['activo'] = False
        return "🔴 Sistema pausado. Usa /inicio para reactivar."

    def procesar_mensaje_libre(self, mensaje: str) -> str:
        """Procesa mensajes libres (no comandos)"""
        mensaje_lower = mensaje.lower()

        # Respuestas inteligentes básicas
        if any(palabra in mensaje_lower for palabra in ['hola', 'buenas', 'saludo']):
            return "👋 ¡Hola! Soy tu agente SEACE. Usa /ayuda para ver qué puedo hacer."

        elif any(palabra in mensaje_lower for palabra in ['oportunidades', 'cuántas', 'total']):
            return f"📊 Actualmente hay {self.estado_monitor['total_oportunidades']} oportunidades. Usa /reporte para detalles."

        elif any(palabra in mensaje_lower for palabra in ['urgente', 'urgent', 'pronto']):
            return "🚨 Para ver oportunidades urgentes usa: /urgentes"

        elif any(palabra in mensaje_lower for palabra in ['estado', 'funcionando', 'activo']):
            return self.comando_estado()

        elif any(palabra in mensaje_lower for palabra in ['ayuda', 'help', 'comandos']):
            return self.comando_ayuda()

        elif any(palabra in mensaje_lower for palabra in ['escanear', 'buscar', 'actualizar']):
            return "🔍 Para buscar nuevas oportunidades usa: /escanear"

        else:
            return f"""🤔 No entendí tu consulta: "{mensaje[:50]}..."

💡 *PUEDES PREGUNTAR:*
• "¿Cuántas oportunidades hay?"
• "Muéstrame las urgentes"
• "Estado del sistema"
• O usar comandos como /reporte, /escanear

Usa /ayuda para ver todos los comandos."""

    def procesar_comando(self, mensaje: str) -> str:
        """Procesa un mensaje y devuelve respuesta"""
        mensaje = mensaje.strip()

        # Guardar en historial
        self.conversaciones.append({
            'timestamp': datetime.now().isoformat(),
            'mensaje': mensaje,
            'tipo': 'recibido'
        })

        # Procesar comando
        if mensaje.startswith('/'):
            partes = mensaje.split(' ', 1)
            comando = partes[0].lower()
            args = partes[1] if len(partes) > 1 else ""

            if comando in self.comandos:
                try:
                    respuesta = self.comandos[comando](args)
                except Exception as e:
                    respuesta = f"❌ Error ejecutando {comando}: {str(e)[:100]}"
            else:
                respuesta = f"❓ Comando '{comando}' no reconocido. Usa /ayuda para ver comandos disponibles."
        else:
            # Mensaje libre
            respuesta = self.procesar_mensaje_libre(mensaje)

        # Guardar respuesta
        self.conversaciones.append({
            'timestamp': datetime.now().isoformat(),
            'mensaje': respuesta,
            'tipo': 'enviado'
        })

        return respuesta

    def _es_urgente(self, fecha_fin: str) -> bool:
        """Determina si una fecha es urgente (≤ 7 días)"""
        try:
            if '/' in fecha_fin:
                fecha_obj = datetime.strptime(fecha_fin[:10], '%d/%m/%Y')
            else:
                fecha_obj = datetime.strptime(fecha_fin[:10], '%Y-%m-%d')

            dias_restantes = (fecha_obj - datetime.now()).days
            return dias_restantes <= 7
        except:
            return False

    def _calcular_dias_restantes(self, fecha_fin: str) -> int:
        """Calcula días restantes hasta fecha fin"""
        try:
            if '/' in fecha_fin:
                fecha_obj = datetime.strptime(fecha_fin[:10], '%d/%m/%Y')
            else:
                fecha_obj = datetime.strptime(fecha_fin[:10], '%Y-%m-%d')

            dias = (fecha_obj - datetime.now()).days
            return max(0, dias)
        except:
            return 999

    def enviar_mensaje(self, mensaje: str) -> bool:
        """Envía mensaje por WhatsApp usando el mejor método disponible"""
        try:
            # Intentar primero el método directo si está disponible y configurado
            if DIRECTO_DISPONIBLE and os.getenv('CALLMEBOT_API_KEY'):
                whatsapp_directo = WhatsAppDirectoReal("+51967717179")
                success = whatsapp_directo.enviar_mensaje_real(mensaje)
                if success:
                    print("✅ Mensaje enviado directamente por CallMeBot")
                    self.estado_monitor['alertas_enviadas'] += 1
                    return True

            # Fallback al método original
            return self.notifier.send_message(mensaje, priority='normal')
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return False

def demo_agente():
    """Demostración del agente conversacional"""
    print("🚀 DEMO AGENTE WHATSAPP SEACE")
    print("=" * 50)

    agente = AgenteWhatsAppSEACE()

    # Comandos de prueba
    comandos_demo = [
        "/inicio",
        "/estado",
        "/escanear",
        "/reporte",
        "/urgentes",
        "¿Cuántas oportunidades hay?",
        "/ayuda"
    ]

    for comando in comandos_demo:
        print(f"\n👤 Usuario: {comando}")
        respuesta = agente.procesar_comando(comando)
        print(f"🤖 Agente: {respuesta[:200]}{'...' if len(respuesta) > 200 else ''}")
        time.sleep(1)  # Simular tiempo de respuesta

if __name__ == "__main__":
    demo_agente()