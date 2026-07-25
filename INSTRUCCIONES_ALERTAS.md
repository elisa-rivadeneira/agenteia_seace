# Sistema de Alertas Automáticas SEACE

## 🎯 Descripción

Sistema que escanea automáticamente el portal SEACE **dos veces al día** (10am y 7pm), detecta oportunidades nuevas y envía alertas por WhatsApp al usuario.

## ⏰ Horarios Configurados

- **10:00 AM** - Escaneo matutino
- **07:00 PM** - Escaneo vespertino

## 🔔 Funcionalidades

### 1. Detección Inteligente de Novedades
- Mantiene historial de oportunidades ya vistas en `historial_oportunidades.json`
- Solo notifica oportunidades **nuevas** que no han sido reportadas antes
- Filtra por relevancia (score de compatibilidad ≥ 30%)

### 2. Notificaciones WhatsApp
- **Mensaje inicial**: Resumen con cantidad de nuevas oportunidades
- **Detalles individuales**: Hasta 5 oportunidades más relevantes
- **Información incluida**:
  - Score de compatibilidad (con emoji visual)
  - Entidad convocante
  - Descripción de la oportunidad
  - Fechas importantes (inicio, fin, presentación)
  - Enlace directo a SEACE

### 3. Formato de Alertas

```
🚨 NUEVA OPORTUNIDAD SEACE

🌟 Score de compatibilidad: 75%

Entidad:
MINISTERIO DE EDUCACIÓN

Descripción:
Adquisición de equipos informáticos y software...

📅 Fechas importantes:
• Inicio consultas: 25/07/2026 10:00
• Fin consultas: 05/08/2026 18:00
• Presentación propuestas: 10/08/2026 15:00

🔗 Ver en SEACE:
https://prod4.seace.gob.pe/openegocio/#/...

Nomenclatura: LP-SM-14-2026-XXX
```

## 🚀 Uso

### Iniciar el Sistema de Alertas

```bash
# En producción (servidor)
python3 scheduler_alertas.py
```

El sistema:
1. Se ejecutará indefinidamente
2. Escaneará automáticamente en los horarios configurados
3. Enviará alertas solo cuando haya novedades

### Test Manual

```bash
# Ejecutar escaneo de prueba inmediato
python3 test_alertas.py
```

### Integración con Docker

Agregar al `Dockerfile`:

```dockerfile
# Copiar script de alertas
COPY scheduler_alertas.py /app/

# El scheduler correrá en paralelo con el webhook server
CMD python3 webhook_server.py & python3 scheduler_alertas.py
```

## 📊 Archivos Generados

- **`historial_oportunidades.json`** - Registro de nomenclaturas ya vistas
- **`seace_todas_oportunidades_YYYYMMDD_HHMMSS.json`** - Datos completos de cada escaneo

## ⚙️ Configuración

### Variables de Entorno Necesarias

```bash
WHATSAPP_NUMBER=51967717179  # Número que recibirá las alertas
EVOLUTION_API_URL=https://...
EVOLUTION_API_KEY=...
EVOLUTION_INSTANCE_NAME=...
OPENAI_API_KEY=sk-proj-...  # Opcional, para análisis IA
```

### Personalizar Horarios

Editar `scheduler_alertas.py`:

```python
def configurar_horarios(self):
    schedule.every().day.at("10:00").do(self.ejecutar_escaneo)
    schedule.every().day.at("19:00").do(self.ejecutar_escaneo)
    # Agregar más horarios si es necesario
    # schedule.every().day.at("14:00").do(self.ejecutar_escaneo)
```

### Ajustar Filtros de Relevancia

Cambiar el threshold de compatibilidad:

```python
# En scheduler_alertas.py, línea ~120
nuevas_relevantes = [op for op in nuevas if op.get('score_compatibilidad', 0) >= 30]
# Cambiar 30 por el valor deseado (0-100)
```

### Cantidad de Alertas Enviadas

Modificar cantidad máxima:

```python
# En scheduler_alertas.py, línea ~140
for i, op in enumerate(nuevas_relevantes[:5], 1):  # Cambiar 5 por el número deseado
```

## 🔧 Troubleshooting

### El sistema no envía alertas

**Verificar:**
1. El scheduler está corriendo: `ps aux | grep scheduler_alertas`
2. Logs de ejecución: revisar salida del script
3. Evolution API está activo
4. Variables de entorno configuradas

### Recibo alertas duplicadas

- Eliminar `historial_oportunidades.json` para resetear el historial
- El sistema aprenderá nuevamente qué oportunidades ya fueron notificadas

### No detecta oportunidades nuevas

- El sistema solo notifica oportunidades con **nomenclatura única** no vista antes
- Si SEACE no publica nuevas oportunidades, el sistema reportará "0 nuevas"

### Error de timeout

- El escaneo puede tomar 30-60 segundos
- Es normal si hay muchas oportunidades
- WhatsApp tiene delay de 2-3 segundos entre mensajes para evitar spam

## 📝 Logs y Monitoreo

### Ver estado en tiempo real

```bash
# Ver logs del scheduler
tail -f /var/log/scheduler_alertas.log  # Si se configura logging

# Ver próximo escaneo programado
# Se muestra en la consola al iniciar el sistema
```

### Historial de ejecuciones

El sistema imprime en consola:
- Hora de cada escaneo
- Total de oportunidades encontradas
- Cantidad de nuevas detectadas
- Cantidad de alertas enviadas

## 🎛️ Comandos de Usuario

El usuario puede:
- Enviar `/escanear` para forzar análisis IA completo
- Enviar `/estado` para ver status del sistema
- Las alertas automáticas son **proactivas** y no requieren intervención

## 🔐 Seguridad

- El historial NO contiene datos sensibles, solo nomenclaturas
- Los mensajes se envían solo al número configurado
- No se almacenan credenciales en el código

## 📊 Estadísticas

El sistema reporta:
- Total de oportunidades escaneadas
- Nuevas vs. ya vistas
- Relevantes por score de compatibilidad
- Urgentes por fecha límite

---

**Desarrollado con:** Claude Code + Python
**Última actualización:** 2026-07-25
