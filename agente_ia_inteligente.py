#!/usr/bin/env python3
"""
AGENTE IA INTELIGENTE PARA MONITOREO Y ANÁLISIS DE LICITACIONES SEACE
Segmento 43: Telecomunicaciones y Tecnología de la Información

Este agente:
1. Monitorea constantemente las oportunidades nuevas
2. Descarga y analiza los PDFs de bases
3. Evalúa la compatibilidad con tu empresa
4. Envía alertas tempranas sobre oportunidades relevantes
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time
import requests
import PyPDF2
import re
from datetime import datetime, timedelta
import sqlite3
import hashlib
from typing import List, Dict, Tuple
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
from dataclasses import dataclass
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agente_seace.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class Oportunidad:
    """Estructura de datos para una oportunidad de licitación"""
    nomenclatura: str
    entidad: str
    objeto: str
    descripcion_procedimiento: str
    descripcion_item: str
    fecha_fin_registro: str
    valor: str
    valor_numerico: float
    moneda: str
    url_bases: str = None
    contenido_pdf: str = None
    score_compatibilidad: float = 0.0
    razones_compatibilidad: List[str] = None
    fecha_descubierta: str = None
    dias_restantes: int = 0

class AgenteIASeace:
    """Agente Inteligente para monitoreo y análisis de licitaciones"""

    def __init__(self, config_file="config_empresa.json"):
        """Inicializa el agente con la configuración de la empresa"""
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.empresa = self.config['empresa']
        self.init_database()
        self.driver = None
        self.oportunidades_nuevas = []
        self.oportunidades_relevantes = []

        logging.info(f"Agente IA inicializado para: {self.empresa['nombre']}")

    def init_database(self):
        """Inicializa la base de datos para tracking"""
        self.conn = sqlite3.connect('seace_monitoring.db')
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oportunidades (
                nomenclatura TEXT PRIMARY KEY,
                entidad TEXT,
                objeto TEXT,
                descripcion_procedimiento TEXT,
                descripcion_item TEXT,
                fecha_fin_registro TEXT,
                valor TEXT,
                valor_numerico REAL,
                moneda TEXT,
                url_bases TEXT,
                contenido_pdf TEXT,
                score_compatibilidad REAL,
                razones_compatibilidad TEXT,
                fecha_descubierta TIMESTAMP,
                dias_restantes INTEGER,
                notificado INTEGER DEFAULT 0,
                estado TEXT DEFAULT 'activo'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analisis_pdf (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomenclatura TEXT,
                fecha_analisis TIMESTAMP,
                palabras_clave_encontradas TEXT,
                requisitos_tecnicos TEXT,
                requisitos_experiencia TEXT,
                requisitos_financieros TEXT,
                cumple_requisitos INTEGER,
                observaciones TEXT,
                FOREIGN KEY(nomenclatura) REFERENCES oportunidades(nomenclatura)
            )
        """)

        self.conn.commit()

    def iniciar_navegador(self, headless=True):
        """Inicializa el navegador Selenium"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        if headless:
            options.add_argument('--headless=new')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def extraer_oportunidades_segmento_43(self) -> List[Oportunidad]:
        """Extrae todas las oportunidades del segmento 43"""
        url = "https://prod4.seace.gob.pe/openegocio/#/lista/43"
        logging.info(f"Accediendo a: {url}")

        self.driver.get(url)
        time.sleep(12)  # Esperar carga de Angular

        oportunidades = []

        try:
            # Hacer clic en cada fila para obtener detalles
            filas = self.driver.find_elements(By.CSS_SELECTOR, "mat-row, tr[role='row']")

            for i in range(len(filas)):
                try:
                    # Re-obtener las filas después de cada navegación
                    filas = self.driver.find_elements(By.CSS_SELECTOR, "mat-row, tr[role='row']")

                    if i >= len(filas):
                        break

                    fila = filas[i]
                    texto_fila = fila.text

                    # Extraer datos básicos de la fila
                    oportunidad = self.parsear_fila(texto_fila)

                    if oportunidad:
                        # Intentar obtener más detalles haciendo clic
                        try:
                            fila.click()
                            time.sleep(2)

                            # Buscar enlace a las bases
                            self.buscar_url_bases(oportunidad)

                            # Volver a la lista
                            self.driver.back()
                            time.sleep(2)

                        except:
                            pass

                        oportunidades.append(oportunidad)

                except Exception as e:
                    logging.error(f"Error procesando fila {i}: {e}")
                    continue

        except Exception as e:
            logging.error(f"Error extrayendo oportunidades: {e}")

        return oportunidades

    def parsear_fila(self, texto: str) -> Oportunidad:
        """Parsea el texto de una fila para crear una Oportunidad"""
        lineas = texto.split('\n')

        datos = {
            'nomenclatura': None,
            'entidad': None,
            'objeto': None,
            'descripcion_procedimiento': None,
            'descripcion_item': None,
            'fecha_fin_registro': None,
            'valor': '0',
            'valor_numerico': 0,
            'moneda': 'PEN'
        }

        # Buscar patrones en las líneas
        for i, linea in enumerate(lineas):
            if 'Entidad:' in linea and i+1 < len(lineas):
                datos['entidad'] = lineas[i+1] if i+1 < len(lineas) else linea.replace('Entidad:', '').strip()
            elif 'Nomenclatura:' in linea:
                datos['nomenclatura'] = linea.replace('Nomenclatura:', '').strip()
            elif 'Objeto:' in linea:
                datos['objeto'] = linea.replace('Objeto:', '').strip()
            elif 'Descripción procedimiento:' in linea:
                datos['descripcion_procedimiento'] = linea.replace('Descripción procedimiento:', '').strip()
            elif 'Descripción ítem:' in linea:
                datos['descripcion_item'] = linea.replace('Descripción ítem:', '').strip()
            elif 'Fecha Fin' in linea and i+1 < len(lineas):
                datos['fecha_fin_registro'] = lineas[i+1]
            elif re.match(r'.*\d+.*Soles', linea):
                # Extraer valor numérico
                numeros = re.findall(r'[\d,]+\.?\d*', linea)
                if numeros:
                    datos['valor'] = linea
                    datos['valor_numerico'] = float(numeros[0].replace(',', ''))

        # Calcular días restantes
        if datos['fecha_fin_registro']:
            datos['dias_restantes'] = self.calcular_dias_restantes(datos['fecha_fin_registro'])

        if datos['nomenclatura']:
            return Oportunidad(**datos, fecha_descubierta=datetime.now().isoformat())

        return None

    def calcular_dias_restantes(self, fecha_str: str) -> int:
        """Calcula los días restantes hasta la fecha límite"""
        try:
            # Parsear fecha en formato DD/MM/YYYY HH:MM:SS
            fecha = datetime.strptime(fecha_str.split()[0], '%d/%m/%Y')
            hoy = datetime.now()
            diferencia = fecha - hoy
            return diferencia.days
        except:
            return 0

    def buscar_url_bases(self, oportunidad: Oportunidad):
        """Busca el enlace para descargar las bases"""
        try:
            # Buscar enlaces de descarga
            enlaces = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Descargar")
            if not enlaces:
                enlaces = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Bases")
            if not enlaces:
                enlaces = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='pdf'], a[href*='doc']")

            if enlaces:
                oportunidad.url_bases = enlaces[0].get_attribute('href')
                logging.info(f"URL bases encontrada: {oportunidad.url_bases}")

        except Exception as e:
            logging.error(f"Error buscando URL bases: {e}")

    def descargar_y_analizar_pdf(self, oportunidad: Oportunidad) -> bool:
        """Descarga y analiza el PDF de las bases"""
        if not oportunidad.url_bases:
            return False

        try:
            # Descargar PDF
            response = requests.get(oportunidad.url_bases, timeout=30)

            # Guardar temporalmente
            pdf_path = f"temp_{oportunidad.nomenclatura}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)

            # Extraer texto del PDF
            texto_pdf = self.extraer_texto_pdf(pdf_path)
            oportunidad.contenido_pdf = texto_pdf

            # Limpiar archivo temporal
            os.remove(pdf_path)

            return True

        except Exception as e:
            logging.error(f"Error descargando/analizando PDF: {e}")
            return False

    def extraer_texto_pdf(self, pdf_path: str) -> str:
        """Extrae el texto de un archivo PDF"""
        texto = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    texto += page.extract_text()
        except Exception as e:
            logging.error(f"Error extrayendo texto del PDF: {e}")

        return texto

    def evaluar_compatibilidad(self, oportunidad: Oportunidad) -> Tuple[float, List[str]]:
        """
        Evalúa la compatibilidad de una oportunidad con las capacidades de la empresa
        Retorna: (score 0-100, lista de razones)
        """
        score = 0
        razones = []
        texto_completo = f"{oportunidad.descripcion_procedimiento} {oportunidad.descripcion_item} {oportunidad.contenido_pdf or ''}"
        texto_completo = texto_completo.lower()

        # 1. Evaluar palabras clave positivas (40 puntos)
        palabras_encontradas = 0
        for palabra in self.empresa['palabras_clave_positivas']:
            if palabra.lower() in texto_completo:
                palabras_encontradas += 1

        if palabras_encontradas > 0:
            puntos_palabras = min(40, palabras_encontradas * 5)
            score += puntos_palabras
            razones.append(f"✅ {palabras_encontradas} palabras clave relevantes encontradas")

        # 2. Evaluar palabras clave negativas (-30 puntos)
        palabras_negativas = 0
        for palabra in self.empresa['palabras_clave_negativas']:
            if palabra.lower() in texto_completo:
                palabras_negativas += 1

        if palabras_negativas > 0:
            score -= palabras_negativas * 10
            razones.append(f"⚠️ {palabras_negativas} palabras no relacionadas con el rubro")

        # 3. Evaluar monto (20 puntos)
        if oportunidad.valor_numerico > 0:
            monto_min = self.empresa['montos_preferidos']['minimo']
            monto_max = self.empresa['montos_preferidos']['maximo']

            if monto_min <= oportunidad.valor_numerico <= monto_max:
                score += 20
                razones.append(f"✅ Monto dentro del rango preferido: {oportunidad.moneda} {oportunidad.valor_numerico:,.2f}")
            elif oportunidad.valor_numerico < monto_min:
                score += 5
                razones.append(f"ℹ️ Monto por debajo del preferido")
            else:
                razones.append(f"⚠️ Monto superior a la capacidad")

        # 4. Evaluar urgencia (20 puntos)
        if oportunidad.dias_restantes > 7:
            score += 20
            razones.append(f"✅ Tiempo suficiente: {oportunidad.dias_restantes} días restantes")
        elif oportunidad.dias_restantes > 3:
            score += 10
            razones.append(f"⚠️ Tiempo ajustado: {oportunidad.dias_restantes} días restantes")
        else:
            razones.append(f"❌ Muy poco tiempo: {oportunidad.dias_restantes} días")

        # 5. Evaluar entidad (20 puntos)
        if any(palabra in texto_completo for palabra in ['gobierno regional', 'ministerio', 'banco']):
            score += 20
            razones.append("✅ Entidad de alto nivel")

        # Normalizar score
        score = max(0, min(100, score))

        return score, razones

    def guardar_oportunidad(self, oportunidad: Oportunidad):
        """Guarda una oportunidad en la base de datos"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO oportunidades (
                nomenclatura, entidad, objeto, descripcion_procedimiento,
                descripcion_item, fecha_fin_registro, valor, valor_numerico,
                moneda, url_bases, contenido_pdf, score_compatibilidad,
                razones_compatibilidad, fecha_descubierta, dias_restantes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            oportunidad.nomenclatura,
            oportunidad.entidad,
            oportunidad.objeto,
            oportunidad.descripcion_procedimiento,
            oportunidad.descripcion_item,
            oportunidad.fecha_fin_registro,
            oportunidad.valor,
            oportunidad.valor_numerico,
            oportunidad.moneda,
            oportunidad.url_bases,
            oportunidad.contenido_pdf[:1000] if oportunidad.contenido_pdf else None,
            oportunidad.score_compatibilidad,
            json.dumps(oportunidad.razones_compatibilidad),
            oportunidad.fecha_descubierta,
            oportunidad.dias_restantes
        ))

        self.conn.commit()

    def verificar_nueva_oportunidad(self, nomenclatura: str) -> bool:
        """Verifica si una oportunidad es nueva"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT notificado FROM oportunidades WHERE nomenclatura = ?", (nomenclatura,))
        resultado = cursor.fetchone()
        return resultado is None or resultado[0] == 0

    def enviar_alerta(self, oportunidades_relevantes: List[Oportunidad]):
        """Envía alertas sobre oportunidades relevantes"""
        if not oportunidades_relevantes:
            return

        mensaje = self.generar_mensaje_alerta(oportunidades_relevantes)

        # Imprimir en consola
        print("\n" + "="*80)
        print(mensaje)
        print("="*80 + "\n")

        # Guardar en archivo
        with open(f"alerta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
            f.write(mensaje)

        # Marcar como notificadas
        cursor = self.conn.cursor()
        for op in oportunidades_relevantes:
            cursor.execute("UPDATE oportunidades SET notificado = 1 WHERE nomenclatura = ?", (op.nomenclatura,))
        self.conn.commit()

    def generar_mensaje_alerta(self, oportunidades: List[Oportunidad]) -> str:
        """Genera el mensaje de alerta"""
        mensaje = f"""
