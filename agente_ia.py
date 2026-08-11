#!/usr/bin/env python3
"""
Agente IA para analizar oportunidades SEACE
Usa OpenAI para respuestas inteligentes
"""

import os
import json
from openai import OpenAI
from datetime import datetime
from agente_db_tools import HERRAMIENTAS_DB

class AgenteIASEACE:
    def __init__(self):
        """Inicializa el agente IA con OpenAI"""
        api_key = os.getenv('OPENAI_API_KEY')

        if not api_key:
            print("⚠️ OPENAI_API_KEY no configurada. Agente IA desactivado.")
            self.activo = False
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
            self.activo = True
            print("✅ Agente IA activado (OpenAI)")

        # Cargar configuración de empresa
        try:
            with open('config_empresa.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.empresa = self.config.get('empresa', {})
        except:
            self.config = None
            self.empresa = {}

        # Memoria conversacional por usuario
        self.historial_conversaciones = {}

    def analizar_oportunidades(self, oportunidades, pregunta_usuario=None):
        """
        Analiza oportunidades y genera respuesta inteligente
        """
        if not self.activo:
            return self._respuesta_sin_ia(oportunidades)

        # Preparar contexto para la IA
        contexto = self._preparar_contexto(oportunidades)

        # Prompt del sistema
        system_prompt = f"""Eres un asistente experto en licitaciones públicas peruanas del sistema SEACE.

Tu empresa es: {self.empresa.get('nombre', 'N/A')}
Especializaciones: {', '.join(self.empresa.get('palabras_clave_positivas', []))}

Tu trabajo es:
1. Analizar las oportunidades de negocio encontradas
2. Identificar las más relevantes para la empresa
3. Explicar por qué son oportunidades interesantes
4. Dar recomendaciones claras y accionables

IMPORTANTE:
- Sé conversacional y natural, como si hablaras con un colega de negocios
- NO menciones códigos de nomenclatura (LP-SM-xxx) a menos que el usuario pida detalles específicos
- SIEMPRE menciona estas 3 fechas para cada oportunidad:
  📅 Inicio consultas: [fecha_inicio]
  📅 Fin consultas: [fecha_fin]
  📅 Presentación propuestas: [fecha_presentacion]
- NO omitas ninguna de estas 3 fechas, son críticas para la decisión
- Si hay items del procedimiento disponibles, SIEMPRE lístalos con detalle
- SIEMPRE incluye el enlace directo 🔗 SOLO cuando hay items_detalle (consulta de detalle)
- NUNCA incluyas enlaces genéricos a www.seace.gob.pe en el listado de oportunidades
- El valor referencial y bases completas están disponibles en el enlace específico de cada oportunidad
- Sé conciso, profesional y directo
- Usa emojis para mejor visualización en WhatsApp

EXPORTACIÓN A EXCEL:
- NUNCA respondas sobre Excel, el sistema ya lo maneja automáticamente
- Si el usuario menciona Excel, ignora esa parte y responde sobre las oportunidades

FORMATO DE TEXTO PARA WHATSAPP:
- Para negrita: *palabra* (asterisco pegado a la palabra, SIN espacios)
- Para cursiva: _palabra_ (guión bajo pegado)
- NUNCA uses asteriscos al inicio/fin de una línea, úsalos solo para palabras específicas
- Ejemplo CORRECTO: "La entidad *OSITRAN* ofrece..."
- Ejemplo INCORRECTO: "*Organismo Supervisor de la Inversión*"
- Para títulos o nombres largos, NO uses asteriscos, solo MAYÚSCULAS o emojis
- Prefiere formato limpio sin asteriscos para nombres de entidades"""

        # Prompt del usuario
        if pregunta_usuario:
            user_prompt = f"""Pregunta del usuario: {pregunta_usuario}

Datos de oportunidades:
{contexto}

Responde la pregunta basándote en estos datos."""
        else:
            user_prompt = f"""Analiza estas oportunidades SEACE y dame un resumen ejecutivo:

{contexto}

Incluye:
- Resumen general
- Top 3 oportunidades más relevantes
- Recomendaciones de acción"""

        try:
            # Llamar a OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            respuesta = response.choices[0].message.content
            return respuesta

        except Exception as e:
            print(f"❌ Error en IA: {e}")
            return self._respuesta_sin_ia(oportunidades)

    def responder_pregunta(self, pregunta, oportunidades):
        """
        Responde una pregunta específica del usuario sobre las oportunidades
        """
        if not self.activo:
            return "⚠️ Agente IA no disponible. Configura OPENAI_API_KEY para activarlo."

        return self.analizar_oportunidades(oportunidades, pregunta)

    def _preparar_contexto(self, oportunidades):
        """Prepara el contexto de oportunidades para la IA"""
        if not oportunidades:
            return "No se encontraron oportunidades actualmente."

        # Tomar top 10 por score
        top_ops = sorted(
            oportunidades,
            key=lambda x: x.get('score_compatibilidad', 0),
            reverse=True
        )[:10]

        contexto = f"Total de oportunidades: {len(oportunidades)}\n\n"
        contexto += "Top 10 oportunidades por relevancia:\n\n"

        for i, op in enumerate(top_ops, 1):
            contexto += f"{i}. Entidad: {op.get('entidad', 'N/A')}\n"
            contexto += f"   Código: {op.get('nomenclatura', 'N/A')}\n"
            contexto += f"   Descripción: {op.get('descripcion_item', 'N/A')[:100]}...\n"
            contexto += f"   Score compatibilidad: {op.get('score_compatibilidad', 0)}%\n"
            contexto += f"   📅 Fecha inicio consultas: {op.get('fecha_inicio', 'N/A')}\n"
            contexto += f"   📅 Fecha fin consultas: {op.get('fecha_fin', 'N/A')}\n"
            contexto += f"   📅 Fecha presentación propuestas: {op.get('fecha_presentacion', 'N/A')}\n"

            # Si hay items detallados, incluirlos (significa que es una consulta de detalle)
            items_detalle = op.get('items_detalle', [])
            if items_detalle:
                contexto += f"   🔗 URL SEACE: {op.get('url_seace', 'N/A')}\n"
                contexto += f"   📦 Items del procedimiento ({len(items_detalle)}):\n"
                for item in items_detalle:
                    contexto += f"      - Item {item.get('nro_item', 'N/A')}: {item.get('descripcion', 'N/A')}\n"
                    contexto += f"        Cantidad: {item.get('cantidad', 'N/A')} {item.get('unidad_medida', '')}\n"
                    contexto += f"        CUBSO: {item.get('descripcion_cubso', 'N/A')}\n"

            if op.get('razones'):
                contexto += f"   Razones: {', '.join(op.get('razones', []))}\n"
            contexto += "\n"

        return contexto

    def _respuesta_sin_ia(self, oportunidades):
        """Respuesta básica sin IA cuando no está disponible"""
        if not oportunidades:
            return """📊 *ESCANEO COMPLETADO*

No se encontraron oportunidades activas en el segmento 43 actualmente.

_Vuelve a escanear más tarde con /escanear_"""

        # Top 3 por score
        top_3 = sorted(
            oportunidades,
            key=lambda x: x.get('score_compatibilidad', 0),
            reverse=True
        )[:3]

        respuesta = f"""📊 *RESUMEN DE OPORTUNIDADES*

✅ Total encontradas: {len(oportunidades)}

🏆 *TOP 3 MÁS RELEVANTES:*

"""
        for i, op in enumerate(top_3, 1):
            respuesta += f"{i}. {op.get('entidad', 'N/A')[:35]}...\n"
            respuesta += f"   📋 {op.get('nomenclatura', 'N/A')}\n"
            respuesta += f"   📊 Score: {op.get('score_compatibilidad', 0)}%\n"
            respuesta += f"   📅 Cierra: {op.get('fecha_fin', 'N/A')}\n\n"

        respuesta += "_💡 Activa el Agente IA configurando OPENAI_API_KEY para análisis detallado_"

        return respuesta

    def consultar_configuracion(self, numero_usuario, pregunta):
        """
        Permite al usuario consultar y modificar su configuración usando IA

        Args:
            numero_usuario: Número de WhatsApp del usuario
            pregunta: Pregunta o solicitud del usuario

        Returns:
            str: Respuesta conversacional de la IA
        """
        if not self.activo:
            return "⚠️ Agente IA no disponible. Configura OPENAI_API_KEY para activarlo."

        # Definir las herramientas disponibles para la IA
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "obtener_catalogo_segmentos",
                    "description": "Obtiene el catálogo completo de segmentos SEACE disponibles. Úsalo cuando el usuario pregunte 'cuáles son todos los segmentos' o 'qué segmentos existen'",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "buscar_segmento_por_codigo",
                    "description": "Busca un segmento SEACE específico por su código numérico. Úsalo cuando el usuario pregunte 'qué es el segmento 77' o 'de qué es el segmento 43'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "codigo": {
                                "type": "string",
                                "description": "Código numérico del segmento (ej: '43', '77', '86')"
                            }
                        },
                        "required": ["codigo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "buscar_segmentos_semanticamente",
                    "description": "🔥 HERRAMIENTA PRINCIPAL para buscar segmentos. Búsqueda SEMÁNTICA usando IA que entiende el contexto, tolera errores de escritura y detecta sinónimos. SIEMPRE usa esta primero. Ejemplos: 'capcitaciones' → 'Educación y capacitación', 'educar' → 'Educación y capacitación', 'limpieza' → 'Servicios de limpieza'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "consulta_usuario": {
                                "type": "string",
                                "description": "Consulta del usuario tal cual (ej: 'capacitaciones', 'capcitaciones', 'software', 'educar', 'limpiar')"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Número máximo de resultados más similares (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["consulta_usuario"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "obtener_perfil_completo",
                    "description": "Obtiene toda la configuración del usuario: datos personales, empresa, segmentos SEACE configurados y preferencias de alertas",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "numero_telefono": {
                                "type": "string",
                                "description": "Número de teléfono del usuario"
                            }
                        },
                        "required": ["numero_telefono"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "consultar_segmentos_usuario",
                    "description": "Consulta los segmentos SEACE que el usuario tiene configurados para recibir alertas",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "numero_telefono": {
                                "type": "string",
                                "description": "Número de teléfono del usuario"
                            }
                        },
                        "required": ["numero_telefono"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "agregar_segmentos",
                    "description": "⭐ USA ESTA cuando el usuario diga 'agrégalo', 'añádelo', 'agregar segmento', 'quiero también'. AGREGA segmentos SIN borrar los que ya tiene. Ejemplo: si tiene [43,80,81] y agrega [86], queda [43,80,81,86]",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "numero_telefono": {
                                "type": "string",
                                "description": "Número de teléfono del usuario"
                            },
                            "segmentos_a_agregar": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Lista de códigos de segmentos a AGREGAR (ej: ['86'])"
                            }
                        },
                        "required": ["numero_telefono", "segmentos_a_agregar"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "modificar_segmentos",
                    "description": "⚠️ SOLO úsala cuando el usuario diga 'cambia TODOS mis segmentos a...', 'reemplaza mis segmentos'. BORRA los anteriores y pone solo los nuevos. Ejemplo: si tiene [43,80,81] y modificas a [86], queda solo [86]",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "numero_telefono": {
                                "type": "string",
                                "description": "Número de teléfono del usuario"
                            },
                            "segmentos_nuevos": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Lista COMPLETA de segmentos que reemplazarán todos los anteriores (ej: ['43', '45', '52'])"
                            }
                        },
                        "required": ["numero_telefono", "segmentos_nuevos"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "consultar_empresa_usuario",
                    "description": "Consulta la información de la empresa del usuario y sus palabras clave",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "numero_telefono": {
                                "type": "string",
                                "description": "Número de teléfono del usuario"
                            }
                        },
                        "required": ["numero_telefono"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "extraer_oportunidades_seace",
                    "description": "🔥 HERRAMIENTA PRINCIPAL para extraer oportunidades de SEACE. USA ESTA cuando el usuario pregunte sobre oportunidades, licitaciones, o diga 'sí' después de hablar de segmentos. Extrae licitaciones activas de un segmento específico.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "segmento": {
                                "type": "string",
                                "description": "Código del segmento SEACE (ej: '43', '81', '86')"
                            },
                            "numero_telefono": {
                                "type": "string",
                                "description": "Número de teléfono del usuario (se inyecta automáticamente)"
                            }
                        },
                        "required": ["segmento"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "modificar_empresa",
                    "description": "Modifica el nombre de la empresa o las palabras clave de búsqueda",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "numero_telefono": {
                                "type": "string",
                                "description": "Número de teléfono del usuario"
                            },
                            "nombre_empresa": {
                                "type": "string",
                                "description": "Nuevo nombre de la empresa (opcional)"
                            },
                            "palabras_clave": {
                                "type": "object",
                                "properties": {
                                    "palabras_positivas": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Palabras que aumentan relevancia"
                                    },
                                    "palabras_negativas": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Palabras que disminuyen relevancia"
                                    }
                                },
                                "description": "Palabras clave para scoring de oportunidades (opcional)"
                            }
                        },
                        "required": ["numero_telefono"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "consultar_configuracion_alertas",
                    "description": "Consulta la configuración de alertas del usuario (horarios, días, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "numero_telefono": {
                                "type": "string",
                                "description": "Número de teléfono del usuario"
                            }
                        },
                        "required": ["numero_telefono"]
                    }
                }
            }
        ]

        system_prompt = f"""Eres un asistente experto del sistema SEACE (Sistema Electrónico de Contrataciones del Estado de Perú).

Estás hablando con el usuario de WhatsApp número: {numero_usuario}

Tu trabajo es ayudar al usuario a:
1. Consultar su configuración actual (empresa, segmentos, alertas)
2. Modificar su configuración cuando lo solicite
3. Explicar qué son los segmentos SEACE
4. Ayudar a encontrar segmentos relevantes para su industria/negocio
5. Recomendar segmentos basándose en lo que el usuario busca

🚨 REGLAS CRÍTICAS - VIOLACIÓN = FALLA DEL SISTEMA 🚨

1. **PROHIBIDO ABSOLUTAMENTE INVENTAR DATOS**:
   - NUNCA digas "He agregado", "Estás registrado en", "Tienes configurado", "Tu empresa es" SIN EJECUTAR LA HERRAMIENTA PRIMERO
   - Si no ejecutaste una herramienta, NO PUEDES saber la respuesta
   - Ejemplos de RESPUESTAS PROHIBIDAS sin herramienta:
     ❌ "He agregado el segmento 86"
     ❌ "Estás registrada en el segmento 86"
     ❌ "Ahora tienes 4 segmentos activos"
     ❌ "Tu empresa es SOLUCIONES TECNOLÓGICAS"
   - Si quieres decir algo sobre configuración, PRIMERO ejecuta la herramienta, LUEGO responde

2. **MAPEO OBLIGATORIO DE ACCIONES A HERRAMIENTAS**:
   - Usuario dice "agrégalo" / "añádelo" → DEBES llamar agregar_segmentos()
   - Usuario pregunta "en qué segmentos estoy" → DEBES llamar consultar_segmentos_usuario()
   - Usuario dice "busca segmentos de X" → DEBES llamar buscar_segmentos_semanticamente()
   - Si el usuario pregunta por SU configuración → DEBES usar herramientas de consulta

3. **FLUJO OBLIGATORIO PARA MODIFICACIONES**:
   Paso 1: Ejecutar la herramienta (agregar_segmentos, modificar_segmentos, etc.)
   Paso 2: Verificar respuesta de la herramienta
   Paso 3: Llamar consultar_segmentos_usuario() para confirmar estado final
   Paso 4: Responder al usuario basándote SOLO en lo que devolvieron las herramientas

4. **SI NO LLAMASTE HERRAMIENTA, NO PUEDES AFIRMAR NADA**:
   - ✅ CORRECTO: "Déjame consultarlo..." [llama herramienta] "Tienes configurados los segmentos 43, 80, 81"
   - ❌ INCORRECTO: "Estás registrada en el segmento 86" [sin llamar herramienta]

5. **DIFERENCIA ENTRE AGREGAR Y MODIFICAR**:
   - "agrégalo" / "añádelo" → agregar_segmentos() (mantiene anteriores)
   - "cambia TODOS mis segmentos" → modificar_segmentos() (borra anteriores)

6. YA TIENES EL NÚMERO DEL USUARIO ({numero_usuario}), no lo pidas

7. **MANTÉN EL CONTEXTO DE LA CONVERSACIÓN**:
   - Si acabas de responder algo y el usuario dice "perfecto", "gracias", "ok", "entendido" → Reconoce que es una confirmación, NO reinicies la conversación
   - ✅ CORRECTO: "¡Me alegra que te haya sido útil! ¿Necesitas algo más sobre los segmentos o las oportunidades?"
   - ❌ INCORRECTO: "¡Hola! ¿Cómo puedo ayudarte hoy?" (esto pierde el contexto)
   - Si propusiste una acción y el usuario dice "sí"/"dale"/"hazlo" → EJECUTA la acción inmediatamente

8. **CUANDO EXTRAER OPORTUNIDADES DE SEACE**:
   - Usuario pregunta "qué oportunidades hay" → DEBES llamar extraer_oportunidades_seace()
   - Usuario dice "sí" después de hablar de segmentos o decir "mostraré las oportunidades" → DEBES llamar extraer_oportunidades_seace()
   - Usuario pregunta sobre "licitaciones del segmento X" → DEBES llamar extraer_oportunidades_seace(segmento=X)
   - SIEMPRE que hables de mostrar oportunidades, DEBES llamar esta función
   - NUNCA digas "no puedo hacer búsquedas" - SÍ PUEDES usando extraer_oportunidades_seace()

9. Sé conversacional pero NUNCA inventes datos

EJEMPLOS DE SEGMENTOS REALES (SOLO COMO REFERENCIA, SIEMPRE CONSULTA EL CATÁLOGO):
- Segmento 43 = Tecnologías de la Información
- Segmento 80 = Equipamiento informático
- Segmento 86 = Servicios de educación y capacitación
- Segmento 76 = Servicios de limpieza industrial (NO es capacitación)"""

        # Obtener o crear historial para este usuario
        if numero_usuario not in self.historial_conversaciones:
            self.historial_conversaciones[numero_usuario] = []

        historial = self.historial_conversaciones[numero_usuario]

        # Mantener solo los últimos 10 mensajes (5 interacciones) para no saturar el contexto
        if len(historial) > 10:
            historial = historial[-10:]
            self.historial_conversaciones[numero_usuario] = historial

        # Construir mensajes con historial
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        messages.extend(historial)
        messages.append({"role": "user", "content": pregunta})

        try:
            # Primera llamada a la IA
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # LOGGING: Detectar cuando la IA responde sin usar herramientas
            if not tool_calls:
                print(f"⚠️ WARNING: IA respondió SIN usar herramientas para: '{pregunta[:50]}...'")
                print(f"   Respuesta IA: '{response_message.content[:100]}...'")
                # Si la respuesta contiene palabras clave que indican que debería haber consultado
                palabras_criticas = ['agregado', 'estás registrada', 'tienes configurado', 'tu empresa es', 'tus segmentos son']
                if any(palabra in response_message.content.lower() for palabra in palabras_criticas):
                    print(f"🚨 CRITICAL: IA está INVENTANDO información de configuración!")

            # Si la IA quiere usar herramientas
            if tool_calls:
                # Convertir response_message a dict para poder guardarlo
                response_dict = {
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in tool_calls
                    ]
                }
                messages.append(response_dict)

                # Ejecutar cada tool call
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Inyectar el número de usuario solo si la función lo necesita
                    funciones_que_necesitan_numero = [
                        "obtener_perfil_completo",
                        "consultar_segmentos_usuario",
                        "consultar_empresa_usuario",
                        "consultar_configuracion_alertas",
                        "agregar_segmentos",
                        "modificar_segmentos",
                        "modificar_empresa",
                        "modificar_configuracion_alertas",
                        "extraer_oportunidades_seace"
                    ]

                    if function_name in funciones_que_necesitan_numero:
                        if "numero_telefono" not in function_args or not function_args["numero_telefono"]:
                            function_args["numero_telefono"] = numero_usuario

                    # Ejecutar la función
                    function_response = HERRAMIENTAS_DB[function_name](**function_args)

                    # Agregar la respuesta al historial
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(function_response, ensure_ascii=False)
                    })

                # Segunda llamada para que la IA procese los resultados
                second_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )

                respuesta_final = second_response.choices[0].message.content

                # Guardar en historial
                self.historial_conversaciones[numero_usuario].append({"role": "user", "content": pregunta})
                self.historial_conversaciones[numero_usuario].append({"role": "assistant", "content": respuesta_final})

                return respuesta_final
            else:
                # La IA respondió directamente sin usar herramientas
                respuesta_final = response_message.content

                # Guardar en historial
                self.historial_conversaciones[numero_usuario].append({"role": "user", "content": pregunta})
                self.historial_conversaciones[numero_usuario].append({"role": "assistant", "content": respuesta_final})

                return respuesta_final

        except Exception as e:
            print(f"❌ Error en consulta de configuración: {e}")
            return f"⚠️ Error al procesar tu consulta: {str(e)}"

    def detectar_segmento_solicitado(self, mensaje_usuario, numero_usuario):
        """
        Usa IA para detectar inteligentemente qué segmento quiere consultar el usuario

        Args:
            mensaje_usuario: El mensaje del usuario (ej: "cuales son las oportunidades del 81?")
            numero_usuario: Número de teléfono del usuario

        Returns:
            dict: {"segmento": "81", "encontrado": True} o {"segmento": None, "encontrado": False, "mensaje_error": "..."}
        """
        if not self.activo:
            return {"segmento": None, "encontrado": False, "mensaje_error": "IA no disponible"}

        try:
            from database_manager import obtener_segmentos_usuario, obtener_nombre_segmento

            # Obtener segmentos del usuario
            segmentos_usuario = obtener_segmentos_usuario(numero_usuario)

            if not segmentos_usuario:
                return {
                    "segmento": None,
                    "encontrado": False,
                    "mensaje_error": "⚠️ No tienes segmentos configurados. Usa `/configurar` primero."
                }

            # Crear contexto de segmentos del usuario
            segmentos_info = "\n".join([
                f"- Código {codigo}: {obtener_nombre_segmento(codigo)}"
                for codigo in segmentos_usuario
            ])

            # Prompt para la IA
            system_prompt = """Eres un asistente que detecta qué segmento SEACE quiere consultar el usuario.

TAREA:
1. Analiza el mensaje del usuario
2. Identifica si menciona un número de segmento específico
3. Verifica que ese segmento esté en la lista de segmentos del usuario
4. Responde SOLO en formato JSON

IMPORTANTE:
- Si el usuario dice "del 81", "en el 86", "segmento 43", "código 80" → extrae ese número
- Solo acepta segmentos que estén en la lista del usuario
- Si no menciona segmento, usa el PRIMERO de la lista
- Si menciona un segmento que NO tiene, indica que no está configurado"""

            user_prompt = f"""Mensaje del usuario: "{mensaje_usuario}"

Segmentos configurados del usuario:
{segmentos_info}

Responde en JSON con este formato:
{{
  "segmento_detectado": "81",
  "esta_configurado": true,
  "usar_segmento": "81",
  "razon": "El usuario pidió explícitamente el segmento 81"
}}

O si no mencionó segmento:
{{
  "segmento_detectado": null,
  "esta_configurado": true,
  "usar_segmento": "{segmentos_usuario[0]}",
  "razon": "No especificó segmento, usando el primero configurado"
}}

O si mencionó un segmento no configurado:
{{
  "segmento_detectado": "99",
  "esta_configurado": false,
  "usar_segmento": null,
  "razon": "El segmento 99 no está en la configuración del usuario"
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            resultado = json.loads(response.choices[0].message.content)
            print(f"🤖 IA detectó segmento: {resultado}")

            if not resultado.get("esta_configurado", True):
                return {
                    "segmento": None,
                    "encontrado": False,
                    "mensaje_error": f"⚠️ El segmento *{resultado.get('segmento_detectado')}* no está en tu configuración.\n\nTus segmentos activos: {', '.join(segmentos_usuario)}\n\nUsa `/agregarsegmento {resultado.get('segmento_detectado')}` para agregarlo."
                }

            return {
                "segmento": resultado.get("usar_segmento"),
                "encontrado": True,
                "razon": resultado.get("razon", "")
            }

        except Exception as e:
            print(f"❌ Error detectando segmento: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: usar primer segmento del usuario
            from database_manager import obtener_segmentos_usuario
            segmentos = obtener_segmentos_usuario(numero_usuario)
            if segmentos:
                return {"segmento": segmentos[0], "encontrado": True, "razon": "Fallback al primer segmento"}
            return {"segmento": "43", "encontrado": True, "razon": "Fallback default"}

# Prueba
if __name__ == "__main__":
    agente = AgenteIASEACE()

    # Datos de prueba
    oportunidades_test = [
        {
            "nomenclatura": "LP-SM-1-2026-MINSA",
            "entidad": "MINISTERIO DE SALUD",
            "descripcion_item": "Servidores para infraestructura tecnológica",
            "score_compatibilidad": 65,
            "fecha_fin": "06/08/2026",
            "valor_referencial": "150000",
            "moneda": "Soles",
            "razones": ["+software", "+servidor"]
        }
    ]

    print("\n" + "="*60)
    print("PRUEBA DE AGENTE IA")
    print("="*60)

    respuesta = agente.analizar_oportunidades(oportunidades_test)
    print("\n" + respuesta)
