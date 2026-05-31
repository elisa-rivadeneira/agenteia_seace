#!/usr/bin/env python3
"""
Agente IA para monitorear procesos SEACE en tiempo real
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import json
import time
from datetime import datetime

class SEACEAgent:
    def __init__(self, headless=True):
        """Inicializa el agente con navegador automatizado"""
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 10)

    def buscar_segmento(self, codigo_segmento):
        """Busca procesos por código de segmento CUBSO"""
        try:
            # Navegar al portal de Oportunidades de Negocio
            url = f"https://prod4.seace.gob.pe/openegocio/#/lista/{codigo_segmento}"
            print(f"Accediendo a: {url}")
            self.driver.get(url)

            # Esperar que cargue la tabla de resultados
            time.sleep(5)  # Esperar carga de Angular

            # Buscar elementos de la tabla
            procesos = []

            # Intentar encontrar la tabla de resultados
            tabla = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )

            # Extraer filas
            filas = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")

            for fila in filas:
                columnas = fila.find_elements(By.TAG_NAME, "td")
                if len(columnas) >= 6:
                    proceso = {
                        "entidad": columnas[0].text,
                        "nomenclatura": columnas[1].text,
                        "objeto": columnas[2].text,
                        "valor_referencial": columnas[3].text,
                        "moneda": columnas[4].text,
                        "fecha_publicacion": columnas[5].text,
                        "fecha_extraccion": datetime.now().isoformat()
                    }
                    procesos.append(proceso)

            return procesos

        except Exception as e:
            print(f"Error: {e}")
            return []

    def monitorear_segmento(self, codigo_segmento, intervalo_minutos=30):
        """Monitorea continuamente un segmento"""
        while True:
            print(f"\n[{datetime.now()}] Buscando segmento {codigo_segmento}...")
            procesos = self.buscar_segmento(codigo_segmento)

            if procesos:
                # Guardar en JSON
                filename = f"seace_segmento_{codigo_segmento}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(procesos, f, ensure_ascii=False, indent=2)
                print(f"Guardados {len(procesos)} procesos en {filename}")

                # Mostrar resumen
                df = pd.DataFrame(procesos)
                print("\nResumen de procesos encontrados:")
                print(df[['entidad', 'nomenclatura', 'valor_referencial']].head(10))
            else:
                print("No se encontraron procesos")

            print(f"\nEsperando {intervalo_minutos} minutos para próxima búsqueda...")
            time.sleep(intervalo_minutos * 60)

    def cerrar(self):
        """Cierra el navegador"""
        self.driver.quit()

# Ejemplo de uso
if __name__ == "__main__":
    agente = SEACEAgent(headless=False)  # False para ver el navegador

    # Buscar segmento 43 (Tecnología de la información)
    procesos = agente.buscar_segmento("43")

    if procesos:
        print(f"\nEncontrados {len(procesos)} procesos del segmento 43:")
        for p in procesos[:5]:
            print(f"- {p['nomenclatura']}: {p['objeto'][:50]}...")

    # Para monitoreo continuo:
    # agente.monitorear_segmento("43", intervalo_minutos=30)

    agente.cerrar()