🚨 ALERTA DE OPORTUNIDADES SEACE - SEGMENTO 43
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Empresa: {self.empresa['nombre']}

Se han detectado {len(oportunidades)} oportunidades relevantes:

"""
        for i, op in enumerate(oportunidades, 1):
            mensaje += f"""
{i}. {op.nomenclatura}
   Entidad: {op.entidad}
   Descripción: {op.descripcion_procedimiento[:100]}...
   Valor: {op.moneda} {op.valor_numerico:,.2f}
   Compatibilidad: {op.score_compatibilidad:.0f}%
   Días restantes: {op.dias_restantes}

   Razones de compatibilidad:
"""
            for razon in op.razones_compatibilidad:
                mensaje += f"   {razon}\n"

            mensaje += f"\n   ⏰ ACCIÓN REQUERIDA: Revisar bases y preparar propuesta\n"
            mensaje += "-"*70 + "\n"

        return mensaje

    def monitorear_continuamente(self):
        """Función principal de monitoreo continuo"""
        logging.info("Iniciando monitoreo continuo del segmento 43...")

        while True:
            try:
                # Iniciar navegador
                self.iniciar_navegador(headless=True)

                # Extraer oportunidades
                oportunidades = self.extraer_oportunidades_segmento_43()
                logging.info(f"Se encontraron {len(oportunidades)} oportunidades")

                oportunidades_relevantes = []

                # Analizar cada oportunidad
                for op in oportunidades:
                    # Verificar si es nueva
                    if self.verificar_nueva_oportunidad(op.nomenclatura):
                        logging.info(f"Nueva oportunidad detectada: {op.nomenclatura}")

                        # Descargar y analizar PDF si está disponible
                        if op.url_bases:
                            self.descargar_y_analizar_pdf(op)

                        # Evaluar compatibilidad
                        score, razones = self.evaluar_compatibilidad(op)
                        op.score_compatibilidad = score
                        op.razones_compatibilidad = razones

                        # Guardar en BD
                        self.guardar_oportunidad(op)

                        # Si es relevante (score > 50), agregar a alertas
                        if score > 50:
                            oportunidades_relevantes.append(op)
                            logging.info(f"  ✅ Relevante: {op.nomenclatura} (Score: {score:.0f}%)")

                # Enviar alertas si hay oportunidades relevantes
                if oportunidades_relevantes:
                    self.enviar_alerta(oportunidades_relevantes)

                # Cerrar navegador
                self.driver.quit()

                # Esperar próximo ciclo
                intervalo = self.config['monitoreo']['intervalo_minutos']
                logging.info(f"Esperando {intervalo} minutos para próximo monitoreo...")
                time.sleep(intervalo * 60)

            except Exception as e:
                logging.error(f"Error en monitoreo: {e}")
                if self.driver:
                    self.driver.quit()
                time.sleep(300)  # Esperar 5 minutos ante error

    def generar_reporte_diario(self):
        """Genera un reporte diario de oportunidades"""
        cursor = self.conn.cursor()

        # Oportunidades de los últimos 7 días
        fecha_limite = (datetime.now() - timedelta(days=7)).isoformat()

        cursor.execute("""
            SELECT nomenclatura, entidad, descripcion_procedimiento,
                   score_compatibilidad, dias_restantes, fecha_descubierta
            FROM oportunidades
            WHERE fecha_descubierta > ?
            ORDER BY score_compatibilidad DESC
        """, (fecha_limite,))

        oportunidades = cursor.fetchall()

        reporte = f"""
