# 🤖 Agente SEACE WhatsApp

Sistema inteligente para monitoreo automático de oportunidades SEACE con notificaciones vía WhatsApp.

## 🚀 Características

- ✅ **Monitor SEACE automático** - Detecta nuevas oportunidades
- ✅ **Agente conversacional** - Responde comandos por WhatsApp
- ✅ **Integration Evolution API** - Envío automático real
- ✅ **Análisis inteligente** - Score de compatibilidad
- ✅ **Alertas urgentes** - Notificaciones de oportunidades próximas a vencer

## 📱 Comandos WhatsApp

- `/estado` - Estado del sistema
- `/escanear` - Buscar oportunidades ahora
- `/urgentes` - Oportunidades urgentes
- `/reporte` - Reporte completo
- `/ayuda` - Lista de comandos

## 🔧 Instalación Local

```bash
git clone <repository-url>
cd seace_buscador
cp .env.example .env
# Editar .env con tus configuraciones
pip install -r requirements.txt
python webhook_server.py
```

## 🐳 Instalación Docker

```bash
docker-compose up -d
```

## ⚙️ Configuración

1. Configurar Evolution API con instancia WhatsApp
2. Establecer webhook URL en Evolution API
3. Configurar variables de entorno en `.env`

## 📊 Endpoints API

- `GET /status` - Estado del sistema
- `POST /webhook` - Webhook Evolution API
- `GET /messages` - Mensajes recibidos
- `POST /send` - Envío manual de mensajes

## 🏢 Empresa

**SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C**
- Segmento SEACE: 43 - Tecnologías de la Información
- WhatsApp: +51967717179

## 📄 Licencia

MIT License
