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
from conversaciones_logger import log_conversacion
import os

# Importar el nuevo sistema directo
try:
    from whatsapp_directo_real import WhatsAppDirectoReal
    DIRECTO_DISPONIBLE = True
except ImportError:
    DIRECTO_DISPONIBLE = False

# Importar agente IA
try:
    from agente_ia import AgenteIASEACE
    IA_DISPONIBLE = True
except ImportError:
    IA_DISPONIBLE = False

class AgenteWhatsAppSEACE:
    def __init__(self):
        """Inicializa el agente conversacional"""
        self.notifier = WhatsAppNotifier()

        # Inicializar agente IA si está disponible
        if IA_DISPONIBLE:
            self.agente_ia = AgenteIASEACE()
        else:
            self.agente_ia = None

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
            '/filtrar': self.comando_filtrar,
            '/excel': self.comando_excel,
            '/configurar': self.comando_configurar,
            '/missegmentos': self.comando_mis_segmentos,
            '/agregarsegmento': self.comando_agregar_segmento
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
• /excel - Exportar TODAS a Excel
• /excel 10 - Solo top 10 a Excel
• /estado - Estado del sistema
• /ayuda - Lista completa de comandos

_Escribe cualquier comando para comenzar_"""

    def comando_escanear(self, args=""):
        """Ejecuta escaneo inmediato"""
        try:
            print("🔍 Iniciando escaneo SEACE EN TIEMPO REAL...")

            # Usar el extractor de tiempo real (API oficial)
            resultado = subprocess.run(
                ['python3', 'seace_extractor_realtime.py'],
                capture_output=True,
                text=True,
                timeout=60  # 1 minuto máximo (API rápida)
            )

            # Log de depuración
            print(f"📊 Return code: {resultado.returncode}")
            print(f"📤 STDOUT: {resultado.stdout[:500]}")
            print(f"📛 STDERR: {resultado.stderr[:500]}")

            if resultado.returncode == 0:
                # Cargar resultados
                archivos_json = [f for f in os.listdir('.') if f.startswith('seace_todas_oportunidades_') and f.endswith('.json')]
                if archivos_json:
                    archivo_mas_reciente = max(archivos_json, key=os.path.getctime)

                    with open(archivo_mas_reciente, 'r') as f:
                        data = json.load(f)

                    total = data.get('total_oportunidades', 0)
                    oportunidades = data.get('oportunidades', [])
                    relevantes = len([op for op in oportunidades if op.get('score_compatibilidad', 0) >= 25])

                    self.estado_monitor['ultimo_escaneo'] = datetime.now()
                    self.estado_monitor['total_oportunidades'] = total
                    self.estado_monitor['oportunidades_relevantes'] = relevantes

                    # Usar agente IA para análisis inteligente
                    if self.agente_ia and self.agente_ia.activo:
                        print("🤖 Generando análisis con IA...")
                        return self.agente_ia.analizar_oportunidades(oportunidades)
                    else:
                        # Respuesta básica sin IA
                        return f"""✅ *ESCANEO COMPLETADO*

🔍 *RESULTADOS:*
• Total encontradas: {total}
• Relevantes (≥25%): {relevantes}

⏰ Escaneo: {datetime.now().strftime('%H:%M:%S')}

