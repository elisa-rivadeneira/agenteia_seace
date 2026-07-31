#!/usr/bin/env python3
"""
Generador de archivos Excel para oportunidades SEACE
Compatible con WhatsApp vía Evolution API
"""

import pandas as pd
from datetime import datetime
import os

class ExcelGeneratorSEACE:
    def __init__(self):
        """Inicializa el generador de Excel"""
        self.output_dir = 'reportes_excel'
        os.makedirs(self.output_dir, exist_ok=True)

    def generar_excel_oportunidades(self, oportunidades, filename=None):
        """
        Genera archivo Excel con las oportunidades

        Args:
            oportunidades: Lista de diccionarios con datos de oportunidades
            filename: Nombre del archivo (opcional)

        Returns:
            str: Path del archivo generado
        """
        if not oportunidades:
            raise ValueError("No hay oportunidades para exportar")

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'oportunidades_seace_{timestamp}.xlsx'

        filepath = os.path.join(self.output_dir, filename)

        df = pd.DataFrame(oportunidades)

        columnas_deseadas = [
            'nomenclatura',
            'entidad',
            'descripcion_item',
            'score_compatibilidad',
            'fecha_inicio',
            'fecha_fin',
            'fecha_presentacion',
            'moneda',
            'url_seace'
        ]

        columnas_finales = [col for col in columnas_deseadas if col in df.columns]
        df_final = df[columnas_finales]

        nombres_columnas = {
            'nomenclatura': 'Código',
            'entidad': 'Entidad',
            'descripcion_item': 'Descripción',
            'score_compatibilidad': 'Compatibilidad %',
            'fecha_inicio': 'Inicio Consultas',
            'fecha_fin': 'Fin Consultas',
            'fecha_presentacion': 'Presentación Propuestas',
            'moneda': 'Moneda',
            'url_seace': 'URL SEACE'
        }

        df_final = df_final.rename(columns=nombres_columnas)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Oportunidades')

            worksheet = writer.sheets['Oportunidades']

            for idx, col in enumerate(df_final.columns, 1):
                max_length = max(
                    df_final[col].astype(str).map(len).max(),
                    len(col)
                )
                adjusted_width = min(max_length + 2, 50)
                column_letter = chr(64 + idx)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        print(f"✅ Excel generado: {filepath}")
        return filepath

    def generar_excel_top_relevantes(self, oportunidades, limite=10, filename=None):
        """
        Genera Excel solo con las oportunidades más relevantes

        Args:
            oportunidades: Lista de oportunidades
            limite: Número máximo de oportunidades a incluir
            filename: Nombre del archivo

        Returns:
            str: Path del archivo generado
        """
        top_ops = sorted(
            oportunidades,
            key=lambda x: x.get('score_compatibilidad', 0),
            reverse=True
        )[:limite]

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'top_{limite}_oportunidades_{timestamp}.xlsx'

        return self.generar_excel_oportunidades(top_ops, filename)

    def generar_excel_filtrado(self, oportunidades, score_minimo=30, filename=None):
        """
        Genera Excel con oportunidades filtradas por score

        Args:
            oportunidades: Lista de oportunidades
            score_minimo: Score mínimo de compatibilidad
            filename: Nombre del archivo

        Returns:
            str: Path del archivo generado
        """
        filtradas = [
            op for op in oportunidades
            if op.get('score_compatibilidad', 0) >= score_minimo
        ]

        if not filtradas:
            raise ValueError(f"No hay oportunidades con score >= {score_minimo}%")

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'oportunidades_score_{score_minimo}+_{timestamp}.xlsx'

        return self.generar_excel_oportunidades(filtradas, filename)

def test_generator():
    """Prueba del generador de Excel"""
    import json
    import glob

    archivos = glob.glob('seace_todas_oportunidades_*.json')
    if not archivos:
        print("❌ No hay datos de oportunidades")
        return

    archivo_reciente = max(archivos, key=os.path.getctime)

    with open(archivo_reciente, 'r', encoding='utf-8') as f:
        data = json.load(f)

    oportunidades = data.get('oportunidades', [])

    if not oportunidades:
        print("❌ No hay oportunidades en el archivo")
        return

    generator = ExcelGeneratorSEACE()

    print("\n📊 Generando reportes Excel...")

    filepath_completo = generator.generar_excel_oportunidades(oportunidades)
    print(f"✅ Reporte completo: {filepath_completo}")

    filepath_top = generator.generar_excel_top_relevantes(oportunidades, limite=5)
    print(f"✅ Top 5: {filepath_top}")

    try:
        filepath_filtrado = generator.generar_excel_filtrado(oportunidades, score_minimo=30)
        print(f"✅ Filtrado (≥30%): {filepath_filtrado}")
    except ValueError as e:
        print(f"⚠️ {e}")

if __name__ == "__main__":
    test_generator()
