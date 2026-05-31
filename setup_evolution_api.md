# 📱 Guía de Configuración WhatsApp para SEACE Buscador

## Opciones de Integración

### 1. Evolution API (Recomendado - Gratis)

Evolution API es una solución gratuita y open source que permite conectar WhatsApp Web.

#### Instalación con Docker:
```bash
# Clonar repositorio
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Configurar variables de entorno
cp .env.example .env
nano .env

# Iniciar con Docker
docker-compose up -d
```

#### Configuración:
1. Accede a `http://localhost:8080/manager`
2. Crea una nueva instancia
3. Escanea el código QR con WhatsApp
4. Copia el API Key generado

#### Crear archivo `whatsapp_config.json`:
```json
{
  "evolution": {
    "enabled": true,
    "base_url": "http://localhost:8080",
    "instance": "seace_monitor",
    "api_key": "TU_API_KEY_AQUI"
  }
}
```

---

### 2. Baileys (Alternativa Gratis)

Usa WhatsApp Web sin interfaz gráfica.

#### Instalación rápida:
```bash
# Instalar Baileys API simple
npm install -g @adiwajshing/baileys
npm install -g baileys-api

# Iniciar servidor
baileys-api start --port 3000
```

#### Configuración en `whatsapp_config.json`:
```json
{
  "baileys": {
    "enabled": true,
    "base_url": "http://localhost:3000",
    "session": "seace_session"
  }
}
```

---

### 3. Twilio (Pago - $0.005 por mensaje)

Servicio profesional con alta confiabilidad.

#### Configuración:
1. Crea cuenta en https://www.twilio.com
2. Verifica tu número de WhatsApp
3. Obtén credenciales desde la consola

```bash
# Instalar biblioteca
pip install twilio
```

#### Configuración en `whatsapp_config.json`:
```json
{
  "twilio": {
    "enabled": true,
    "account_sid": "ACxxxxxxxxxxxxxxxxxx",
    "auth_token": "xxxxxxxxxxxxxxxx",
    "from_number": "+14155238886"
  }
}
```

---

### 4. WhatsApp Business API (Oficial - Requiere aprobación)

Para empresas con volumen alto.

#### Requisitos:
- Cuenta de Facebook Business
- Número de teléfono verificado
- Aprobación de Meta

---

## 🚀 Uso Rápido

### Probar conexión:
```bash
python3 whatsapp_notifier.py
# Selecciona opción 1
```

### Enviar notificaciones de oportunidades:
```python
from whatsapp_notifier import WhatsAppNotifier
import json

# Cargar oportunidades
with open('seace_todas_oportunidades_20260525_212224.json', 'r') as f:
    data = json.load(f)

# Enviar notificaciones
notifier = WhatsAppNotifier()
notifier.send_oportunidades_report(data['oportunidades'])
```

### Integrar con el monitor automático:
```python
# En tu script de monitoreo agregar:
from whatsapp_notifier import WhatsAppNotifier

notifier = WhatsAppNotifier()

# Cuando encuentres oportunidades relevantes:
if oportunidad['score_compatibilidad'] >= 70:
    notifier.send_message(
        notifier.format_oportunidad(oportunidad),
        priority='high'
    )
```

---

## 📊 Ejemplo de Notificación

```
📊 REPORTE SEACE - SOLUCIONES TECNOLÓGICAS S.A.C
25/05/2026 21:30

Total encontradas: 25
Relevantes (≥30%): 10
Urgentes (≤3 días): 3

🚨 URGENTES:
• COFIDE - 26/05/2026
• Universidad Sánchez Carrión - 26/05/2026
• GR Cusco - 26/05/2026

⭐ MÁS RELEVANTES:
• Banco de la Nación (85%)
• Contraloría General (80%)
• Electro Oriente (75%)

_Revisa el sistema para más detalles_
```

---

## 🔧 Comandos Útiles

### Instalar todas las dependencias:
```bash
pip install requests twilio pywhatkit
```

### Ejecutar monitor con notificaciones:
```bash
# Monitor continuo con WhatsApp
python3 -c "
from whatsapp_notifier import WhatsAppNotifier
import time
import subprocess

notifier = WhatsAppNotifier()
while True:
    # Ejecutar extractor
    subprocess.run(['python3', 'seace_extractor_multipagina.py'])

    # Enviar notificaciones
    import json
    with open('seace_todas_oportunidades_20260525_212224.json') as f:
        data = json.load(f)
    notifier.send_oportunidades_report(data['oportunidades'])

    # Esperar 30 minutos
    time.sleep(1800)
"
```

---

## ⚠️ Notas Importantes

1. **Evolution API** es la opción más fácil y gratuita
2. Mantén tu sesión de WhatsApp Web activa
3. No uses el mismo número en múltiples dispositivos
4. Respeta los límites de mensajes (evita spam)
5. Configura horarios apropiados (7am - 8pm)

---

## 🆘 Solución de Problemas

### Error: "No se pudo enviar el mensaje"
- Verifica que Evolution API esté ejecutándose
- Confirma que la sesión de WhatsApp esté activa
- Revisa el archivo `whatsapp_config.json`

### Error: "Session expired"
- Escanea nuevamente el código QR
- Reinicia Evolution API

### No llegan los mensajes
- Verifica el número en formato internacional (+51...)
- Confirma que el número esté registrado en WhatsApp
- Revisa los logs de Evolution API