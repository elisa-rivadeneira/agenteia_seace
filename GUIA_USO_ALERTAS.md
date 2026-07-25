# 📘 Guía de Uso - Sistema de Alertas SEACE

## 🌐 Acceso al Sistema

**URL Local:** `http://localhost:5000/admin`
**URL Producción:** `https://automation-agente-seace.gnrjtm.easypanel.host/admin`
**Password:** `admin123` (cambiar con variable `ADMIN_PASSWORD`)

---

## 👥 Gestión de Usuarios

### Acceder
`http://localhost:5000/admin/usuarios`

### Agregar Usuario Manualmente
1. Click en **"➕ Agregar Usuario"**
2. Completar formulario:
   - **Nombre:** (requerido)
   - **Número:** 51967717179 (sin espacios, con código de país)
   - **Email:** (opcional)
3. Click **"Guardar"**

### Importar Usuarios desde Conversaciones
1. Click en **"📥 Importar desde Conversaciones"**
2. Confirmar
3. Se importan automáticamente todos los usuarios que han chateado con el bot

### Activar/Desactivar Usuario
- Click en **"Desactivar"** o **"Activar"** según el estado actual
- Los usuarios inactivos NO recibirán alertas

### Eliminar Usuario
- Click en **"Eliminar"**
- Confirmar acción
- **Nota:** Si el usuario está asignado a alertas, se eliminará de ellas

---

## ⏰ Gestión de Alertas

### Acceder
`http://localhost:5000/admin/alertas`

### Crear Nueva Alerta

1. Click en **"➕ Crear Nueva Alerta"**

2. **Completar Formulario:**

   **Nombre de la Alerta** *
   ```
   Ejemplo: "Alerta TI - Lunes a Viernes"
   ```

   **Segmento SEACE** *
   ```
   43 - Tecnologías de la Información (por defecto)
   ```

   **Horarios** * (uno o más)
   ```
   1. Seleccionar hora: 10:00
   2. Click "Agregar"
   3. Repetir para agregar más horarios (14:00, 19:00, etc.)
   ```

   **Días de la Semana** * (uno o más)
   ```
   ☑️ Lunes
   ☑️ Martes
   ☑️ Miércoles
   ☑️ Jueves
   ☑️ Viernes
   ☐ Sábado
   ☐ Domingo
   ```

   **Usuarios** * (uno o más)
   ```
   Mantén Ctrl/Cmd presionado para seleccionar múltiples
   - Elisa Rivadaneira (51967717179)
   - Carlos Mendoza (51999888777)
   ```

   **Score Mínimo** (opcional)
   ```
   30 (por defecto)
   Solo se envían oportunidades con este score o superior
   ```

   **Máximo Oportunidades** (opcional)
   ```
   5 (por defecto)
   Cantidad máxima de oportunidades por alerta
   ```

3. Click **"Guardar Alerta"**

### ✏️ Editar Alerta Existente

1. En la tabla de alertas, click **"Editar"** en la alerta deseada
2. El formulario se llena automáticamente con los datos actuales
3. Modificar los campos necesarios
4. Click **"Guardar Alerta"**

**Campos editables:**
- ✅ Nombre
- ✅ Segmento
- ✅ Horarios (agregar/eliminar)
- ✅ Días de la semana
- ✅ Usuarios asignados
- ✅ Score mínimo
- ✅ Máximo de oportunidades

### Activar/Desactivar Alerta

- Click en **"Desactivar"** o **"Activar"**
- Las alertas inactivas **no se ejecutarán** en sus horarios programados

### Eliminar Alerta

- Click **"Eliminar"**
- Confirmar acción
- La alerta se elimina permanentemente

---

## 📋 Ejemplos de Uso

### Ejemplo 1: Alerta de Lunes a Viernes, 2 horarios

```
Nombre: Alerta TI - Horario Laboral
Segmento: 43
Horarios: 10:00, 19:00
Días: L, M, X, J, V
Usuarios: Elisa Rivadaneira, Carlos Mendoza
Score Mínimo: 30
Max Oportunidades: 5
```

**Resultado:** Se escanea SEACE a las 10am y 7pm de lunes a viernes, notificando a 2 usuarios.

### Ejemplo 2: Alerta de Fin de Semana

