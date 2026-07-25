# Instrucciones para Descarga Manual de SEACE

Ya que el portal SEACE bloquea bots automatizados, necesitas descargar manualmente el archivo de oportunidades.

## Pasos para Descargar

### Opción 1: Desde el Portal de Oportunidades (Datos más recientes - 2026)

1. **Abre tu navegador** e ingresa a:
   ```
   https://prod4.seace.gob.pe/openegocio/#/lista/43
   ```

2. **Espera** a que cargue la tabla con todas las oportunidades del segmento 43 (Tecnologías)

3. **Exporta los datos:**
   - Busca el botón de exportar/descargar (usualmente un ícono de Excel o CSV)
   - Descarga el archivo

4. **Renombra el archivo** a: `seace_convocatorias.xlsx` o `seace_convocatorias.csv`

### Opción 2: Desde Datos Abiertos (Datos hasta 2025)

1. **Abre tu navegador** e ingresa a:
   ```
   https://bi.seace.gob.pe/pentaho/api/repos/:public:portal:datosabiertosconvocatorias.html/content?userid=public&password=key
   ```

2. **Descarga el archivo Excel** de convocatorias

3. **Renombra el archivo** a: `seace_convocatorias.xlsx`

## Subir al Servidor

### Método 1: SCP (recomendado)

```bash
scp seace_convocatorias.xlsx root@your-server:/root/seace_convocatorias.xlsx
```

Luego en el servidor:
```bash
docker cp seace_convocatorias.xlsx $(docker ps -q --filter "name=seace"):/app/
```

### Método 2: Desde el servidor directamente

```bash
# Conectar al servidor
ssh root@your-server

# Descargar el archivo (si tienes un link directo)
wget -O seace_convocatorias.xlsx "URL_DEL_ARCHIVO"

# Copiar al contenedor
docker cp seace_convocatorias.xlsx $(docker ps -q --filter "name=seace"):/app/
```

## Probar que Funciona

```bash
# Ejecutar extractor
docker exec -it $(docker ps -q --filter "name=seace") python3 /app/seace_extractor_api.py
```

Deberías ver:
```
✅ Encontrado archivo: seace_convocatorias.xlsx
📊 Total de filas: XXXX
🎯 Oportunidades en segmento 43: XXX
```

## Automatizar con el Bot de WhatsApp

Una vez que el archivo esté en el contenedor, simplemente envía `/escanear` al bot por WhatsApp y procesará el archivo automáticamente.

## Frecuencia Recomendada

- **Descargar**: 1 vez al día (por la mañana)
- **Subir**: Usar un script cron o hacerlo manualmente
- **El bot**: Procesará automáticamente cuando hagas `/escanear`

## Script de Automatización (Opcional)

Puedes crear un script en tu computadora local que:
1. Descargue el archivo usando Selenium desde tu máquina
2. Lo suba automáticamente al servidor via SCP
3. Lo copie al contenedor

Esto lo ejecutas 1 vez al día desde tu computadora.
