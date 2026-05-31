#!/usr/bin/env python3
"""
Agente IA completo para monitoreo inteligente de SEACE
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
import smtplib
from email.mime.text import MIMEText
from dataclasses import dataclass
import schedule
import time

@dataclass
class Proceso:
    """Estructura de datos para un proceso de contratación"""
    ocid: str
    entidad: str
    nomenclatura: str
    objeto: str
    valor_referencial: float
    moneda: str
    fecha_publicacion: str
    segmento: str
    hash_id: str = None

    def __post_init__(self):
        if not self.hash_id:
            self.hash_id = hashlib.md5(
                f"{self.nomenclatura}{self.entidad}".encode()
            ).hexdigest()

class AgenteIASEACE:
    """Agente IA para monitoreo inteligente de contrataciones"""

    def __init__(self, db_path="seace_monitor.db"):
        self.db_path = db_path
        self._init_db()
        self.nuevos_procesos = []
        self.procesos_actualizados = []

    def _init_db(self):
        """Inicializa base de datos para tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS procesos (
                hash_id TEXT PRIMARY KEY,
                ocid TEXT,
                entidad TEXT,
                nomenclatura TEXT,
                objeto TEXT,
                valor_referencial REAL,
                moneda TEXT,
                fecha_publicacion TEXT,
                segmento TEXT,
                fecha_registro TIMESTAMP,
                ultima_actualizacion TIMESTAMP,
                estado TEXT DEFAULT 'activo',
                notificado INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                mensaje TEXT,
                fecha TIMESTAMP,
                proceso_id TEXT,
                enviado INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def analizar_cambios(self, procesos_actuales: List[Proceso]) -> Dict:
        """Analiza cambios vs datos históricos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        nuevos = []
        actualizados = []
        eliminados = []

        # Obtener procesos existentes
        cursor.execute("SELECT hash_id, valor_referencial FROM procesos WHERE segmento = ?",
                       (procesos_actuales[0].segmento,))
        procesos_db = {row[0]: row[1] for row in cursor.fetchall()}

        for proceso in procesos_actuales:
            if proceso.hash_id not in procesos_db:
                # Nuevo proceso
                nuevos.append(proceso)
                self._guardar_proceso(proceso, conn)
            elif procesos_db[proceso.hash_id] != proceso.valor_referencial:
                # Proceso actualizado
                actualizados.append(proceso)
                self._actualizar_proceso(proceso, conn)

        # Detectar procesos eliminados
        hash_ids_actuales = {p.hash_id for p in procesos_actuales}
        for hash_id in procesos_db:
            if hash_id not in hash_ids_actuales:
                eliminados.append(hash_id)

        conn.commit()
        conn.close()

        return {
            "nuevos": nuevos,
            "actualizados": actualizados,
            "eliminados": eliminados,
            "total": len(procesos_actuales)
        }

    def _guardar_proceso(self, proceso: Proceso, conn):
        """Guarda nuevo proceso en DB"""
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO procesos (
                hash_id, ocid, entidad, nomenclatura, objeto,
                valor_referencial, moneda, fecha_publicacion,
                segmento, fecha_registro, ultima_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            proceso.hash_id, proceso.ocid, proceso.entidad,
            proceso.nomenclatura, proceso.objeto,
            proceso.valor_referencial, proceso.moneda,
            proceso.fecha_publicacion, proceso.segmento,
            datetime.now(), datetime.now()
        ))

    def _actualizar_proceso(self, proceso: Proceso, conn):
        """Actualiza proceso existente"""
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE procesos
            SET valor_referencial = ?, ultima_actualizacion = ?
            WHERE hash_id = ?
        """, (proceso.valor_referencial, datetime.now(), proceso.hash_id))

    def generar_alerta(self, tipo: str, mensaje: str, proceso_id: Optional[str] = None):
        """Genera alertas para notificación"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alertas (tipo, mensaje, fecha, proceso_id)
            VALUES (?, ?, ?, ?)
        """, (tipo, mensaje, datetime.now(), proceso_id))
        conn.commit()
        conn.close()

    def analizar_patrones(self, segmento: str) -> Dict:
        """Análisis de patrones con IA"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Análisis temporal
        cursor.execute("""
            SELECT
                strftime('%H', fecha_publicacion) as hora,
                COUNT(*) as cantidad
            FROM procesos
            WHERE segmento = ?
            GROUP BY hora
            ORDER BY cantidad DESC
            LIMIT 5
        """, (segmento,))
        horas_pico = cursor.fetchall()

        # Entidades más activas
        cursor.execute("""
            SELECT entidad, COUNT(*) as cantidad
            FROM procesos
            WHERE segmento = ?
            GROUP BY entidad
            ORDER BY cantidad DESC
            LIMIT 10
        """, (segmento,))
        top_entidades = cursor.fetchall()

        # Tendencia de valores
        cursor.execute("""
            SELECT
                AVG(valor_referencial) as promedio,
                MAX(valor_referencial) as maximo,
                MIN(valor_referencial) as minimo
            FROM procesos
            WHERE segmento = ? AND moneda = 'PEN'
        """, (segmento,))
        estadisticas = cursor.fetchone()

        conn.close()

        return {
            "horas_pico_publicacion": horas_pico,
            "entidades_mas_activas": top_entidades,
            "estadisticas_valores": {
                "promedio": estadisticas[0],
                "maximo": estadisticas[1],
                "minimo": estadisticas[2]
            }
        }

    def predecir_oportunidades(self, segmento: str) -> List[Dict]:
        """Predice oportunidades basado en patrones históricos"""
        patrones = self.analizar_patrones(segmento)

        predicciones = []

        # Predicción basada en patrones temporales
        if patrones["horas_pico_publicacion"]:
            hora_pico = patrones["horas_pico_publicacion"][0][0]
            predicciones.append({
                "tipo": "temporal",
                "mensaje": f"Mayor probabilidad de nuevas publicaciones a las {hora_pico}:00 horas",
                "confianza": 0.75
            })

        # Predicción basada en entidades activas
        for entidad, cantidad in patrones["entidades_mas_activas"][:3]:
            if cantidad > 5:
                predicciones.append({
                    "tipo": "entidad",
                    "mensaje": f"{entidad} tiene alta actividad ({cantidad} procesos)",
                    "confianza": 0.8
                })

        return predicciones

    def generar_reporte(self, segmento: str) -> str:
        """Genera reporte inteligente"""
        analisis = self.analizar_patrones(segmento)
        predicciones = self.predecir_oportunidades(segmento)

        reporte = f"""
        === REPORTE INTELIGENTE SEACE - SEGMENTO {segmento} ===
        Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}

        RESUMEN EJECUTIVO:
        - Entidades más activas: {len(analisis['entidades_mas_activas'])}
        - Valor promedio: S/. {analisis['estadisticas_valores']['promedio']:,.2f}
        - Rango: S/. {analisis['estadisticas_valores']['minimo']:,.2f} - S/. {analisis['estadisticas_valores']['maximo']:,.2f}

        PATRONES DETECTADOS:
        - Horas pico de publicación: {', '.join([f"{h[0]}:00 ({h[1]} procesos)" for h in analisis['horas_pico_publicacion'][:3]])}

        TOP ENTIDADES:
        {chr(10).join([f"  {i+1}. {e[0]} - {e[1]} procesos" for i, e in enumerate(analisis['entidades_mas_activas'][:5])])}

        PREDICCIONES IA:
        {chr(10).join([f"  • {p['mensaje']} (Confianza: {p['confianza']:.0%})" for p in predicciones[:3]])}

        === FIN DEL REPORTE ===
        """
        return reporte

# Función principal de monitoreo
def monitorear_segmento_con_ia(segmento: str = "43"):
    """Función principal para monitoreo inteligente"""
    print(f"[{datetime.now()}] Iniciando monitoreo inteligente del segmento {segmento}")

    agente = AgenteIASEACE()

    # Aquí conectarías con el scraper de Selenium/Playwright
    # Por ahora simulamos datos
    procesos_ejemplo = [
        Proceso(
            ocid="ocds-example-001",
            entidad="MINISTERIO DE EJEMPLO",
            nomenclatura="LP-001-2024",
            objeto="Servicios de TI",
            valor_referencial=150000.00,
            moneda="PEN",
            fecha_publicacion="2024-01-15",
            segmento=segmento
        )
    ]

    # Analizar cambios
    cambios = agente.analizar_cambios(procesos_ejemplo)

    if cambios["nuevos"]:
        print(f"✅ {len(cambios['nuevos'])} nuevos procesos detectados")
        for p in cambios["nuevos"]:
            agente.generar_alerta("nuevo_proceso",
                                 f"Nuevo: {p.nomenclatura} - {p.objeto[:50]}",
                                 p.hash_id)

    # Generar reporte
    reporte = agente.generar_reporte(segmento)
    print(reporte)

    return cambios

if __name__ == "__main__":
    # Monitoreo único
    monitorear_segmento_con_ia("43")

    # Para monitoreo programado:
    # schedule.every(30).minutes.do(monitorear_segmento_con_ia, "43")
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)