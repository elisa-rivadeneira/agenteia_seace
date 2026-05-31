#!/usr/bin/env python3
"""
Buscar Evolution API en puertos comunes
"""

import requests
import json

def buscar_evolution_api():
    """Busca Evolution API en puertos comunes"""

    puertos_comunes = [3000, 3001, 5000, 5001, 8000, 8001, 8080, 9000, 9001]
    api_key = "429683C4C977415CAAFCCE10F7D57E11"

    print("🔍 BUSCANDO EVOLUTION API...")
    print("=" * 40)

    for puerto in puertos_comunes:
        url_base = f"http://localhost:{puerto}"

        try:
            print(f"🔍 Probando puerto {puerto}...")

            # Probar endpoint básico
            response = requests.get(f"{url_base}/", timeout=3)

            if response.status_code == 200:
                content = response.text[:200]
                print(f"✅ Puerto {puerto} responde: {content[:50]}...")

                # Probar si es Evolution API
                try:
                    headers = {'apikey': api_key}
                    api_response = requests.get(f"{url_base}/instance/fetchInstances",
                                              headers=headers, timeout=5)

                    if api_response.status_code == 200:
                        print(f"🎉 ¡EVOLUTION API ENCONTRADO EN PUERTO {puerto}!")
                        instances = api_response.json()
                        print(f"📱 Instancias: {len(instances)}")
                        return url_base

                except Exception:
                    pass

        except Exception:
            pass

    print("❌ No se encontró Evolution API en puertos comunes")
    return None

if __name__ == "__main__":
    buscar_evolution_api()