_Usa /reporte para ver detalles completos_"""
                else:
                    return "⚠️ Escaneo completado pero no se encontró archivo de resultados"
            else:
                error_msg = resultado.stderr[:300] if resultado.stderr else resultado.stdout[:300]
                return f"❌ Error en escaneo:\n{error_msg}"

        except subprocess.TimeoutExpired:
            return "⏳ Escaneo en proceso... Puede tardar unos minutos. Usa /estado para verificar."
        except Exception as e:
            import traceback
            print(f"❌ EXCEPCIÓN en escaneo: {e}")
            print(traceback.format_exc())
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
• `/excel` - Exportar a Excel
• `/estado` - Estado del sistema

⚙️ *CONFIGURACIÓN PERSONAL:*
• `/configurar` - Seleccionar segmentos SEACE
• `/missegmentos` - Ver tus segmentos activos
• `/agregarsegmento <código>` - Agregar un segmento

📊 *ANÁLISIS Y EXPORTACIÓN:*
• `/estadisticas` - Métricas detalladas
• `/filtrar [score]` - Filtrar por score mínimo
• `/excel` - TODAS las oportunidades en Excel
• `/excel 10` - Solo top 10 en Excel
• `/excel 20` - Solo top 20 en Excel

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
• "/excel" → Envía Excel con top 10
• "¿Cuántas oportunidades hay?" → Consulta libre
• "Envíame un Excel" → El agente te enviará el archivo

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

    def comando_excel(self, args=""):
        """Genera y envía reporte Excel de oportunidades"""
        print("📊 ========== COMANDO EXCEL INICIADO ==========")
        print(f"📊 Args recibidos: '{args}'")

        try:
            from excel_generator import ExcelGeneratorSEACE
            print("📊 Módulo excel_generator importado correctamente")

            # Enviar mensaje de procesando
            self.notifier.send_message("⏳ Escaneando SEACE y generando Excel...\nEsto puede tardar unos segundos.", priority='normal')

            # ESCANEAR AUTOMÁTICAMENTE primero para tener datos frescos
            print("🔍 Escaneando SEACE para datos frescos...")
            resultado_escaneo = subprocess.run(
                ['python3', 'seace_extractor_realtime.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if resultado_escaneo.returncode != 0:
                print(f"⚠️ Error en escaneo: {resultado_escaneo.stderr[:200]}")
                return "❌ Error al escanear SEACE. Intenta de nuevo en unos segundos."

            print("✅ Escaneo completado, cargando datos...")

            # Cargar datos recién escaneados
            archivos_json = [f for f in os.listdir('.') if f.startswith('seace_todas_oportunidades_') and f.endswith('.json')]
            if not archivos_json:
                print("📊 ❌ No hay archivos JSON de oportunidades")
                return "❌ No se encontraron oportunidades. Intenta de nuevo."

            archivo_mas_reciente = max(archivos_json, key=os.path.getctime)

            with open(archivo_mas_reciente, 'r', encoding='utf-8') as f:
                data = json.load(f)

            oportunidades = data.get('oportunidades', [])

            if not oportunidades:
                return "❌ No hay oportunidades para exportar."

            generator = ExcelGeneratorSEACE()

            # Ordenar por fecha de presentación (más próximas primero)
            oportunidades_ordenadas = sorted(
                oportunidades,
                key=lambda x: x.get('fecha_presentacion', '9999-12-31')
            )

            if args.strip():
                args_lower = args.strip().lower()

                # /excel 10 - Top N oportunidades
                if args_lower.isdigit():
                    limite = int(args_lower)
                    oportunidades_exportadas = oportunidades_ordenadas[:limite]
                    excel_path = generator.generar_excel_top_relevantes(oportunidades_ordenadas, limite=limite)
                    caption = f"📊 Top {limite} Oportunidades SEACE (ordenadas por fecha de presentación)"

                else:
                    return """❌ Uso incorrecto. Opciones disponibles:

📊 *COMANDOS /excel:*
• `/excel` - TODAS las oportunidades (ordenadas por fecha)
• `/excel 10` - Solo top 10 más próximas a vencer
• `/excel 20` - Solo top 20 más próximas a vencer

