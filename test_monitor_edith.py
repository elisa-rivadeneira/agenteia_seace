#!/usr/bin/env python3
"""Test rápido del monitor EDITH"""

from monitor_realtime import MonitorRealtimeSEACE

print("🧪 TEST MONITOR EDITH\n")

monitor = MonitorRealtimeSEACE()
print("\n✅ Monitor inicializado correctamente")

print("\n📡 Ejecutando escaneo de prueba...")
monitor.ejecutar_escaneo_completo()

print("\n✅ TEST COMPLETADO")
