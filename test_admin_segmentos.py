#!/usr/bin/env python3
"""
Test completo del flujo de edición de segmentos en el admin
"""

import requests
import json
from database_manager import obtener_usuario

def test_edicion_segmentos():
    print("🧪 TEST: Edición de segmentos por usuario\n")

    s = requests.Session()

    # 1. Login
    print("1️⃣ Login al admin...")
    r = s.post('http://localhost:5000/admin/login', data={'password': 'admin123'}, allow_redirects=True)
    if r.status_code == 200 and 'Dashboard' in r.text:
        print("   ✅ Login exitoso")
    else:
        print(f"   ❌ Login falló: {r.status_code}")
        return

    # 2. Ver usuario actual
    print("\n2️⃣ Estado inicial del usuario...")
    usuario = obtener_usuario('51967717179')
    segmentos_iniciales = usuario.get('segmentos', [])
    print(f"   Usuario: {usuario['nombre']}")
    print(f"   Segmentos iniciales: {segmentos_iniciales}")

    # 3. Cambiar segmentos (agregar 81, quitar 80)
    print("\n3️⃣ Modificando segmentos...")
    nuevos_segmentos = ['43', '72', '81']  # Quitamos 80, agregamos 81

    r = s.post('http://localhost:5000/admin/usuarios/configurar-segmentos', json={
        'numero': '51967717179',
        'segmentos': nuevos_segmentos
    })

    result = r.json()
    if result.get('success'):
        print(f"   ✅ Actualización exitosa")
    else:
        print(f"   ❌ Error: {result.get('error')}")
        return

    # 4. Verificar cambios
    print("\n4️⃣ Verificando cambios en la base de datos...")
    usuario = obtener_usuario('51967717179')
    segmentos_finales = usuario.get('segmentos', [])
    print(f"   Segmentos finales: {segmentos_finales}")

    if segmentos_finales == nuevos_segmentos:
        print("   ✅ Segmentos actualizados correctamente")
    else:
        print(f"   ❌ Esperado: {nuevos_segmentos}, obtenido: {segmentos_finales}")

    # 5. Verificar que el HTML refleja los cambios
    print("\n5️⃣ Verificando que el HTML muestra los nuevos segmentos...")
    r = s.get('http://localhost:5000/admin/usuarios')

    for seg in nuevos_segmentos:
        if f'<span class="badge" style="background: #667eea; color: white; margin-right: 5px;">\n                                        {seg}' in r.text:
            print(f"   ✅ Segmento {seg} visible en HTML")
        else:
            print(f"   ⚠️ Segmento {seg} no encontrado en HTML")

    # 6. Restaurar estado original
    print("\n6️⃣ Restaurando segmentos originales...")
    s.post('http://localhost:5000/admin/usuarios/configurar-segmentos', json={
        'numero': '51967717179',
        'segmentos': segmentos_iniciales
    })

    usuario = obtener_usuario('51967717179')
    if usuario.get('segmentos') == segmentos_iniciales:
        print(f"   ✅ Restaurado a: {segmentos_iniciales}")

    print("\n✅ TEST COMPLETADO")

if __name__ == "__main__":
    test_edicion_segmentos()
