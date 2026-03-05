import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def generar_dashboard_pro():
    objetoAPI = nxm.ReadDB()
    hoy = dt.datetime.now().date()
    df_gen, df_meta, fecha_final = None, None, None

    print(f"🔍 Iniciando extracción de datos XM...")

    # Buscamos el día más reciente con datos (2-15 días de rezago)
    for i in range(2, 16):
        fecha_test = hoy - dt.timedelta(days=i)
        try:
            temp_gen = objetoAPI.request_data("Gene", "Recurso", fecha_test, fecha_test)
            if temp_gen is not None and not temp_gen.empty:
                df_gen, fecha_final = temp_gen, fecha_test
                df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha_test, fecha_test)
                break
        except: continue

    if df_gen is None: 
        print("❌ No se encontraron datos recientes.")
        return

    try:
        # 1. Procesamiento de Datos
        df_gen.columns = [c.lower() for c in df_gen.columns]
        df_meta.columns = [c.lower() for c in df_meta.columns]
        df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
        df['gwh'] = df.sum(axis=1, numeric_only=True) / 1_000_000
        
        resumen = df.groupby('values_enersource')['gwh'].sum().reset_index()
        total_dia = resumen['gwh'].sum()

        # 2. Definición de Bloques y Colores Solicitados
        colores_dict = {
            'RAD SOLAR': '#FFD700',   # Amarillo
            'VIENTO': '#7FFFD4',      # Aguamarina
            'AGUA': '#1E90FF',        # Azul
            'CARBON': '#2F4F4F',      # Gris oscuro (Negro visual)
            'GAS': '#FF4500',          # Rojo
        }

        g_fncer = resumen[resumen['values_enersource'].isin(['RAD SOLAR', 'VIENTO', 'BAGAZO', 'BIOMASA', 'BIOGAS'])]['gwh'].sum()
        g_termica = resumen[resumen['values_enersource'].isin(['GAS', 'CARBON', 'COMBUSTOLEO', 'ACPM'])]['gwh'].sum()

        # --- DISEÑO DEL DASHBOARD ---
        plt.style.use('ggplot')
        fig = plt.figure(figsize=(14, 10), facecolor='white')
        gs = fig.add_gridspec(3, 2, height_ratios=[0.2, 1.2, 0.8])

        # A. Encabezado
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.5, f"MONITOR DE TRANSICIÓN ENERGÉTICA COLOMBIA\nReporte Diario de Generación - {fecha_final}", 
                      ha='center', va='center', fontsize=18, fontweight='bold', color='#333333')

        # B. Ranking de Generación (Barras Horizontales) - MUCHO MEJOR QUE LA TORTA
        ax1 = fig.add_subplot(gs[1, :])
        resumen_sorted = resumen.sort_values('gwh', ascending=True)
        colors_bars = [colores_dict.get(x, '#D3D3D3') for x in resumen_sorted['values_enersource']]
        
        bars = ax1.barh(resumen_sorted['values_enersource'], resumen_sorted['gwh'], color=colors_bars, edgecolor='#555555')
        ax1.set_title("Mezcla de Generación por Fuente (GWh)", fontsize=14, pad=10)
        ax1.set_xlabel("Gigavatios-hora (GWh)")
        
        for bar in bars:
            width = bar.get_width()
            ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width:.2f}', va='center', fontsize=11, fontweight='bold')

        # C. Barra de Progreso de la Transición (Brecha)
        ax2 = fig.add_subplot(gs[2, 0])
        categorias = ['Térmica Fósil', 'FNCER']
        valores = [g_termica, g_fncer]
        colores_brecha = ['#FF4500', '#32CD32'] # Rojo vs Verde
        
        ax2.bar(categorias, valores, color=colores_brecha, alpha=0.8, width=0.6)
        ax2.set_title("Carrera de la Transición: FNCER vs Fósiles", fontsize=12, fontweight='bold')
        ax2.set_ylabel("GWh")

        # D. Texto Informativo y Logo
        ax_info = fig.add_subplot(gs[2, 1])
        ax_info.axis('off')
        cobertura = (g_fncer / g_termica * 100) if g_termica > 0 else 100
        txt_info = (f"Resumen Ejecutivo:\n"
                    f"• Generación Total: {total_dia:.2f} GWh\n"
                    f"• Cobertura FNCER/Térmica: {cobertura:.1f}%\n"
                    f"• Brecha Actual: {abs(g_termica - g_fncer):.2f} GWh")
        ax_info.text(0.1, 0.5, txt_info, va='center', fontsize=13, linespacing=1.8, 
                     bbox=dict(facecolor='none', edgecolor='#CCCCCC', boxstyle='round,pad=1'))

        # Inserción de Logo (con manejo de error)
        if os.path.exists("Logo-PNG.png"):
            logo = mpimg.imread("Logo-PNG.png")
            imagebox = OffsetImage(logo, zoom=0.15)
            ab = AnnotationBbox(imagebox, (0.85, 0.15), xycoords=ax_info.transAxes, frameon=False)
            ax_info.add_artist(ab)

        plt.tight_layout()
        plt.savefig('dashboard_generacion.png', dpi=200, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Dashboard guardado exitosamente: dashboard_generacion.png")
        print(f"🏆 Cobertura FNCER: {cobertura:.2f}%")

    except Exception as e:
        print(f"❌ Error en la generación del dashboard: {e}")

if __name__ == "__main__":
    generar_dashboard_pro()
