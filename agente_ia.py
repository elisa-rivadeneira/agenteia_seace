#!/usr/bin/env python3
"""
Agente IA para analizar oportunidades SEACE
Usa OpenAI para respuestas inteligentes
"""

import os
import json
from openai import OpenAI
from datetime import datetime

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
- SIEMPRE incluye el enlace directo 🔗 cuando el usuario pida más información específica
- El valor referencial y bases completas están disponibles en el enlace de SEACE
- Sé conciso, profesional y directo
- Usa emojis para mejor visualización en WhatsApp

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
            contexto += f"   🔗 URL SEACE: {op.get('url_seace', 'N/A')}\n"
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
