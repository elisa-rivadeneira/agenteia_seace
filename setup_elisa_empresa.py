#!/usr/bin/env python3
import json
from database_mysql import guardar_empresa_usuario

with open('config_empresa.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

empresa_data = {
    'nombre': config['empresa']['nombre'],
    'ruc': config['empresa']['ruc'],
    'palabras_positivas': config['empresa']['palabras_clave_positivas'],
    'palabras_negativas': config['empresa']['palabras_clave_negativas']
}

numero_elisa = '51967717179'

if guardar_empresa_usuario(numero_elisa, empresa_data):
    print(f"✅ Empresa configurada para usuario elisa ({numero_elisa})")
    print(f"   📝 Nombre: {empresa_data['nombre']}")
    print(f"   🏢 RUC: {empresa_data['ruc']}")
    print(f"   ✅ Palabras positivas: {len(empresa_data['palabras_positivas'])} palabras")
    print(f"   ❌ Palabras negativas: {len(empresa_data['palabras_negativas'])} palabras")
else:
    print("❌ Error al configurar empresa")
