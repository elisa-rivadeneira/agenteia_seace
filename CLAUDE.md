# Agente SEACE WhatsApp - Documentación Técnica

## 📋 Descripción General

Sistema inteligente de monitoreo de oportunidades de licitaciones públicas peruanas del portal SEACE (Sistema Electrónico de Contrataciones del Estado), con integración de IA para análisis conversacional vía WhatsApp.

## 🏢 Empresa Cliente

**SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C**
- **Segmento SEACE:** 43 (Tecnologías de la Información)
- **Especializaciones:** Software, hardware, servidores, almacenamiento, bases de datos, sistemas, aplicaciones

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.11**
- **Flask 2.3.3** - Servidor webhook
- **OpenAI API (GPT-4o-mini)** - Agente IA conversacional
- **Requests** - Cliente HTTP para SEACE API

### Infraestructura
- **Docker** - Containerización
- **Easypanel** - Plataforma de despliegue (Docker Swarm)
- **Evolution API v2.3.6** - Gateway WhatsApp (Baileys)

### APIs Externas
- **SEACE API Oficial:** `https://prod4.seace.gob.pe:8086/api/oportunidades/listaProcesosCubso/codigoSegmento/43`
- **Evolution API:** `https://automation-evolution-api.gnrjtm.easypanel.host`

### Dependencias Clave
```txt
flask==2.3.3
requests==2.31.0
openai==1.54.3
httpx==0.27.2
python-dotenv==1.0.0
schedule==1.2.0
APScheduler==3.10.4
pandas==2.0.3
openpyxl==3.1.2
```

## 📁 Estructura del Proyecto

```
seace_buscador/
├── webhook_server.py              # Servidor Flask para webhooks Evolution API
├── agente_whatsapp.py             # Lógica del agente conversacional
├── agente_ia.py                   # Motor de IA con OpenAI
├── seace_extractor_realtime.py    # Extractor de datos SEACE en tiempo real
├── whatsapp_notifier.py           # Cliente WhatsApp
├── excel_generator.py             # Generador de reportes Excel
├── scheduler_alertas.py           # Sistema de alertas automáticas (10am y 7pm)
├── config_empresa.json            # Configuración de empresa y palabras clave
├── requirements.txt               # Dependencias Python
├── Dockerfile                     # Configuración Docker
├── CLAUDE.md                      # Esta documentación
└── INSTRUCCIONES_ALERTAS.md       # Documentación del sistema de alertas
```

## 🔧 Variables de Entorno

```bash
# Evolution API
EVOLUTION_API_URL=https://automation-evolution-api.gnrjtm.easypanel.host
EVOLUTION_API_KEY=5DD598ABD764-474E-BCA4-53B1AC9FD4BD
EVOLUTION_INSTANCE_NAME=service_reloaded_otronumber
WHATSAPP_NUMBER=51910364758

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Flask
FLASK_ENV=production
FLASK_PORT=5000
FLASK_HOST=0.0.0.0

# Empresa
EMPRESA_NOMBRE=SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C
SEACE_SEGMENTO=43
```

## ✨ Funcionalidades Implementadas

### 1. Extracción de Datos en Tiempo Real
- Consulta automática al API oficial de SEACE
- Extrae 32+ oportunidades activas del segmento 43
- Scoring de compatibilidad basado en palabras clave
- Almacenamiento en JSON con timestamp

### 2. Agente IA Conversacional
- **Motor:** OpenAI GPT-4o-mini
- **Capacidades:**
  - Análisis inteligente de oportunidades
  - Respuestas en lenguaje natural
  - Recomendaciones personalizadas
  - Top 3 oportunidades más relevantes

### 3. Integración WhatsApp
- **Plataforma:** Evolution API v2.3.6
- **Número:** +51 910364758
- Recepción de mensajes vía webhooks
- Respuestas automáticas asíncronas
- Soporte para mensajes conversacionales

### 4. Sistema de Alertas Automáticas ⏰ **NUEVO**
- **Horarios:** 10:00 AM y 07:00 PM (hora local)
- **Funcionamiento:**
  - Escaneo automático de SEACE 2 veces al día
  - Detección inteligente de oportunidades nuevas
  - Notificación automática vía Evolution API (WhatsApp)
  - Historial persistente para evitar duplicados
- **Filtrado:**
  - Solo alerta oportunidades con score ≥ 30%
  - Prioriza las 5 más relevantes por escaneo
  - Incluye fechas críticas y enlaces directos