_Ejemplos:_
• /excel ← Descarga completa del segmento 43
• /excel 5 ← Solo las 5 más urgentes"""
            else:
                # Por defecto: TODAS las oportunidades
                oportunidades_exportadas = oportunidades_ordenadas
                excel_path = generator.generar_excel_oportunidades(oportunidades_ordenadas)
                caption = f"📊 TODAS las oportunidades del segmento 43 ({len(oportunidades)} total)\n⏰ Ordenadas por fecha de presentación"

            print(f"📊 Intentando enviar archivo: {excel_path}")
            print(f"📊 Caption: {caption}")

            success = self.notifier.send_file_via_evolution(
                file_path=excel_path,
                caption=caption
            )

            if success:
                print("📊 ✅ Archivo enviado exitosamente!")
                alta_compatibilidad = len([op for op in oportunidades_exportadas if op.get('score_compatibilidad', 0) >= 30])
                return f"✅ Excel enviado exitosamente\n📁 {os.path.basename(excel_path)}\n📊 {len(oportunidades_exportadas)} oportunidades incluidas ({alta_compatibilidad} con compatibilidad ≥30%)"
            else:
                print("📊 ❌ Error al enviar archivo")
                return f"❌ Error enviando Excel. Archivo generado en:\n{excel_path}"

        except Exception as e:
            import traceback
            print(f"❌ Error generando Excel: {e}")
            traceback.print_exc()
            return f"❌ Error generando Excel: {str(e)[:150]}"

    def comando_configurar(self, args="", numero_usuario=None):
        """Configuración interactiva de segmentos"""
        from database_manager import obtener_catalogo_segmentos, obtener_segmentos_usuario, configurar_segmentos_usuario, obtener_usuario, agregar_usuario

        if not numero_usuario:
            return "❌ Error: No se pudo identificar el usuario"

        # Auto-registrar usuario si no existe
        usuario = obtener_usuario(numero_usuario)
        if not usuario:
            agregar_usuario(numero_usuario, "Usuario", "")
            print(f"✅ Usuario auto-registrado: {numero_usuario}")

        catalogo = obtener_catalogo_segmentos()

        if not args.strip():
            # Mostrar catálogo
            segmentos_actuales = obtener_segmentos_usuario(numero_usuario)
            segmentos_texto = '\n'.join([
                f"{'✅' if codigo in segmentos_actuales else '⬜'} *{codigo}* - {nombre}"
                for codigo, nombre in sorted(catalogo.items())
            ])

            return f"""⚙️ *CONFIGURAR SEGMENTOS*

Tus segmentos actuales: *{', '.join(segmentos_actuales)}*

*Segmentos disponibles:*
{segmentos_texto}

*Para configurar*, envía:
`/configurar 43,80,81`

_Separa los códigos con comas_
Ejemplo: `/configurar 43,45` para Tecnologías de la Información + Telecomunicaciones"""

        # Procesar configuración
        try:
            # Limpiar espacios y separar por comas
            codigos = [c.strip() for c in args.replace(' ', '').split(',') if c.strip()]
            validos = [c for c in codigos if c in catalogo]

            if not validos:
                invalidos = [c for c in codigos if c not in catalogo]
                return f"""❌ No se encontraron segmentos válidos

Códigos inválidos: {', '.join(invalidos) if invalidos else 'ninguno procesado'}

Usa `/configurar` (sin argumentos) para ver la lista completa de segmentos disponibles."""

            if configurar_segmentos_usuario(numero_usuario, validos):
                nombres = [f"*{c}* - {catalogo[c]}" for c in validos]
                return f"""✅ *Configuración actualizada*

Tus nuevos segmentos:
{chr(10).join(nombres)}

Ahora recibirás alertas de estos segmentos."""
            else:
                return "❌ Error al guardar configuración. Intenta de nuevo."

        except Exception as e:
            return f"❌ Error: {str(e)[:100]}\n\nUso: `/configurar 43,80,81`"

    def comando_mis_segmentos(self, args="", numero_usuario=None):
        """Muestra los segmentos configurados del usuario"""
        from database_manager import obtener_segmentos_usuario, obtener_nombre_segmento, obtener_usuario, agregar_usuario

        if not numero_usuario:
            return "❌ Error: No se pudo identificar el usuario"

        # Auto-registrar usuario si no existe
        usuario = obtener_usuario(numero_usuario)
        if not usuario:
            agregar_usuario(numero_usuario, "Usuario", "")

        segmentos = obtener_segmentos_usuario(numero_usuario)

        if not segmentos:
            return """⚠️ No tienes segmentos configurados

Usa `/configurar` para seleccionar tus segmentos de interés."""

        lista = '\n'.join([
            f"• *{codigo}* - {obtener_nombre_segmento(codigo)}"
            for codigo in segmentos
        ])

        return f"""📋 *TUS SEGMENTOS ACTIVOS*

{lista}

Total: {len(segmentos)} segmentos

