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

REGLAS CRÍTICAS (DEBES SEGUIRLAS AL PIE DE LA LETRA):
1. YA TIENES EL NÚMERO DEL USUARIO ({numero_usuario}), no lo vuelvas a preguntar
2. **NUNCA JAMÁS INVENTES INFORMACIÓN**: Si no puedes consultar la base de datos, admite que tuviste un error técnico
3. **DIFERENCIA ENTRE ERROR Y NO ENCONTRADO**:
   - Si la herramienta devuelve {{"error": "..."}}, di: "Tuve un problema técnico al buscar esa información. ¿Podrías intentar de nuevo?"
   - Si la herramienta devuelve {{"total_encontrados": 0}}, di: "No encontré segmentos con esa palabra. Prueba con sinónimos o palabras relacionadas."
4. **SIEMPRE USA LAS HERRAMIENTAS** - NUNCA respondas de memoria:
   - Para buscar segmentos: usa buscar_segmentos_semanticamente()
   - Para consultar configuración del usuario: usa consultar_segmentos_usuario()
   - Para agregar segmentos: usa agregar_segmentos()
   - Para reemplazar todos los segmentos: usa modificar_segmentos()
5. **ANTES DE CONFIRMAR UNA ACCIÓN, EJECUTA LA HERRAMIENTA**:
   - ❌ MAL: "He agregado el segmento 86" (sin llamar a la función)
   - ✅ BIEN: Llamar agregar_segmentos(segmentos_a_agregar=["86"]), luego confirmar basándote en la respuesta
6. **DESPUÉS DE MODIFICAR, SIEMPRE CONSULTA PARA CONFIRMAR**:
   - Después de agregar_segmentos(), llama consultar_segmentos_usuario() para confirmar
   - Muestra al usuario los segmentos finales basándote en la consulta real
7. **DIFERENCIA ENTRE AGREGAR Y MODIFICAR**:
   - "agrégalo" / "añádelo" → agregar_segmentos() (mantiene los anteriores)
   - "cambia todos mis segmentos" → modificar_segmentos() (borra anteriores)
8. RECUERDA EL CONTEXTO: Si ya propusiste una acción y el usuario dice "sí"/"ok"/"dale", EJECUTA LA ACCIÓN inmediatamente
9. Sé conversacional, amigable y profesional
10. Usa emojis para mejor visualización en WhatsApp

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
                        "modificar_configuracion_alertas"
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