- **Archivo:** `scheduler_alertas.py`
- **Documentación:** `INSTRUCCIONES_ALERTAS.md`

### 5. Exportación a Excel 📊 **NUEVO**
- **Generación automática:** Archivos Excel con oportunidades SEACE
- **Envío por WhatsApp:** Usando Evolution API endpoint `/message/sendMedia`
- **Formato:** `.xlsx` con columnas optimizadas y auto-ajuste de ancho
- **Filtros disponibles:**
  - Top N oportunidades más relevantes
  - Filtrado por score de compatibilidad
  - Reporte completo
- **Comandos:**
  - `/excel` - Top 10 oportunidades
  - `/excel 30` - Oportunidades con score ≥30%
  - `/excel top 5` - Top 5 más relevantes
- **Detección inteligente:** El agente detecta palabras como "excel", "exportar", "envíame archivo"
- **Archivo:** `excel_generator.py`

### 6. Comandos Disponibles

#### Comandos Directos
- `/escanear` - Escanea SEACE y analiza con IA
- `/reporte` - Reporte completo de oportunidades
- `/urgentes` - Oportunidades que vencen pronto
- `/excel` - Exportar a Excel y enviar archivo
- `/estadisticas` - Métricas del sistema
- `/filtrar [score]` - Filtrar por score mínimo
- `/estado` - Estado del sistema
- `/ayuda` - Lista de comandos
- `/inicio` - Mensaje de bienvenida

#### Consultas en Lenguaje Natural
El agente detecta automáticamente preguntas sobre oportunidades y ejecuta escaneo + análisis IA:
- "¿Qué oportunidades hay?"
- "Dame las últimas oportunidades"
- "¿Cuáles me recomiendas?"
- "Analiza las licitaciones del mes"
- "Dame más información de la oportunidad 4"
- "Envíame un Excel" → Ejecuta `/excel` automáticamente
- "Exporta las oportunidades" → Ejecuta `/excel` automáticamente

### 7. Características del Análisis IA

#### Información Proporcionada
✅ Nombre de la entidad
✅ Descripción de la oportunidad
✅ 📅 Fecha inicio consultas
✅ 📅 Fecha fin consultas
✅ 📅 Fecha presentación propuestas
✅ 🔗 Enlace directo a SEACE
✅ Score de compatibilidad (%)
✅ Razones de compatibilidad

#### Formato de Respuesta
- Conversacional y natural
- Formato WhatsApp (negritas con `*texto*`)
- Sin códigos de nomenclatura innecesarios
- Emojis para mejor visualización
- Recomendaciones accionables

## 🔄 Flujo de Operación

1. **Usuario envía mensaje** → WhatsApp
2. **Evolution API** → Webhook a Flask Server
3. **Webhook Server** → Procesa con `agente_whatsapp.py`
4. **Detección de intención:**
   - Si pregunta sobre oportunidades → Ejecuta extractor SEACE
   - Carga datos JSON generados
   - Envía contexto a `agente_ia.py`
5. **Agente IA** → Analiza con GPT-4o-mini
6. **Respuesta** → Envía vía Evolution API → WhatsApp

## 📊 Algoritmo de Scoring

```python
score = 0
# Palabras positivas: +5 puntos cada una
# Palabras negativas: -10 puntos cada una
# Score final: max(0, min(100, score))
```

**Palabras Clave Positivas:**
- software, hardware, servidor, tecnología, sistema
- aplicación, desarrollo, base de datos

**Palabras Clave Negativas:**
- construcción, obra civil, infraestructura física

## 🌐 Endpoint SEACE

```bash
GET https://prod4.seace.gob.pe:8086/api/oportunidades/listaProcesosCubso/codigoSegmento/43

Headers:
  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0
  Accept: application/json, text/plain, */*
  Referer: https://prod4.seace.gob.pe/openegocio/
```

**Respuesta:** Array de oportunidades con 20+ campos por item

## 🔗 URL de Oportunidades

Formato: `https://prod4.seace.gob.pe/openegocio/#/busqueda-por-item?numeroProcesoItem={nomenclatura}`

Ejemplo: `https://prod4.seace.gob.pe/openegocio/#/busqueda-por-item?numeroProcesoItem=LP-SM-14-2026-BCRPLIM-1`

## 🚀 Despliegue

