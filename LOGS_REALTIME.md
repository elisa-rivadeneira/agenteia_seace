# 📊 Guía: Ver Logs de Docker en Tiempo Real

## 🎯 Objetivo

Ver los logs del contenedor del bot SEACE mientras está ejecutándose, para debugging y monitoreo en vivo.

---

## 🔍 Paso 1: Identificar el Contenedor Correcto

### Opción A: Ver todos los contenedores en ejecución
```bash
docker ps
```

**Busca la columna `NAMES` o `IMAGE`** que contenga "seace" o el nombre de tu app.

**Ejemplo de salida:**
```
CONTAINER ID   IMAGE                    NAMES
b79e4f88edfb   seace_monitor:latest     automation-agente-seace
ad8fd63130e7   nginx:alpine             proxy-server
```

✅ **Copia el CONTAINER ID** (ejemplo: `b79e4f88edfb`)

### Opción B: Filtrar directamente por nombre
```bash
docker ps --filter "name=seace"
```

### Opción C: Usar variable para detectar automáticamente
```bash
# Detectar automáticamente el contenedor por nombre
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)
echo "Contenedor detectado: $CONTAINER_ID"
```

---

## 📺 Paso 2: Ver Logs en Tiempo Real

### 🔥 Método 1: `docker logs -f` (Recomendado)

**Con variable (más fácil y portátil):**
```bash
# Definir la variable una vez
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)

# Ver logs en tiempo real
docker logs -f $CONTAINER_ID
```

**Opciones útiles:**
```bash
# Ver solo las últimas 100 líneas + seguir
docker logs -f --tail 100 $CONTAINER_ID

# Ver solo desde los últimos 10 minutos
docker logs -f --since 10m $CONTAINER_ID

# Ver con timestamps
docker logs -f -t $CONTAINER_ID
```

**Cómo salir:**
- Presiona `Ctrl + C` para detener la visualización (el contenedor sigue corriendo)

---

### 🔄 Método 2: `watch` (Actualización automática cada N segundos)

Útil si `docker logs -f` se desconecta:

```bash
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)
watch -n 2 "docker logs --tail 50 $CONTAINER_ID"
```

- `-n 2`: Actualiza cada 2 segundos
- `--tail 50`: Muestra las últimas 50 líneas

**Cómo salir:**
- Presiona `Ctrl + C`

---

### 🎭 Método 3: Segunda terminal SSH (Más cómodo)

1. **Terminal 1:** Deja corriendo `docker logs -f`
   ```bash
   CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)
   docker logs -f --tail 100 $CONTAINER_ID
   ```

2. **Terminal 2:** Haz pruebas enviando mensajes al bot por WhatsApp

De esta forma ves en tiempo real cómo responde el sistema.

---

## 🔎 Paso 3: Filtrar Logs (Buscar cosas específicas)

```bash
# Definir variable primero
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)
```

### Ver solo errores
```bash
docker logs -f $CONTAINER_ID 2>&1 | grep -E "(ERROR|CRITICAL|Exception)"
```

### Ver solo conversaciones del agente IA
```bash
docker logs -f $CONTAINER_ID 2>&1 | grep -E "(🤖|agente|IA|Respondiendo)"
```

### Ver solo llamadas a herramientas
```bash
docker logs -f $CONTAINER_ID 2>&1 | grep -E "(🔧|Ejecutando|Herramienta)"
```

### Ver advertencias de hallucination
```bash
docker logs -f $CONTAINER_ID 2>&1 | grep -E "(⚠️|WARNING|CRITICAL)"
```

---

## ⚡ Atajos Rápidos (Aliases)

Agrega estos a tu `~/.bashrc` para acceso rápido:

```bash
# Ver logs del contenedor SEACE
alias seace-logs='docker logs -f --tail 100 $(docker ps -q --filter "name=seace" | head -1)'

# Ver solo errores
alias seace-errors='docker logs -f $(docker ps -q --filter "name=seace" | head -1) 2>&1 | grep -E "(ERROR|CRITICAL)"'

# Ver últimas 200 líneas
alias seace-recent='docker logs --tail 200 $(docker ps -q --filter "name=seace" | head -1)'
```