📊 REPORTE SEMANAL DE OPORTUNIDADES
Fecha: {datetime.now().strftime('%Y-%m-%d')}
Total oportunidades analizadas: {len(oportunidades)}

TOP 10 OPORTUNIDADES MÁS RELEVANTES:
"""
        for i, op in enumerate(oportunidades[:10], 1):
            reporte += f"""
{i}. {op[0]}
   Entidad: {op[1]}
   Descripción: {op[2][:80]}...
   Compatibilidad: {op[3]:.0f}%
   Días restantes: {op[4]}
"""

        # Guardar reporte
        with open(f"reporte_semanal_{datetime.now().strftime('%Y%m%d')}.txt", 'w') as f:
            f.write(reporte)

        return reporte

def main():
    """Función principal"""
    print("="*80)
    print(" AGENTE IA INTELIGENTE PARA LICITACIONES SEACE")
    print(" Segmento 43: Tecnología de la Información")
    print("="*80)

    # Verificar configuración
    if not os.path.exists('config_empresa.json'):
        print("\n⚠️ No se encontró config_empresa.json")
        print("Por favor, edita el archivo con los datos de tu empresa")
        return

    # Crear agente
    agente = AgenteIASeace()

    print(f"\n🤖 Agente configurado para: {agente.empresa['nombre']}")
    print(f"📋 Monitoreando {len(agente.empresa['palabras_clave_positivas'])} palabras clave")
    print(f"💰 Rango de montos: {agente.empresa['montos_preferidos']['minimo']:,} - {agente.empresa['montos_preferidos']['maximo']:,}")

    print("\n🚀 Iniciando monitoreo continuo...")
    print("Presiona Ctrl+C para detener\n")

    try:
        agente.monitorear_continuamente()
    except KeyboardInterrupt:
        print("\n\n✋ Monitoreo detenido por el usuario")
        print(agente.generar_reporte_diario())

if __name__ == "__main__":
    main()