### Producción (Easypanel)
1. Push a GitHub → `main` branch
2. Easypanel auto-deploy desde GitHub
3. Rebuild en Easypanel UI
4. Servicio disponible en: `https://automation-agente-seace.gnrjtm.easypanel.host`

### Local (Desarrollo)
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export OPENAI_API_KEY=sk-proj-...

# Modo chat interactivo
python3 chat_local.py

# Servidor webhook
python3 webhook_server.py

# Sistema de alertas automáticas
python3 scheduler_alertas.py
```

### Producción con Alertas Automáticas
Para activar las alertas en el servidor, el Dockerfile debe ejecutar **ambos** servicios:

```dockerfile
# Ejecutar webhook server y sistema de alertas en paralelo
CMD python3 webhook_server.py & python3 scheduler_alertas.py
```

O usar un proceso supervisor (recomendado para producción).

## 🧪 Testing

### Test Local del Agente
```bash
python3 chat_local.py
```

### Test del Extractor
```bash
python3 seace_extractor_realtime.py
```

### Test del Agente IA
```bash
python3 agente_ia.py
```

### Test del Sistema de Alertas
```bash
# Test con escaneo inmediato
python3 test_alertas.py

# Ver próximos horarios programados
python3 scheduler_alertas.py
```

### Test del Generador de Excel
```bash
# Generar reportes Excel de prueba
python3 excel_generator.py

# Ver archivos generados
ls -lh reportes_excel/
```

### Ver Logs de Producción
```bash
# SSH al servidor
docker logs -f $(docker ps -q --filter "name=seace" | head -1)

# Filtrar por errores
docker logs --tail 500 $(docker ps | grep -i seace | awk '{print $1}') | grep -E "(ERROR|Inicializando|agente|IA)"
```

## ⚠️ Limitaciones Conocidas

1. **Valor Referencial:** El API de SEACE devuelve `"---"` en el campo `valorReferencialItem`. El valor completo solo está disponible en las bases integradas (PDF) dentro del portal SEACE.

2. **Rate Limiting:** El API oficial de SEACE no tiene rate limits documentados, pero se recomienda no hacer más de 1 request por minuto.

3. **Datos en Tiempo Real:** Los datos se obtienen en tiempo real del API, pero SEACE actualiza su información según su calendario oficial.

## 🐛 Troubleshooting

### Agente no responde
1. Verificar logs: `docker logs [container_id]`
2. Verificar `OPENAI_API_KEY` está configurada
3. Verificar Evolution API está activo

### Error de dependencias
```bash
# Reinstalar con versiones específicas
docker exec -it [container_id] pip install --force-reinstall --no-cache-dir openai==1.54.3 httpx==0.27.2
docker restart [container_id]
```

### Webhook no recibe mensajes
1. Verificar webhook URL en Evolution API
2. Verificar instance name coincide
3. Revisar logs de Evolution API

## 📝 Commits y Despliegue

### Comandos Git
```bash
# Verificar estado
git status

# Agregar cambios
git add .

# Commit
git commit -m "Descripción del cambio"

# Push a producción
git push origin main
```

### Después del Push
1. Ir a Easypanel
2. Seleccionar servicio "automation-agente-seace"
3. Click en "Rebuild"
4. Esperar deployment
5. Verificar logs

## 👥 Equipo

- **Desarrollo:** Claude Code + Elisa Rivadeneira
- **Infraestructura:** Easypanel (Docker Swarm)
- **Cliente:** SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C

## 📅 Historial de Versiones

- **v1.0** - Sistema básico con extractor y comandos
- **v2.0** - Integración OpenAI GPT-4o-mini
- **v2.1** - Escaneo automático proactivo
- **v2.2** - Corrección formato WhatsApp markdown
- **v2.3** - Links directos a SEACE
- **v2.4** - Optimización de prompts y fechas críticas
- **v2.5** - Sistema de alertas automáticas (10am y 7pm) con detección de oportunidades nuevas
- **v2.6** - Exportación a Excel y envío por WhatsApp vía Evolution API

## 🔐 Seguridad

- API keys en variables de entorno
- No se almacenan credenciales en código
- HTTPS para todas las comunicaciones
- Validación de webhooks de Evolution API

## 📞 Contacto en Producción

**WhatsApp del Bot:** +51 910364758

Envía cualquier mensaje o comando para interactuar con el agente IA.

---

**Última actualización:** 2026-07-24
**Generado con:** Claude Code
**Repositorio:** https://github.com/elisa-rivadeneira/agenteia_seace
