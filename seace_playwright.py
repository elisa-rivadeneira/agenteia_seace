#!/usr/bin/env python3
"""
Agente IA avanzado con Playwright para capturar llamadas API
"""

from playwright.sync_api import sync_playwright
import json
import asyncio
from typing import List, Dict

class SEACEAPIInterceptor:
    def __init__(self):
        self.api_calls = []
        self.procesos = []

    def interceptar_llamadas_api(self, segmento: str) -> List[Dict]:
        """Intercepta las llamadas API del frontend"""
        with sync_playwright() as p:
            # Lanzar navegador
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Interceptar requests de red
            def handle_request(request):
                if 'api' in request.url or 'seace' in request.url:
                    print(f"API Request: {request.method} {request.url}")
                    self.api_calls.append({
                        'url': request.url,
                        'method': request.method,
                        'headers': dict(request.headers)
                    })

            def handle_response(response):
                if 'api' in response.url and response.status == 200:
                    try:
                        data = response.json()
                        print(f"API Response: {response.url}")
                        self.procesos.append(data)
                    except:
                        pass

            # Configurar interceptores
            page.on("request", handle_request)
            page.on("response", handle_response)

            # Navegar al segmento
            url = f"https://prod4.seace.gob.pe/openegocio/#/lista/{segmento}"
            print(f"Navegando a: {url}")
            page.goto(url)

            # Esperar que cargue el contenido
            page.wait_for_timeout(5000)

            # Extraer datos del DOM si no se capturaron por API
            if not self.procesos:
                # Evaluar JavaScript en el contexto de la página
                data = page.evaluate("""
                    () => {
                        const rows = document.querySelectorAll('table tbody tr');
                        const procesos = [];
                        rows.forEach(row => {
                            const cells = row.querySelectorAll('td');
                            if (cells.length > 0) {
                                procesos.push({
                                    entidad: cells[0]?.innerText || '',
                                    nomenclatura: cells[1]?.innerText || '',
                                    objeto: cells[2]?.innerText || '',
                                    valor: cells[3]?.innerText || '',
                                    moneda: cells[4]?.innerText || '',
                                    fecha: cells[5]?.innerText || ''
                                });
                            }
                        });
                        return procesos;
                    }
                """)
                self.procesos = data

            browser.close()
            return self.procesos

    def descubrir_endpoints(self):
        """Descubre los endpoints API usados"""
        return self.api_calls

# Uso del agente
if __name__ == "__main__":
    agente = SEACEAPIInterceptor()

    # Buscar segmento 43
    print("Buscando procesos del segmento 43...")
    procesos = agente.interceptar_llamadas_api("43")

    print(f"\nProcesos encontrados: {len(procesos)}")

    # Mostrar endpoints descubiertos
    print("\nEndpoints API descubiertos:")
    for call in agente.api_calls:
        print(f"  {call['method']} {call['url']}")

    # Guardar resultados
    with open('seace_segmento_43.json', 'w', encoding='utf-8') as f:
        json.dump(procesos, f, ensure_ascii=False, indent=2)