Usa `/configurar` para modificarlos"""

    def comando_agregar_segmento(self, args="", numero_usuario=None):
        """Agrega un segmento sin reemplazar los existentes"""
        from database_manager import agregar_segmento_usuario, obtener_catalogo_segmentos, obtener_nombre_segmento, obtener_usuario, agregar_usuario

        if not numero_usuario:
            return "❌ Error: No se pudo identificar el usuario"

        # Auto-registrar usuario si no existe
        usuario = obtener_usuario(numero_usuario)
        if not usuario:
            agregar_usuario(numero_usuario, "Usuario", "")

        if not args.strip():
            return """❌ Debes especificar el código del segmento

Ejemplo: `/agregarsegmento 80`

Usa `/configurar` para ver todos los segmentos disponibles"""

        codigo = args.strip()
        catalogo = obtener_catalogo_segmentos()

        if codigo not in catalogo:
            return f"❌ Segmento *{codigo}* no encontrado\n\nUsa `/configurar` para ver la lista completa"

        if agregar_segmento_usuario(numero_usuario, codigo):
            return f"""✅ Segmento agregado

*{codigo}* - {obtener_nombre_segmento(codigo)}

Usa `/missegmentos` para ver todos tus segmentos activos"""
        else:
            return f"⚠️ El segmento *{codigo}* ya estaba en tu lista"

    def procesar_mensaje_libre(self, mensaje: str, numero_usuario=None) -> str:
        """Procesa mensajes libres usando IA para entender la intención"""
        mensaje_lower = mensaje.lower()

        # Si hay agente IA activo, usarlo para TODAS las consultas
        if self.agente_ia and self.agente_ia.activo and numero_usuario:
            # La IA decidirá si es sobre configuración, segmentos, oportunidades, etc.
            print(f"🤖 IA procesando mensaje: '{mensaje[:80]}...'")

            # Primero intentar con consulta de configuración (maneja segmentos, empresa, alertas)
            # Si la pregunta NO es sobre oportunidades/licitaciones
            palabras_oportunidades = ['oportunidad', 'licitacion', 'licitación', 'convocatoria',
                                     'concurso', 'tender', 'propuesta', 'bid']

            es_sobre_oportunidades = any(palabra in mensaje_lower for palabra in palabras_oportunidades)

            if not es_sobre_oportunidades:
                # Probablemente es sobre configuración/segmentos
                return self.agente_ia.consultar_configuracion(numero_usuario, mensaje)

        # Si hay agente IA y parece pregunta sobre oportunidades
        if self.agente_ia and self.agente_ia.activo:
            # Detectar si pide detalle de una oportunidad específica
            # Acepta: "6", "la 2", "el 4", "oportunidad 4", "detallame la 2", "háblame del 3", "dime sobre el 5"
            import re
            match_detalle = re.search(r'(?:oportunidad|detalle|detallame|información|info|mas sobre|más sobre|háblame|hablame|dime|cuéntame|cuentame|muéstrame|muestrame|ver|dame)\s+(?:sobre\s+)?(?:de\s+)?(?:la\s+)?(?:el\s+)?(?:número|numero|#)?\s*(\d+)', mensaje_lower)

            # También detectar si solo escribe un número (1-10)
            if not match_detalle and re.match(r'^\s*(\d+)\s*$', mensaje):
                numero = int(re.match(r'^\s*(\d+)\s*$', mensaje).group(1))
                if 1 <= numero <= 10:
                    match_detalle = re.match(r'^\s*(\d+)\s*$', mensaje)

            if match_detalle:
                numero_oportunidad = int(match_detalle.group(1))
                print(f"🔍 Solicitud de detalle para oportunidad #{numero_oportunidad}")

                # Cargar oportunidades
                try:
                    archivos_json = [f for f in os.listdir('.') if f.startswith('seace_todas_oportunidades_') and f.endswith('.json')]
                    if archivos_json:
                        archivo_mas_reciente = max(archivos_json, key=os.path.getctime)
                        with open(archivo_mas_reciente, 'r') as f:
                            data = json.load(f)
                        oportunidades = data.get('oportunidades', [])

                        # Buscar la oportunidad por posición en el top 10 (como la IA las numera)
                        top_ops = sorted(
                            oportunidades,
                            key=lambda x: x.get('score_compatibilidad', 0),
                            reverse=True
                        )[:10]

                        if 1 <= numero_oportunidad <= len(top_ops):
                            oportunidad = top_ops[numero_oportunidad - 1]
                        else:
                            oportunidad = None

                        if oportunidad:
                            # Obtener detalle completo con items
                            from seace_detalle import obtener_detalle_oportunidad
                            id_proc = oportunidad.get('id_procedimiento')

                            if id_proc:
                                detalle = obtener_detalle_oportunidad(id_proc)
                                if detalle:
                                    # Agregar items al contexto
                                    oportunidad['items_detalle'] = detalle.get('items', [])
                                    print(f"✅ Detalle obtenido con {len(detalle.get('items', []))} items")
                                    return self.agente_ia.responder_pregunta(mensaje, [oportunidad])

                        return f"❌ No encontré la oportunidad #{numero_oportunidad}. Usa /escanear para actualizar."
                except Exception as e:
                    print(f"⚠️ Error obteniendo detalle: {e}")
                    import traceback
                    traceback.print_exc()
                    return f"❌ Error obteniendo detalle: {str(e)[:100]}"

            # Detectar si pregunta sobre oportunidades en general
            if any(palabra in mensaje_lower for palabra in [
                'oportunidad', 'licitacion', 'licitación', 'proceso', 'convocatoria',
                'cuántas', 'cuantas', 'qué hay', 'que hay', 'mostrar', 'analiza',
                'recomiend', 'mejor', 'conveniente', 'debería', 'deberia', 'últimas',
                'ultimas', 'nuevas', 'hoy', 'mes', 'semana'
            ]):
                # Usar IA para detectar inteligentemente el segmento solicitado
                print(f"🤖 Usando IA para detectar segmento en: '{mensaje[:80]}...'")
                deteccion = self.agente_ia.detectar_segmento_solicitado(mensaje, numero_usuario)

                if not deteccion.get("encontrado"):
                    # Error: segmento no configurado o no disponible
                    return deteccion.get("mensaje_error", "❌ Error detectando segmento")

                segmento = deteccion.get("segmento")
                print(f"✅ IA detectó segmento: {segmento} - {deteccion.get('razon', '')}")

                # ESCANEAR primero para tener datos frescos
                try:
                    # Llamar al extractor directamente con el segmento
                    from seace_extractor_realtime import extraer_oportunidades_realtime
                    resultado_data = extraer_oportunidades_realtime(segmento)

                    # El resultado ya está en memoria
                    oportunidades = resultado_data.get('oportunidades', [])

                    if oportunidades:
                        print(f"🤖 Respondiendo con IA sobre {len(oportunidades)} oportunidades del segmento {segmento}: {mensaje[:50]}...")
                        return self.agente_ia.responder_pregunta(mensaje, oportunidades)
                    else:
                        return f"📊 No se encontraron oportunidades activas en el segmento {segmento}."

                except Exception as e:
                    print(f"⚠️ Error escaneando para IA: {e}")
                    import traceback
                    traceback.print_exc()
                    return f"❌ Error al buscar oportunidades: {str(e)[:100]}"

        # Si llegamos aquí y hay IA, dejar que la IA maneje el mensaje
        if self.agente_ia and self.agente_ia.activo and numero_usuario:
            return self.agente_ia.consultar_configuracion(numero_usuario, mensaje)

        # Fallback sin IA
        return f"""🤔 No entendí tu consulta: "{mensaje[:50]}..."

💡 *PUEDES USAR COMANDOS:*
• /escanear - Buscar oportunidades
• /configurar - Ver/modificar tu configuración
• /missegmentos - Ver tus segmentos activos
• /ayuda - Lista completa de comandos"""

    def procesar_comando(self, mensaje: str, numero_usuario: str = None) -> str:
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
                    # Comandos que necesitan numero_usuario
                    if comando in ['/configurar', '/missegmentos', '/agregarsegmento']:
                        respuesta = self.comandos[comando](args, numero_usuario=numero_usuario)
                    else:
                        respuesta = self.comandos[comando](args)
                except Exception as e:
                    respuesta = f"❌ Error ejecutando {comando}: {str(e)[:100]}"
            else:
                respuesta = f"❓ Comando '{comando}' no reconocido. Usa /ayuda para ver comandos disponibles."
        else:
            # Mensaje libre
            respuesta = self.procesar_mensaje_libre(mensaje, numero_usuario=numero_usuario)

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