# 🤖 AGENTE WHATSAPP SEACE - MANUAL DE USO

## ✅ SISTEMA COMPLETAMENTE OPERATIVO

Tu agente conversacional SEACE está **100% funcional** y listo para usar.

---

## 🚀 INICIO RÁPIDO

### 1. ACTIVAR EL AGENTE
```bash
python3 activar_agente.py
# Cuando se abra WhatsApp Web, HAZ CLIC EN ENVIAR
```

### 2. COMANDOS DISPONIBLES POR WHATSAPP

Una vez activado, puedes enviar estos comandos **directamente a tu WhatsApp**:

#### 📊 **COMANDOS PRINCIPALES:**
- `/escanear` - Busca nuevas oportunidades AHORA
- `/reporte` - Reporte completo del último escaneo
- `/urgentes` - Solo oportunidades que vencen pronto
- `/estado` - Estado actual del sistema

#### 🔍 **ANÁLISIS:**
- `/estadisticas` - Métricas detalladas del sistema
- `/filtrar 50` - Filtrar oportunidades por score (ej: ≥50%)
- `/config` - Ver configuración actual

#### 💬 **CONVERSACIÓN NATURAL:**
- "¿Cuántas oportunidades hay?"
- "Muéstrame las urgentes"
- "Estado del sistema"
- "¿Hay algo nuevo?"

#### ⚙️ **CONTROL:**
- `/ayuda` - Lista completa de comandos
- `/inicio` - Reiniciar agente
- `/parar` - Pausar sistema

---

## 🎯 EJEMPLOS DE USO

### **Scenario 1: Consulta Rápida**
```
👤 Tú: /estado
🤖 Agente: 🖥️ ESTADO DEL SISTEMA
          🔄 MONITOR: ✅ ACTIVO
          📱 WHATSAPP: ✅ Funcionando
          ⏰ Último escaneo: 15 minutos
```

### **Scenario 2: Buscar Oportunidades**
```
👤 Tú: /escanear
🤖 Agente: ✅ ESCANEO COMPLETADO
          🔍 Total encontradas: 30
          📊 Relevantes (≥25%): 6
          ⏰ Escaneo: 10:55:23
```

### **Scenario 3: Consulta Natural**
```
👤 Tú: ¿Hay oportunidades urgentes?
🤖 Agente: 🚨 Para ver oportunidades urgentes usa: /urgentes
```

### **Scenario 4: Reporte Completo**
```
👤 Tú: /reporte
🤖 Agente: 📊 REPORTE COMPLETO SEACE
          🎯 Total: 30 oportunidades
          🏆 TOP 5 MÁS COMPATIBLES:
          1. MUNICIPALIDAD DE LA MOLINA...
```

---

## 🔄 MONITOREO AUTOMÁTICO

### **Opción 1: Manual (Recomendado para pruebas)**
- Envías comandos cuando quieras
- El agente responde inmediatamente
- Control total sobre cuándo usar

### **Opción 2: Monitor Automático** ⚠️
```bash
python3 monitor_whatsapp.py
```
- **RESPONDE AUTOMÁTICAMENTE** a TODOS tus mensajes
- Mantiene WhatsApp Web abierto
- Para usuarios avanzados

---

## 📁 ARCHIVOS DEL SISTEMA

### **Principales:**
- `agente_whatsapp.py` - Cerebro del agente conversacional
- `activar_agente.py` - Script de activación simple
- `whatsapp_notifier.py` - Sistema de envío de mensajes
- `seace_extractor_multipagina.py` - Motor de búsqueda SEACE

### **Configuración:**
- `config_empresa.json` - Configuración principal
- `whatsapp_config.json` - Configuración de WhatsApp

### **De prueba:**
- `prueba_simple.py` - Pruebas básicas
- `verificar_whatsapp.py` - Verificar configuración

---

## 🔧 CONFIGURACIÓN ACTUAL

```json
{
  "empresa": "SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C",
  "whatsapp": "+51967717179",
  "segmento": "43 - Tecnologías de la Información",
  "método": "WhatsApp Auto Selenium",
  "estado": "✅ OPERATIVO"
}
```

---

## 💡 CONSEJOS DE USO

### **Para mejores resultados:**
1. **Envía comandos claros**: `/escanear`, `/reporte`, `/urgentes`
2. **Usa preguntas naturales**: "¿Cuántas oportunidades hay?"
3. **Espera respuesta** antes del siguiente comando
4. **Usa /ayuda** si olvidas comandos

### **Comandos más útiles:**
- **Inicio del día**: `/estado` → `/escanear` → `/reporte`
- **Durante el día**: `/urgentes` → `/filtrar 40`
- **Final del día**: `/estadisticas`

### **Para monitoreo automático:**
- Ejecuta `/escanear` cada 30-60 minutos
- Usa `/urgentes` para alertas críticas
- Revisa `/estadisticas` semanalmente

---

## 🚨 ALERTAS Y NOTIFICACIONES

El agente detecta automáticamente:
- ✅ **Nuevas oportunidades** en cada escaneo
- 🔥 **Oportunidades urgentes** (vencen en ≤7 días)
- 📊 **Alta compatibilidad** (score ≥50%)
- ⚠️ **Cambios en el sistema**

---

## 🔗 INTEGRACIÓN COMPLETA

### **Flujo automático recomendado:**
1. **Cron job** ejecuta escaneo cada 30 min
2. **Agente analiza** nuevas oportunidades
3. **Envía alertas** solo si hay algo relevante
4. **Tú recibes** notificación en WhatsApp
5. **Respondes** con comandos para más detalles

### **Script de automatización:**
```bash
# Cada 30 minutos
*/30 * * * * cd /ruta/seace_buscador && python3 seace_extractor_multipagina.py

# Si hay oportunidades relevantes, enviar alerta
*/35 * * * * cd /ruta/seace_buscador && python3 -c "
from agente_whatsapp import AgenteWhatsAppSEACE
import json, os
archivos = [f for f in os.listdir('.') if f.startswith('seace_todas_')]
if archivos:
    archivo = max(archivos, key=os.path.getctime)
    with open(archivo) as f:
        data = json.load(f)
    relevantes = [op for op in data['oportunidades'] if op.get('score_compatibilidad', 0) >= 40]
    if relevantes:
        agente = AgenteWhatsAppSEACE()
        mensaje = f'🚨 ALERTA: {len(relevantes)} oportunidades relevantes detectadas. Usa /reporte para detalles.'
        agente.enviar_mensaje(mensaje)
"
```

---

## 🎉 ¡SISTEMA COMPLETAMENTE OPERATIVO!

Tu agente WhatsApp SEACE está **listo para usar**. Solo necesitas:

1. **Ejecutar**: `python3 activar_agente.py`
2. **Hacer clic** en ENVIAR cuando se abra WhatsApp Web
3. **Enviar comandos** directamente por WhatsApp
4. **Recibir respuestas** automáticas del agente

**¡Ya tienes tu asistente personal SEACE funcionando al 100%!** 🚀