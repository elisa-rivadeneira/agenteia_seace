FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome and ChromeDriver
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | sed 's/Google Chrome //') \
    && CHROMEDRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION%%.*}) \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary application files
COPY webhook_server.py .
COPY agente_whatsapp.py .
COPY agente_ia.py .
COPY whatsapp_notifier.py .
COPY seace_extractor_realtime.py .
COPY seace_detalle.py .
COPY conversaciones_logger.py .
COPY alertas_manager.py .
COPY scheduler_alertas.py .
COPY scheduler_alertas_v2.py .
COPY database_manager.py .
COPY admin_routes.py .
COPY admin_templates.py .
COPY config_paths.py .
COPY config_empresa.json .

# Create data directory for persistent volume
RUN mkdir -p /data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# VOLUME for persistent data (configurar en Easypanel)
VOLUME ["/data"]

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/status || exit 1

COPY landing_page.html .
COPY robots.txt .
COPY start_services.sh .
RUN chmod +x start_services.sh

# Run both webhook server and scheduler
CMD ["./start_services.sh"]
