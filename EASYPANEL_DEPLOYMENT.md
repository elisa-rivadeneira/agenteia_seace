# 🚀 Deployment a Easypanel

Guía completa para desplegar el Agente SEACE WhatsApp en Easypanel.

## 📋 Pre-requisitos

- Cuenta en Easypanel
- Evolution API ya configurado en Easypanel (mismo servidor)
- Repositorio en GitHub
- API Key y nombre de instancia de Evolution API

## 🔧 Paso 1: Configurar GitHub

```bash
# 1. Agregar remote si no existe
git remote add origin https://github.com/tu-usuario/seace_buscador.git

# 2. Push a GitHub
git push -u origin main
```

## 🐳 Paso 2: Crear App en Easypanel

### 2.1 Crear nueva aplicación
1. En Easypanel, click en "Create" > "App"
2. Nombre: `seace-whatsapp-agent`
3. Seleccionar fuente: **GitHub**

### 2.2 Configurar GitHub Source
- **Repository**: `tu-usuario/seace_buscador`
- **Branch**: `main`
- **Build Method**: `Dockerfile`
- **Dockerfile Path**: `./Dockerfile`

### 2.3 Configurar Build
- **Port**: `5000`
- **Health Check Path**: `/status`

## ⚙️ Paso 3: Variables de Entorno

Agregar en Easypanel > App Settings > Environment Variables:

```env
EVOLUTION_API_URL=https://automation-evolution-api.gnrjtm.easypanel.host
EVOLUTION_API_KEY=tu_api_key_real
EVOLUTION_INSTANCE_NAME=tu_instancia_real
WHATSAPP_NUMBER=+51967717179
FLASK_ENV=production
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
EMPRESA_NOMBRE=SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C
SEACE_SEGMENTO=43
```

## 🌐 Paso 4: Configurar Dominio

### 4.1 En Easypanel
1. Ir a **Domains** en tu app
2. Agregar dominio personalizado o usar el subdominio de Easypanel
3. Ejemplo: `seace-agent.easypanel.host`

### 4.2 Obtener URL del Webhook
Tu webhook será: `https://seace-agent.easypanel.host/webhook`

## 🔗 Paso 5: Configurar Webhook en Evolution API

### Opción A: Usando la UI de Evolution API
1. Acceder a tu Evolution API
2. Ir a la instancia configurada
3. En **Webhooks**, agregar:
   - **URL**: `https://seace-agent.easypanel.host/webhook`
   - **Events**: `messages.upsert`
   - **Method**: `POST`

### Opción B: Usando API
```bash
curl -X POST https://automation-evolution-api.gnrjtm.easypanel.host/webhook/set/tu_instancia \
  -H 'apikey: TU_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://seace-agent.easypanel.host/webhook",
    "webhook_by_events": true,
    "webhook_base64": false,
    "events": [
      "messages.upsert"
    ]
  }'
```

## ✅ Paso 6: Deploy

1. En Easypanel, click en **Deploy**
2. Esperar que el build termine (2-5 minutos)
3. Verificar logs para errores

## 🧪 Paso 7: Probar el Sistema

### 7.1 Verificar Health
```bash
curl https://seace-agent.easypanel.host/status
```

Debe retornar:
```json
{
  "status": "running",
  "agente_activo": true,
  "mensajes_recibidos": 0
}
```

### 7.2 Probar WhatsApp
Envía un mensaje a tu número WhatsApp configurado:
```
/estado
```

Deberías recibir respuesta automática del agente.

### 7.3 Ver logs en Easypanel
```
🚀 INICIANDO WEBHOOK SERVER PARA EVOLUTION API
🤖 Agente SEACE inicializado
🌐 Servidor webhook corriendo en: http://0.0.0.0:5000/webhook
```

## 🔍 Endpoints Disponibles

- `GET /status` - Estado del sistema
- `POST /webhook` - Recibir mensajes de Evolution API
- `GET /messages` - Ver últimos mensajes recibidos
- `POST /send` - Enviar mensaje manual (testing)

## 🛠️ Troubleshooting

### Problema: Webhook no recibe mensajes
**Solución**: Verificar que Evolution API tenga configurada la URL correcta

```bash
# Ver configuración actual de webhook
curl https://automation-evolution-api.gnrjtm.easypanel.host/webhook/find/tu_instancia \
  -H 'apikey: TU_API_KEY'
```

### Problema: Build falla
**Solución**: Verificar logs en Easypanel y asegurarte que todos los archivos necesarios estén en el repo:
- `webhook_server.py`
- `agente_whatsapp.py`
- `whatsapp_notifier.py`
- `seace_extractor_multipagina.py`
- `config_empresa.json`

### Problema: Evolution API no conecta
**Solución**: Verificar variables de entorno:
- `EVOLUTION_API_URL` debe apuntar a la URL correcta
- `EVOLUTION_API_KEY` debe ser válida
- `EVOLUTION_INSTANCE_NAME` debe existir en Evolution API

## 📊 Monitoreo

### Ver logs en tiempo real
En Easypanel: App > Logs

### Verificar mensajes recibidos
```bash
curl https://seace-agent.easypanel.host/messages
```

### Comandos disponibles vía WhatsApp
- `/estado` - Estado del sistema
- `/escanear` - Buscar oportunidades
- `/urgentes` - Oportunidades urgentes
- `/reporte` - Reporte completo
- `/ayuda` - Lista de comandos

## 🔄 Actualizar Deployment

```bash
# 1. Hacer cambios en código local
git add .
git commit -m "Descripción de cambios"
git push origin main

# 2. En Easypanel, hacer Re-deploy automático o manual
```

## 🔐 Seguridad

- ✅ `.env` está en `.gitignore` (no se sube a GitHub)
- ✅ API Keys se configuran en Easypanel
- ✅ Solo expone endpoints necesarios
- ✅ Health check configurado

## 📝 Notas Importantes

1. **Persistencia**: Los datos se guardan en volumen Docker
2. **Restart Policy**: `unless-stopped` - se reinicia automáticamente
3. **Health Checks**: Cada 30s verifica que el servicio esté activo
4. **Logs**: Accesibles desde Easypanel UI
5. **Evolution API**: Debe estar en la misma red o accesible públicamente

## 🎯 Checklist Final

- [ ] Código subido a GitHub
- [ ] App creada en Easypanel
- [ ] Variables de entorno configuradas
- [ ] Dominio configurado
- [ ] Webhook configurado en Evolution API
- [ ] Deploy exitoso
- [ ] Health check pasa
- [ ] Prueba de mensaje WhatsApp funciona
- [ ] Logs muestran actividad correcta

¡Listo! Tu agente SEACE debería estar funcionando en producción. 🎉
