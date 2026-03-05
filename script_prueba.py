import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def calcular_comparativa(valor_a, nombre_a, valor_b, nombre_b):
    """Genera el texto dinámico y color para la comparativa."""
    if valor_a > valor_b:
        diff = valor_a - valor_b
        pct = (diff / valor_b * 100) if valor_b > 0 else 100
        txt = f"✅ {nombre_a} superó a {nombre_b} por {diff:.2f} GWh ({pct:.1f}%)"
        color = '#228B22' # Verde
    else:
        diff = valor_b - valor_a
        pct = (diff / valor_a * 100) if valor_a > 0 else 100
        txt = f"⚠️ {nombre_b} superó a {nombre_a} por {diff:.2f} GWh ({pct:.1f}%)"
        color = '#D22B2B' # Rojo
    return txt, color

def generar_dashboard_tecnico():
    objetoAPI = nxm.ReadDB()
    hoy = dt.datetime.now().date()
    df_gen, df_meta, fecha_final = None, None, None

    print(f"🔍 Extrayendo datos de XM...")

    for i in range(2, 16):
        fecha_test = hoy - dt.timedelta(days=i)
        try:
            temp_gen = objetoAPI.request_data("Gene", "Recurso", fecha_test, fecha_test)
            if temp_gen is not None and not temp_gen.empty:
                df_gen, fecha_final = temp_gen, fecha_test
                df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha_test, fecha_test)
                break
        except: continue

    if df_gen is None: return

    try:
        # 1. Procesamiento
        df_gen.columns = [c.lower() for c in df_gen.columns]
        df_meta.columns = [c.lower() for c in df_meta.columns]
        df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
        df['gwh'] = df.sum(axis=1, numeric_only=True) / 1_000_000
        resumen = df.groupby('values_enersource')['gwh'].sum().reset_index()

        # 2. Variables para comparativas
        v_solar = resumen[resumen['values_enersource'] == 'RAD SOLAR']['gwh'].sum()
        v_viento = resumen[resumen['values_enersource'] == 'VIENTO']['gwh'].sum()
        v_carbon = resumen[resumen['values_enersource'] == 'CARBON']['gwh'].sum()
        v_gas = resumen[resumen['values_enersource'] == 'GAS']['gwh'].sum()
        
        # 3. Lógica dinámica del Resumen Ejecutivo
        rep1_txt, rep1_col = calcular_comparativa(v_solar, "Solar", v_carbon, "Carbón")
        rep2_txt, rep2_col = calcular_comparativa(v_solar, "Solar", v_gas, "Gas")
        rep3_txt, rep3_col = calcular_comparativa(v_solar + v_viento, "Solar + Viento", v_carbon + v_gas, "Carbón + Gas")

        # 4. Diseño Visual
        plt.style.use('seaborn-v0_8-whitegrid')
        fig = plt.figure(figsize=(15, 12), facecolor='white')
        gs = fig.add_gridspec(3, 2, height_ratios=[0.3, 1.2, 1.0])

        # A. Título Superior
        ax_header = fig.add_subplot(gs[0, :])
        ax_header.axis('off')
        ax_header.text(0.5, 0.5, f"ANÁLISIS TÉCNICO DE TRANSICIÓN ENERGÉTICA\nColombia - Reporte del {fecha_final}", 
                       ha='center', va='center', fontsize=22, fontweight='bold', color='#1A5276')

        # B. Gráfica 1: Mezcla de Generación (Ranking Completo)
        ax1 = fig.add_subplot(gs[1, :])
        res_sorted = resumen.sort_values('gwh', ascending=True)
        col_map = {'RAD SOLAR': 'yellow', 'VIENTO': 'aquamarine', 'AGUA': 'royalblue', 'CARBON': 'black', 'GAS': 'red'}
        colors = [col_map.get(x, '#BDC3C7') for x in res_sorted['values_enersource']]
        
        bars = ax1.barh(res_sorted['values_enersource'], res_sorted['gwh'], color=colors, edgecolor='#566573', linewidth=1)
        ax1.set_title("Matriz de Generación SIN (GWh)", fontsize=16, fontweight='bold', pad=15)
        for b in bars:
            ax1.text(b.get_width()+0.8, b.get_y()+b.get_height()/2, f'{b.get_width():.2f}', va='center', fontsize=11, fontweight='bold')

        # C. Gráfica 2: Carreras Críticas (Solar, Viento, Carbón, Gas)
        ax2 = fig.add_subplot(gs[2, 0])
        labels_c = ['Solar', 'Viento', 'Carbón', 'Gas']
        valores_c = [v_solar, v_viento, v_carbon, v_gas]
        colores_c = ['yellow', 'aquamarine', 'black', 'red']
        
        ax2.bar(labels_c, valores_c, color=colores_c, edgecolor='grey', alpha=0.85)
        ax2.set_title("Comparativa de Tecnologías Clave", fontsize=14, fontweight='bold')
        ax2.set_ylabel("GWh")

        # D. Resumen Ejecutivo Dinámico
        ax3 = fig.add_subplot(gs[2, 1])
        ax3.axis('off')
        ax3.text(0, 0.9, "RESUMEN EJECUTIVO DE IMPACTO:", fontsize=15, fontweight='bold', color='#1A5276')
        
        # Posicionamiento de los 3 reportes
        ax3.text(0.05, 0.7, rep1_txt, fontsize=12, fontweight='bold', color=rep1_col, bbox=dict(facecolor='white', alpha=0.9, edgecolor=rep1_col, boxstyle='round,pad=0.5'))
        ax3.text(0.05, 0.45, rep2_txt, fontsize=12, fontweight='bold', color=rep2_col, bbox=dict(facecolor='white', alpha=0.9, edgecolor=rep2_col, boxstyle='round,pad=0.5'))
        ax3.text(0.05, 0.2, rep3_txt, fontsize=12, fontweight='bold', color=rep3_col, bbox=dict(facecolor='white', alpha=0.9, edgecolor=rep3_col, boxstyle='round,pad=0.5'))

        # Logo
        if os.path.exists("Logo-PNG.png"):
            logo = mpimg.imread("Logo-PNG.png")
            ax3.add_artist(AnnotationBbox(OffsetImage(logo, zoom=0.18), (0.85, 0.05), frameon=False, xycoords='axes fraction'))

        plt.tight_layout()
        plt.savefig('dashboard_generacion.png', dpi=250, bbox_inches='tight')
        print(f"✅ Dashboard Técnico Generado.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generar_dashboard_tecnico()