```
Nombre: Alerta TI - Fin de Semana
Segmento: 43
Horarios: 11:00
Días: S, D
Usuarios: Elisa Rivadaneira
Score Mínimo: 50
Max Oportunidades: 3
```

**Resultado:** Se escanea SEACE a las 11am sábados y domingos, notificando solo oportunidades con score ≥50%.

### Ejemplo 3: Alerta Urgente - Todos los días, 3 horarios

```
Nombre: Alerta TI - Urgente
Segmento: 43
Horarios: 09:00, 14:00, 20:00
Días: L, M, X, J, V, S, D
Usuarios: Elisa Rivadaneira, Carlos Mendoza, Ana Torres
Score Mínimo: 40
Max Oportunidades: 10
```

**Resultado:** Se escanea 3 veces al día, todos los días, notificando a 3 usuarios.

---

## 🔔 Cómo Funcionan las Alertas

### Flujo de Ejecución

1. **Scheduler verifica horarios** cada minuto
2. **Si coincide** con alguna alerta activa:
   - Verifica que sea el día correcto
   - Escanea SEACE para el segmento configurado
   - Filtra oportunidades nuevas (no vistas antes)
   - Calcula score de compatibilidad
   - Filtra por score mínimo
   - Ordena por relevancia
   - Toma las top N oportunidades
3. **Envía notificaciones** por WhatsApp a usuarios asignados
4. **Registra ejecución** para evitar duplicados

### Formato del Mensaje

```
🔔 ALERTA AUTOMÁTICA SEACE
Hora: 25/07/2026 10:00

¡Se encontraron 3 nuevas oportunidades!
2 con alta compatibilidad (≥30%)

Te enviaré los detalles...

---

🚨 NUEVA OPORTUNIDAD SEACE

🌟 Score de compatibilidad: 75%

Entidad:
MINISTERIO DE EDUCACIÓN

Descripción:
Adquisición de equipos informáticos...

📅 Fechas importantes:
• Inicio consultas: 25/07/2026
• Fin consultas: 05/08/2026
• Presentación propuestas: 10/08/2026

🔗 Ver en SEACE:
https://prod4.seace.gob.pe/...

Nomenclatura: LP-SM-14-2026-XXX
```

---

## ❓ Preguntas Frecuentes

### ¿Puedo tener múltiples alertas con diferentes configuraciones?
✅ Sí, puedes crear tantas alertas como necesites, cada una independiente.

### ¿Un usuario puede estar en varias alertas?
✅ Sí, un usuario puede recibir notificaciones de múltiples alertas.

### ¿Qué pasa si agrego el mismo horario dos veces?
⚠️ El sistema evita duplicados, solo se ejecuta una vez por horario.

### ¿Se pueden editar los horarios de una alerta activa?
✅ Sí, los cambios se aplican en el próximo escaneo programado.

### ¿Cómo sé si una alerta se ejecutó?
📊 En la tabla de alertas se muestra "Última Ejecución" con fecha y hora.

### ¿Qué pasa si elimino un usuario que está en alertas?
⚠️ Se elimina automáticamente de todas las alertas donde estaba asignado.

### ¿Las alertas funcionan en producción?
✅ Sí, el sistema funciona igual en local y producción con volúmenes persistentes.

---

## 🚀 Puesta en Producción

### Pasos para Deploy

1. **Actualizar Dockerfile** (ya incluye nuevos archivos):
   ```dockerfile
   COPY database_manager.py .
   COPY admin_routes.py .
   COPY admin_templates.py .
   ```

2. **Configurar Volumen en Easypanel**:
   ```
   Mount Type: Volume
   Container Path: /data
   Volume Name: seace_data_volume
   ```

3. **Push a GitHub**:
   ```bash
   git add .
   git commit -m "Sistema de alertas múltiples con gestión de usuarios"
   git push origin main
   ```

4. **Rebuild en Easypanel**

5. **Verificar** en `https://automation-agente-seace.gnrjtm.easypanel.host/admin/alertas`

---

## 📞 Soporte

Para ayuda adicional, revisa:
- `CLAUDE.md` - Documentación técnica completa
- `CONFIGURACION_VOLUMEN_EASYPANEL.md` - Guía de persistencia de datos

---

**Última actualización:** 2026-07-25
**Versión:** 3.0 (Sistema de alertas múltiples)
