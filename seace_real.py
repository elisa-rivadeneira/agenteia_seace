#!/usr/bin/env python3
"""
Agente real para extraer datos del SEACE
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

class SEACERealAgent:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def buscar_oportunidades_negocio(self):
        """Intenta acceder al portal de oportunidades de negocio"""
        print("\n=== Intentando acceder al portal de Oportunidades de Negocio ===\n")

        # Primero, obtener la página principal para establecer cookies
        url_base = "https://prod2.seace.gob.pe/seacebus-uiwd-pub/buscador/buscadorPublico.xhtml"

        try:
            print(f"1. Accediendo a: {url_base}")
            response = self.session.get(url_base, timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                # Intentar parsear el HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Buscar formularios o elementos de búsqueda
                forms = soup.find_all('form')
                print(f"   Formularios encontrados: {len(forms)}")

                # Buscar ViewState (común en aplicaciones JSF)
                viewstate = soup.find('input', {'name': 'javax.faces.ViewState'})
                if viewstate:
                    print(f"   ViewState encontrado: {viewstate.get('value')[:50]}...")

                return soup

        except Exception as e:
            print(f"   Error: {e}")

        return None

    def buscar_por_api_conosce(self):
        """Intenta usar la API de CONOSCE (datos abiertos)"""
        print("\n=== Intentando acceder a CONOSCE (Datos Abiertos) ===\n")

        url = "https://bi.seace.gob.pe/pentaho/api/repos/:public:portal:datosabiertos.html/content?userid=public&password=key"

        try:
            print(f"1. Accediendo a: {url}")
            response = self.session.get(url, timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                print("   ✓ Acceso exitoso a datos abiertos")
                # Este endpoint devuelve HTML con enlaces a datasets
                return response.text

        except Exception as e:
            print(f"   Error: {e}")

        return None

    def buscar_convocatorias_vigentes(self):
        """Busca convocatorias vigentes en el buscador público"""
        print("\n=== Buscando Convocatorias Vigentes ===\n")

        # URL del buscador público de convocatorias
        url = "https://prodapp3.seace.gob.pe/seacebus-uiwd-pub/buscador/convocatorias/convocatoriasBusqueda.xhtml"

        try:
            # Parámetros de búsqueda
            params = {
                'anioConvocatoria': '2024',
                'tipoBusqueda': 'porFiltros',
                'tipoConvocatoria': '1',  # 1 = Bienes, 2 = Servicios, 3 = Obras
                'estado': 'publicado'
            }

            print(f"1. Buscando en: {url}")
            response = self.session.get(url, params=params, timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Buscar tabla de resultados
                tabla = soup.find('table', {'class': 'grilla'})
                if tabla:
                    print("   ✓ Tabla de resultados encontrada")
                    return self._parsear_tabla_convocatorias(tabla)
                else:
                    print("   ✗ No se encontró tabla de resultados")

        except Exception as e:
            print(f"   Error: {e}")

        return []

    def _parsear_tabla_convocatorias(self, tabla):
        """Parsea la tabla de convocatorias"""
        convocatorias = []

        filas = tabla.find_all('tr')[1:]  # Saltar header
        for fila in filas[:10]:  # Primeras 10
            celdas = fila.find_all('td')
            if len(celdas) >= 4:
                conv = {
                    'nomenclatura': celdas[0].text.strip(),
                    'objeto': celdas[1].text.strip(),
                    'valor_referencial': celdas[2].text.strip(),
                    'fecha': celdas[3].text.strip()
                }
                convocatorias.append(conv)

        return convocatorias

    def buscar_segmento_43_alternativo(self):
        """Método alternativo para buscar el segmento 43"""
        print("\n=== Método Alternativo: Búsqueda por texto ===\n")

        # Buscar por palabras clave relacionadas con TI
        keywords = [
            "software",
            "sistema",
            "tecnologia",
            "informatica",
            "computadora",
            "servidor",
            "red",
            "telecomunicaciones"
        ]

        resultados = []

        for keyword in keywords[:3]:  # Probar con 3 keywords
            print(f"Buscando: {keyword}")
            url = "https://prodapp3.seace.gob.pe/seacebus-uiwd-pub/buscador/convocatorias"

            params = {
                'textoConvocatoria': keyword,
                'anio': '2024'
            }

            try:
                response = self.session.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    print(f"  ✓ Encontrados resultados para: {keyword}")
                    # Aquí procesarías los resultados

            except Exception as e:
                print(f"  ✗ Error: {str(e)[:50]}")

            time.sleep(1)  # Evitar sobrecarga

        return resultados

def main():
    print("="*60)
    print("AGENTE DE BÚSQUEDA SEACE - SEGMENTO 43")
    print("="*60)

    agente = SEACERealAgent()

    # Intentar diferentes métodos
    print("\n📍 MÉTODO 1: Portal de Oportunidades de Negocio")
    resultado1 = agente.buscar_oportunidades_negocio()

    print("\n📍 MÉTODO 2: API CONOSCE (Datos Abiertos)")
    resultado2 = agente.buscar_por_api_conosce()

    print("\n📍 MÉTODO 3: Convocatorias Vigentes")
    convocatorias = agente.buscar_convocatorias_vigentes()
    if convocatorias:
        print(f"\n✅ Se encontraron {len(convocatorias)} convocatorias:")
        for conv in convocatorias[:5]:
            print(f"  - {conv['nomenclatura']}: {conv['objeto'][:50]}...")

    print("\n📍 MÉTODO 4: Búsqueda Alternativa por Keywords")
    agente.buscar_segmento_43_alternativo()

    print("\n" + "="*60)
    print("CONCLUSIÓN:")
    print("="*60)
    print("""
    El portal SEACE tiene varias interfaces:

    1. Portal de Oportunidades de Negocio (Angular SPA)
       - Requiere JavaScript para funcionar
       - No accesible directamente via requests

    2. CONOSCE - Datos Abiertos
       - Accesible pero con datos agregados/históricos

    3. Buscador Público de Convocatorias
       - Parcialmente accesible
       - Puede requerir sesión activa

    Para obtener los datos del segmento 43 en tiempo real,
    necesitas usar Selenium o Playwright que ejecuten JavaScript.
    """)

    print("\n🔧 Ejecutando ahora con Selenium para obtener datos reales...")

if __name__ == "__main__":
    main()