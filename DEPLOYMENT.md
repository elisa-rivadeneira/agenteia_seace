# 🚀 Deployment Guide - Easypanel

## Pasos para deployar en VPS con Easypanel

### 1. Preparar Repositorio
```bash
git remote add origin https://github.com/tu-usuario/seace-agent.git
git push -u origin main
```

### 2. En Easypanel (VPS)

1. **Crear nueva aplicación**
   - Tipo: Docker
   - Fuente: GitHub Repository
   - Repository: tu-usuario/seace-agent

2. **Configurar variables de entorno**
   ```
   EVOLUTION_API_URL=https://automation-evolution-api.gnrjtm.easypanel.host
   EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
   EVOLUTION_INSTANCE_NAME=Elisa Rivadeneira
   WHATSAPP_NUMBER=+51967717179
   FLASK_ENV=production
   ```

3. **Configurar puerto**
   - Puerto interno: 5000
   - Puerto externo: 80 (o el que prefieras)

4. **Deploy**
   - Click "Deploy"
   - Esperar a que se construya la imagen
   - Verificar logs

### 3. Configurar Webhook en Evolution API

1. Obtener URL pública de la aplicación (ej: `https://seace-agent.tu-dominio.com`)
2. Configurar webhook en Evolution API:
   ```
   URL: https://seace-agent.tu-dominio.com/webhook
   Eventos: MESSAGES_UPSERT, SEND_MESSAGE
   ```

### 4. Verificar funcionamiento

1. Ir a `https://seace-agent.tu-dominio.com/status`
2. Enviar mensaje de WhatsApp a la instancia
3. Verificar respuesta automática

## 🔧 Troubleshooting

- **Logs**: Ver logs en Easypanel
- **Health check**: `/status` endpoint
- **Webhook test**: `/messages` endpoint

## 🚀 Auto-deploy

Cada push a `main` branch redesplegará automáticamente.
