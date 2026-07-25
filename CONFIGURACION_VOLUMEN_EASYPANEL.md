# 📁 Configuración de Volumen Persistente en Easypanel

## 🎯 Objetivo

Evitar que los datos se pierdan al hacer deploy del agente SEACE. Los archivos JSON con conversaciones, configuración de alertas e historial de oportunidades deben persistir entre despliegues.

## 📝 Archivos que se Guardarán

Estos archivos se guardarán en el volumen persistente `/data`:

```
/data/
├── conversaciones_log.json        # Historial de chats con usuarios
├── alertas_config.json            # Configuración de horarios y destinatarios
└── historial_oportunidades.json   # Oportunidades ya vistas (evita duplicados)
```

## 🔧 Configuración en Easypanel

### Paso 1: Acceder a la Configuración del Servicio

1. Ve a Easypanel → **automation** → **agente_seace**
2. Click en el botón **"Implementar"** (Deploy)
3. Busca la sección **"Puntos de montaje"** (Mount Points)

### Paso 2: Agregar Montaje de Volumen

Click en **"Agregar montaje de volumen"** y configura:

```
Tipo: Volume
Ruta del contenedor: /data
Nombre del volumen: seace_data_volume
```

### Paso 3: Configuración Detallada

**Opción 1: Volumen Named (Recomendado)**
```
Mount Type: Volume
Container Path: /data
Volume Name: seace_data_volume
Read Only: No (desmarcado)
```

**Opción 2: Bind Mount (Alternativa)**
```
Mount Type: Bind
Container Path: /data
Host Path: /var/easypanel/projects/automation/seace_data
Read Only: No (desmarcado)
```

### Paso 4: Guardar y Redesplegar

1. Click en **"Guardar"** o **"Save"**
2. Click en **"Implementar"** (Deploy/Rebuild)
3. Espera que el servicio se reinicie

## ✅ Verificación

### Verificar que el volumen está montado:

1. **Desde Easypanel Console:**
   - Ve a tu servicio → Console/Terminal
   - Ejecuta:
     ```bash
     ls -la /data
     df -h | grep /data
     ```

2. **Verificar archivos creados:**
   ```bash
   # Dentro del contenedor
   ls -lh /data/
   cat /data/conversaciones_log.json
   ```

### Verificar desde logs:

Al iniciar el servicio deberías ver en los logs:

```
📁 Directorio de datos: /data
🔧 Modo: PRODUCCIÓN
✅ Creado: /data/conversaciones_log.json
✅ Creado: /data/alertas_config.json
✅ Creado: /data/historial_oportunidades.json
```

## 🧪 Prueba de Persistencia

### Test completo:

1. **Crear datos de prueba:**
   - Envía mensajes al bot por WhatsApp
   - Configura alertas en `/admin/alertas`

2. **Verificar que se guardaron:**
   ```bash
   # En Easypanel Console
   cat /data/conversaciones_log.json
   cat /data/alertas_config.json
   ```

3. **Hacer un deploy nuevo:**
   - Haz cambios en el código
   - Push a GitHub
   - Rebuild en Easypanel

4. **Verificar que los datos siguen ahí:**
   - Los chats antiguos deben estar en `/admin`
   - Las alertas configuradas deben seguir activas

## 🔥 Troubleshooting

### Problema: Los datos se pierden al hacer deploy

**Solución:**
1. Verifica que el volumen está configurado correctamente
2. Revisa que `FLASK_ENV=production` esté configurado
3. Verifica logs al iniciar:
   ```bash
   docker logs <container_id> | grep "Directorio de datos"
   ```

### Problema: No se crean los archivos

**Solución:**
1. Verifica permisos del directorio:
   ```bash
   ls -ld /data
   chmod 777 /data  # Si hay problemas de permisos
   ```

2. Verifica que `config_paths.py` está copiado en el Dockerfile

### Problema: Error "No such file or directory"

**Solución:**
1. Asegúrate que el directorio `/data` existe en el contenedor
2. Verifica el Dockerfile tenga:
   ```dockerfile
   RUN mkdir -p /data
   VOLUME ["/data"]
   ```

## 📊 Tamaño Estimado de Datos

| Archivo | Tamaño Estimado | Frecuencia de Escritura |
|---------|----------------|-------------------------|
| conversaciones_log.json | 1-10 MB | Cada mensaje recibido |
| alertas_config.json | 5-50 KB | Solo al configurar |
| historial_oportunidades.json | 10-100 KB | 2 veces al día |

**Total estimado:** < 20 MB (después de 1 año de uso intensivo)

## 🔐 Seguridad

- ✅ Los archivos JSON NO contienen contraseñas ni API keys
- ✅ Solo contienen números de teléfono y configuraciones
- ✅ El volumen es privado del contenedor
- ⚠️ **Importante:** Hacer backups periódicos de `/data`

## 💾 Backup Manual

### Descargar backup desde Easypanel:

```bash
# Opción 1: Desde la consola de Easypanel
docker exec <container_id> tar -czf /tmp/seace_backup.tar.gz /data
docker cp <container_id>:/tmp/seace_backup.tar.gz ./seace_backup.tar.gz

# Opción 2: Usando volume
docker run --rm -v seace_data_volume:/data -v $(pwd):/backup alpine \
  tar -czf /backup/seace_backup.tar.gz /data
```

### Restaurar backup:

```bash
# Subir el archivo al servidor
# Luego desde Easypanel Console:
docker run --rm -v seace_data_volume:/data -v /path/to:/backup alpine \
  tar -xzf /backup/seace_backup.tar.gz -C /
```

## 📝 Variables de Entorno Importantes

Asegúrate que estas estén configuradas en Easypanel:

```bash
FLASK_ENV=production              # CRÍTICO para usar /data
EVOLUTION_API_URL=https://...
EVOLUTION_API_KEY=...
EVOLUTION_INSTANCE_NAME=...
OPENAI_API_KEY=sk-proj-...
WHATSAPP_NUMBER=51967717179      # Número por defecto (opcional)
```

## 🎯 Resultado Esperado

✅ **Antes del volumen:**
- Deploy → Datos perdidos ❌
- Conversaciones borradas ❌
- Alertas reseteadas ❌

✅ **Después del volumen:**
- Deploy → Datos intactos ✅
- Conversaciones preservadas ✅
- Alertas configuradas persisten ✅

---

**Desarrollado con:** Claude Code
**Fecha:** 2026-07-25
**Versión:** 2.5 (con volúmenes persistentes)
