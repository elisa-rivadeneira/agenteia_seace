#!/usr/bin/env python3
"""
Preparar aplicación para producción en VPS con Easypanel
"""

import os
import json
from datetime import datetime

def crear_estructura_produccion():
    """Crear estructura de archivos para producción"""

    print("📦 PREPARANDO PARA PRODUCCIÓN")
    print("=" * 50)

    # Crear requirements.txt
    requirements = """flask==2.3.3
requests==2.31.0
selenium==4.15.0
beautifulsoup4==4.12.2
python-dotenv==1.0.0
schedule==1.2.0
"""

    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("✅ requirements.txt creado")

    # Crear .env template
    env_template = """# Evolution API Configuration
EVOLUTION_API_URL=https://automation-evolution-api.gnrjtm.easypanel.host
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
EVOLUTION_INSTANCE_NAME=Elisa Rivadeneira

# WhatsApp Configuration
WHATSAPP_NUMBER=+51967717179

# Server Configuration
FLASK_ENV=production
FLASK_PORT=5000
FLASK_HOST=0.0.0.0

# Company Configuration
EMPRESA_NOMBRE=SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C
SEACE_SEGMENTO=43
"""

    with open('.env.example', 'w') as f:
        f.write(env_template)
    print("✅ .env.example creado")

    # Crear Dockerfile
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    unzip \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \\
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \\
    && apt-get update \\
    && apt-get install -y google-chrome-stable \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/status || exit 1

# Run application
CMD ["python", "webhook_server.py"]
"""

    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)
    print("✅ Dockerfile creado")

    # Crear docker-compose.yml
    docker_compose = """version: '3.8'

services:
  seace-agent:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
"""

    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose)
    print("✅ docker-compose.yml creado")

    # Crear .gitignore
    gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env
*.env

# Database
*.db
*.sqlite

# Logs
*.log

# Data files
seace_*.json
evolution_*.json
PyWhatKit_DB.txt
whatsapp_url*.txt

# Chrome/Selenium
chromedriver*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Screenshots
*.png
*.jpg
*.jpeg
"""

    with open('.gitignore', 'w') as f:
        f.write(gitignore)
    print("✅ .gitignore creado")

    # Crear README.md
    readme = """# 🤖 Agente SEACE WhatsApp

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
"""

    with open('README.md', 'w') as f:
        f.write(readme)
    print("✅ README.md creado")

    return True

def crear_git_repo():
    """Inicializar repositorio Git"""

    print("\n📁 INICIALIZANDO REPOSITORIO GIT")
    print("=" * 40)

    import subprocess

    try:
        # Inicializar git
        subprocess.run(['git', 'init'], check=True)
        print("✅ Git inicializado")

        # Agregar archivos
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Archivos agregados")

        # Commit inicial
        subprocess.run(['git', 'commit', '-m', 'Initial commit: SEACE WhatsApp Agent'], check=True)
        print("✅ Commit inicial creado")

        print("\n🌐 PARA SUBIR A GITHUB:")
        print("1. Crea un repositorio en GitHub")
        print("2. Ejecuta estos comandos:")
        print("   git remote add origin https://github.com/tu-usuario/seace-agent.git")
        print("   git branch -M main")
        print("   git push -u origin main")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error con git: {e}")
        return False
    except FileNotFoundError:
        print("❌ Git no está instalado")
        return False

def crear_deployment_guide():
    """Crear guía de deployment para Easypanel"""

    deployment_guide = """# 🚀 Deployment Guide - Easypanel

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
"""

    with open('DEPLOYMENT.md', 'w') as f:
        f.write(deployment_guide)
    print("✅ DEPLOYMENT.md creado")

def main():
    """Preparación completa para producción"""

    print("🚀 PREPARANDO SEACE AGENT PARA PRODUCCIÓN")
    print("=" * 60)
    print("📱 WhatsApp: +51967717179")
    print("🏢 SOLUCIONES TECNOLÓGICAS INTEGRALES S.A.C")
    print("🌐 VPS: Easypanel")
    print()

    if crear_estructura_produccion():
        print("\n📦 Estructura de archivos lista")

        if crear_git_repo():
            print("\n📁 Repositorio Git inicializado")

            crear_deployment_guide()

            print("\n🎉 ¡LISTO PARA PRODUCCIÓN!")
            print("=" * 40)
            print("📋 PRÓXIMOS PASOS:")
            print("1. Crear repositorio en GitHub")
            print("2. Subir código a GitHub")
            print("3. Configurar app en Easypanel")
            print("4. Configurar webhook en Evolution API")
            print("5. ¡Disfrutar del agente automático!")

        else:
            print("⚠️ Git no inicializado, pero archivos listos")
    else:
        print("❌ Error preparando archivos")

if __name__ == "__main__":
    main()