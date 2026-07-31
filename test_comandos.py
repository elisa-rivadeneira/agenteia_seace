#!/usr/bin/env python3
"""
Script de verificación de comandos del agente
"""

import sys
import os

try:
    from agente_whatsapp import AgenteWhatsAppSEACE

    print("=" * 60)
    print("VERIFICACIÓN DE COMANDOS DEL AGENTE SEACE")
    print("=" * 60)

    agente = AgenteWhatsAppSEACE()

    print(f"\n✅ Agente inicializado correctamente")
    print(f"\n📋 Comandos registrados ({len(agente.comandos)}):")

    for comando in sorted(agente.comandos.keys()):
        print(f"  • {comando}")

    if '/excel' in agente.comandos:
        print(f"\n✅ ¡Comando /excel ENCONTRADO!")

        # Probar el comando
        print("\n🧪 Probando /excel...")
        try:
            respuesta = agente.procesar_comando('/excel')
            print(f"📤 Respuesta: {respuesta[:200]}...")
        except Exception as e:
            print(f"⚠️ Error al probar: {e}")
    else:
        print(f"\n❌ Comando /excel NO ENCONTRADO")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("VERIFICACIÓN COMPLETA")
    print("=" * 60)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
