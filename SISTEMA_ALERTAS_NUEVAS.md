# Sistema de Alertas de Nuevas Oportunidades SEACE

## 📋 Descripción

Sistema que detecta automáticamente cuando aparecen **NUEVAS licitaciones** en SEACE y envía alertas inmediatas por WhatsApp.

## 🔑 Conceptos Clave

### Punto de Partida (Historial Base)
Cada usuario debe establecer un "punto de partida" que marca cuáles son las oportunidades actuales en SEACE. A partir de ese momento, el sistema solo alertará sobre oportunidades NUEVAS que aparezcan después.

### Tabla MySQL: `historial_oportunidades`
```sql
CREATE TABLE historial_oportunidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    segmento VARCHAR(10) NOT NULL,
    nomenclatura VARCHAR(100) NOT NULL,
    fecha_visto TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_historial (usuario_id, segmento, nomenclatura)
)
```

## 🚀 Flujo para Usuario Nuevo

### 1. Usuario se registra y configura segmentos
```
Usuario: /configurar
Agente: [Muestra catálogo de segmentos]
Usuario: Selecciona 43, 80, 81, 86
```

### 2. Primera vez que interactúa (sin historial)
El sistema detecta automáticamente que no tiene historial y pregunta:

```
👋 ¡Bienvenido al sistema de alertas SEACE!

📊 Veo que es tu primera vez o aún no has inicializado el sistema.

Para comenzar a recibir alertas de nuevas licitaciones, necesito:

1️⃣ Escanear SEACE en tus segmentos configurados
2️⃣ Marcar las oportunidades actuales como "punto de partida"
3️⃣ Enviarte un Excel con todas las oportunidades base

De esta forma, a partir de ese momento solo recibirás alertas de licitaciones NUEVAS que aparezcan.

¿Deseas que inicialice el sistema ahora? (Responde "sí" para continuar)
```

### 3. Usuario responde "sí"
El sistema ejecuta automáticamente `/init`:

1. Escanea SEACE en los 4 segmentos del usuario (43, 80, 81, 86)
2. Inserta todas las nomenclaturas en `historial_oportunidades`
3. Genera Excel con TODAS las oportunidades encontradas
4. Envía Excel por WhatsApp

**Resultado:**
- Historial: 150 oportunidades guardadas (ejemplo)
- Excel enviado con 150 oportunidades ordenadas por score
- Sistema listo para alertar sobre NUEVAS

### 4. Monitoreo automático
El sistema ejecuta `monitor_nuevas_oportunidades.py` cada 30 minutos:

- Escanea SEACE en los segmentos del usuario
- Compara con `historial_oportunidades`
- Detecta las que NO están en el historial = NUEVAS
- Envía alerta por WhatsApp
- **IMPORTANTE:** Agrega las nuevas al historial

## 📝 Comandos Disponibles

### `/init`
Inicializa el sistema para un usuario:
- Escanea todos sus segmentos
- Guarda historial base
- Envía Excel con oportunidades actuales
- Establece punto de partida

**Uso:**
```
/init
```

**Cuándo usarlo:**
- Primera vez que usa el sistema
- Quiere "refrescar" el punto de partida
- Agregó nuevos segmentos y quiere el Excel actualizado

### Detección Automática Conversacional
Si el usuario escribe cualquier mensaje y NO tiene historial, el sistema pregunta automáticamente si desea inicializar.

**Ejemplo:**
```
Usuario: hola
Agente: 👋 ¡Bienvenido! Veo que es tu primera vez...
Usuario: sí
Agente: [Ejecuta /init automáticamente]
```

## 🔧 Archivos del Sistema

### `monitor_nuevas_oportunidades.py`
Monitor que se ejecuta cada X minutos para detectar nuevas licitaciones.

**Uso:**
```bash
# Ejecutar cada 30 minutos (default)
python3 monitor_nuevas_oportunidades.py

# Ejecutar cada 15 minutos
python3 monitor_nuevas_oportunidades.py 15

# Test único (sin loop)
python3 monitor_nuevas_oportunidades.py --test
```

**Lo que hace:**
1. Obtiene usuarios con `alertas_realtime_activas = TRUE`
2. Para cada usuario, escanea sus segmentos
3. Compara con `historial_oportunidades`
4. Detecta nuevas (no en historial)
5. Filtra por `score_minimo` del usuario
6. Envía alertas por WhatsApp
7. Inserta nuevas en historial

### `agente_whatsapp.py`
Procesamiento de mensajes y comandos.

**Modificaciones:**
- Agregado `comando_init()`
- Agregado `verificar_historial_vacio()`
- Detección automática de historial vacío en `procesar_mensaje_libre()`

### `inicializar_historial_usuario.py`
Script manual para inicializar historial (ya no se usa tanto, `/init` lo reemplaza).

### `test_alerta_nueva_oportunidad.py`
Script de pruebas para simular detección de nuevas oportunidades.

**Uso:**
```bash
# Test normal
python3 test_alerta_nueva_oportunidad.py 51967717179 86

# Test simulando todo como nuevo
python3 test_alerta_nueva_oportunidad.py 51967717179 86 --limpiar
```

## 🎯 Ejemplo Completo de Flujo

### Día 1 - Inicialización
```
Usuario: hola
Agente: 👋 Bienvenido... ¿Deseas inicializar?
Usuario: sí

[Sistema ejecuta /init]
- Escanea segmentos: 43, 80, 81, 86
- Encuentra 150 oportunidades
- Guarda 150 en historial_oportunidades
- Genera Excel con 150 oportunidades
- Envía Excel por WhatsApp

Agente: ✅ Sistema inicializado
        📊 150 oportunidades guardadas
        📁 Te envié el Excel con tu punto de partida
        🔔 A partir de ahora solo recibirás alertas de NUEVAS licitaciones
```