**Activar cambios:**
```bash
source ~/.bashrc
```

**Usar:**
```bash
seace-logs
seace-errors
seace-recent
```

---

## 🐛 Troubleshooting

### ❌ Problema: "docker logs -f" se sale inmediatamente

**Posibles causas:**
1. El contenedor ya no está corriendo
   ```bash
   docker ps -a  # Ver todos los contenedores (incluso detenidos)
   ```

2. El container ID está mal
   ```bash
   docker ps  # Verificar el ID correcto
   ```

---

### ❌ Problema: Los logs están atrasados (no aparecen inmediatamente)

**Causa:** Python buffering en stdout/stderr

**Solución:** Verifica que el Dockerfile tenga:
```dockerfile
ENV PYTHONUNBUFFERED=1
```

**Verificar si está configurado:**
```bash
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)
docker exec $CONTAINER_ID env | grep PYTHONUNBUFFERED
```

**Si no aparece:** Rebuild del contenedor con la variable de entorno.

---

### ❌ Problema: Logs muy largos, difícil de leer

**Solución 1:** Usa `--tail` para limitar líneas
```bash
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)
docker logs -f --tail 50 $CONTAINER_ID
```

**Solución 2:** Usa `less` para navegar
```bash
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)
docker logs $CONTAINER_ID | less
```
- `Espacio`: Siguiente página
- `b`: Página anterior
- `/texto`: Buscar texto
- `q`: Salir

---

### ❌ Problema: Quiero ver logs de hace 1 hora

```bash
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)
docker logs --since 1h $CONTAINER_ID
```

**Otras opciones:**
- `--since 30m`: Últimos 30 minutos
- `--since 2h`: Últimas 2 horas
- `--since 2024-08-10T20:00:00`: Desde fecha específica

---

## 📋 Resumen de Comandos Más Usados

**Primero definir la variable:**
```bash
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)
```

**Luego usar los comandos:**

| Comando | Descripción |
|---------|-------------|
| `docker ps` | Ver contenedores activos |
| `docker logs -f $CONTAINER_ID` | Ver logs en tiempo real |
| `docker logs -f --tail 100 $CONTAINER_ID` | Últimas 100 líneas + seguir |
| `docker logs --since 10m $CONTAINER_ID` | Solo últimos 10 minutos |
| `docker logs $CONTAINER_ID \| grep "ERROR"` | Filtrar por palabra clave |
| `Ctrl + C` | Salir de logs (contenedor sigue corriendo) |

---

## 🎓 Ejemplo Completo de Sesión de Debugging

```bash
# 1. Conectar por SSH al servidor
ssh usuario@servidor

# 2. Definir variable del contenedor
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)

# 3. Verificar que se detectó correctamente
echo "Contenedor: $CONTAINER_ID"

# 4. Ver logs en tiempo real
docker logs -f --tail 100 $CONTAINER_ID

# 5. En otra terminal SSH (o en WhatsApp), enviar mensaje al bot
# Ejemplo: "Qué oportunidades hay en el segmento 86?"

# 6. Ver en la primera terminal cómo se procesan los logs:
# - 📥 Webhook recibido
# - 🔍 Mensaje detectado
# - 🤖 Agente IA analizando
# - 🔧 Herramienta ejecutada
# - ✅ Respuesta enviada

# 7. Si detectas un error, filtrar:
docker logs -f $CONTAINER_ID 2>&1 | grep -E "(ERROR|Exception|Traceback)"

# 8. Salir con Ctrl + C
```

---

## 🚀 Tip Pro: Logs Persistentes

Para guardar logs en un archivo mientras los ves en tiempo real:

```bash
CONTAINER_ID=$(docker ps --filter "name=agente_seace" --format "{{.ID}}" | head -1)
docker logs -f $CONTAINER_ID | tee seace_debug_$(date +%Y%m%d_%H%M%S).log
```

Esto guarda **todo** en un archivo `.log` y además lo muestra en pantalla.

---

**Última actualización:** 2026-08-11
**Generado con:** Claude Code
**Para:** Debugging del bot SEACE WhatsApp
