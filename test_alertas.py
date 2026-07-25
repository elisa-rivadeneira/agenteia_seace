#!/usr/bin/env python3
"""
Script de prueba para el sistema de alertas
"""

from scheduler_alertas import AlertasAutomaticas
from datetime import datetime

def test_sistema_alertas():
    print("="*80)
    print(" TEST DEL SISTEMA DE ALERTAS AUTOMÁTICAS")
    print("="*80)
    print(f"\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

    alertas = AlertasAutomaticas()

    print("\n🧪 Ejecutando escaneo de prueba...")
    print("-" * 80)

    try:
        alertas.ejecutar_escaneo()
        print("\n" + "="*80)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print("="*80)
    except Exception as e:
        print(f"\n❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sistema_alertas()