### Día 2 - Monitor detecta 3 nuevas
```
[monitor_nuevas_oportunidades.py se ejecuta cada 30 min]

10:30 AM - Escaneo
- Encuentra 153 oportunidades en total
- Compara con historial (150)
- Detecta 3 NUEVAS (LP-SM-15-2026, LP-SM-16-2026, LP-SM-17-2026)
- Filtra por score ≥30%: las 3 cumplen
- Envía alertas:

🔔 NUEVAS LICITACIONES DETECTADAS
Se detectaron 3 nuevas oportunidades

[Mensaje 1: LP-SM-15-2026]
[Mensaje 2: LP-SM-16-2026]
[Mensaje 3: LP-SM-17-2026]

- Inserta las 3 en historial_oportunidades
- Historial ahora tiene 153 oportunidades
```

### Día 3 - Usuario ejecuta /init de nuevo
```
Usuario: /init

[Sistema vuelve a escanear]
- Encuentra 155 oportunidades
- BORRA historial anterior (153)
- Guarda 155 nuevas en historial
- Genera Excel con 155
- Envía Excel

Usuario: Ahora mi punto de partida son 155
```

## ⚙️ Configuración de Producción

### Dockerfile
Para ejecutar el monitor en producción junto con el webhook:

```dockerfile
# Ejecutar webhook server y monitor en paralelo
CMD python3 webhook_server.py & python3 monitor_nuevas_oportunidades.py 30
```

### Variables de Entorno
```bash
# MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=seace_monitor
DB_USER=root
DB_PASSWORD=tu_password

# Evolution API
EVOLUTION_API_URL=https://...
EVOLUTION_API_KEY=...
EVOLUTION_INSTANCE_NAME=...

# OpenAI
OPENAI_API_KEY=sk-proj-...
```

## 🧪 Testing

### Método 1: Script automático (Recomendado)

```bash
# Simula 1 oportunidad nueva
python3 simular_oportunidad_nueva.py 51967717179

# Simula 5 oportunidades nuevas
python3 simular_oportunidad_nueva.py 51967717179 5
```

El script:
1. Selecciona oportunidades aleatorias del historial
2. Te muestra cuáles borrará
3. Pide confirmación
4. Las borra del historial
5. Te dice cómo ejecutar el monitor

Luego ejecuta:
```bash
python3 monitor_nuevas_oportunidades.py --test
```

Deberías recibir alertas en WhatsApp ✅

### Método 2: Script bash completo

```bash
./test_monitor_nuevas.sh
```

Hace todo automáticamente:
- Muestra estado del historial
- Borra 1 oportunidad
- Ejecuta el monitor
- Te dice qué verificar

### Método 3: Manual con MySQL

```bash
# 1. Ver historial actual
mysql -u root -p seace_monitor -e "
SELECT COUNT(*) as total, MAX(fecha_visto) as ultima
FROM historial_oportunidades
WHERE usuario_id = 1
"

# 2. Borrar UNA oportunidad específica
mysql -u root -p seace_monitor -e "
DELETE FROM historial_oportunidades
WHERE usuario_id = 1
AND nomenclatura = 'LP-SM-14-2026-XXXXX'
LIMIT 1
"

# 3. Ejecutar monitor
python3 monitor_nuevas_oportunidades.py --test

# 4. Verificar que se agregó de nuevo al historial
mysql -u root -p seace_monitor -e "
SELECT * FROM historial_oportunidades
WHERE nomenclatura = 'LP-SM-14-2026-XXXXX'
"
```

### Test completo del flujo (desde cero)

```bash
# 1. Limpiar historial
mysql -u root -p seace_monitor -e "DELETE FROM historial_oportunidades WHERE usuario_id = 1"

# 2. Ejecutar /init por WhatsApp
Usuario: /init

# 3. Verificar historial
mysql -u root -p seace_monitor -e "SELECT COUNT(*) FROM historial_oportunidades WHERE usuario_id = 1"

# 4. Simular nueva oportunidad
python3 simular_oportunidad_nueva.py 51967717179 3

# 5. Ejecutar monitor
python3 monitor_nuevas_oportunidades.py --test

# 6. Verificar WhatsApp - deberían llegar 3 alertas
```

## 📊 Monitoreo

### Ver historial de un usuario
```sql
SELECT
    h.segmento,
    COUNT(*) as total_vistas,
    MAX(h.fecha_visto) as ultima_vista
FROM historial_oportunidades h
WHERE h.usuario_id = 1
GROUP BY h.segmento
```

### Ver usuarios con alertas activas
```sql
SELECT
    u.nombre,
    u.numero,
    c.alertas_realtime_activas,
    c.score_minimo,
    COUNT(h.id) as oportunidades_vistas
FROM usuarios u
INNER JOIN usuario_configuracion c ON u.id = c.usuario_id
LEFT JOIN historial_oportunidades h ON u.id = h.usuario_id
WHERE u.activo = TRUE
GROUP BY u.id
```

## ❓ FAQ

### ¿Qué pasa si un usuario agrega un nuevo segmento?
Debería ejecutar `/init` para refrescar su historial base con el nuevo segmento.

### ¿Con qué frecuencia se debe ejecutar el monitor?
Recomendado: 30 minutos. SEACE actualiza oportunidades constantemente pero no es necesario escanear cada 5 minutos.

### ¿Se puede cambiar el punto de partida?
Sí, ejecutando `/init` de nuevo. Esto reescribirá el historial.

### ¿Qué pasa si SEACE elimina una licitación?
Permanece en el historial. Solo se agregan nuevas, nunca se eliminan registros históricos.

---

**Última actualización:** 2026-08-11
**Autor:** Claude Code + Elisa Rivadeneira
