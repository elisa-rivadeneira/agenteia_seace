FROM python:3.11-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary application files
COPY webhook_server.py .
COPY agente_whatsapp.py .
COPY agente_ia.py .
COPY whatsapp_notifier.py .
COPY excel_generator.py .
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
COPY landing_page.html .
COPY robots.txt .
COPY start_services.sh .

# Create data directory for persistent storage
RUN mkdir -p /data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV TZ=America/Lima

# Expose port
EXPOSE 5000

# Volume declaration (mount will be configured in Easypanel)
VOLUME /data

# Make start script executable
RUN chmod +x start_services.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/status || exit 1

# Run both webhook server and scheduler
CMD ["./start_services.sh"]
