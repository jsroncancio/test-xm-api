import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt
import matplotlib.pyplot as plt

def generar_reporte_visual():
    objetoAPI = nxm.ReadDB()
    hoy = dt.datetime.now().date()
    df_gen, df_meta, fecha_final = None, None, None

    print(f"🔍 Buscando el reporte más reciente...")

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
        # 1. Procesamiento de Datos
        df_gen.columns = [c.lower() for c in df_gen.columns]
        df_meta.columns = [c.lower() for c in df_meta.columns]
        df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
        df['gwh'] = df.sum(axis=1, numeric_only=True) / 1_000_000
        
        resumen = df.groupby('values_enersource')['gwh'].sum().reset_index()
        total_dia = resumen['gwh'].sum()

        # 2. Definición de Bloques y Colores
        colores_dict = {
            'RAD SOLAR': 'yellow',
            'VIENTO': 'aquamarine',
            'AGUA': 'royalblue',
            'CARBON': 'black',
            'GAS': 'red',
            'OTROS': 'lightgrey'
        }
        
        # Mapeo de nombres para la gráfica circular
        resumen['color'] = resumen['values_enersource'].map(colores_dict).fillna('lightgrey')
        
        # 3. Cálculos de Brechas (Análisis Dinámico)
        g_sv = resumen[resumen['values_enersource'].isin(['RAD SOLAR', 'VIENTO'])]['gwh'].sum()
        g_fncer = resumen[resumen['values_enersource'].isin(['RAD SOLAR', 'VIENTO', 'BAGAZO', 'BIOMASA', 'BIOGAS'])]['gwh'].sum()
        g_termica = resumen[resumen['values_enersource'].isin(['GAS', 'CARBON', 'COMBUSTOLEO', 'ACPM'])]['gwh'].sum()

        # --- GENERACIÓN DE GRÁFICAS ---
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Gráfica 1: Circular (Balance por Bloques)
        resumen_pie = resumen.sort_values(by='gwh', ascending=False)
        ax1.pie(resumen_pie['gwh'], labels=resumen_pie['values_enersource'], 
                colors=resumen_pie['color'], autopct='%1.1f%%', startangle=140,
                textprops={'color':"grey" if 'black' in resumen_pie['color'].values else "black"})
        ax1.set_title(f"Balance de Generación - {fecha_final}", fontsize=14, fontweight='bold')

        # Gráfica 2: Barras (Análisis de Brechas)
        categorias = ['FNCER vs Térmica', 'Sol+Viento vs Térmica']
        valores_renov = [g_fncer, g_sv]
        valores_term = [g_termica, g_termica]
        
        x = np.arange(len(categorias))
        width = 0.35
        
        ax2.bar(x - width/2, valores_renov, width, label='Renovables/FNCER', color='limegreen')
        ax2.bar(x + width/2, valores_term, width, label='Térmica Fósil', color='salmon')
        
        ax2.set_ylabel('GWh')
        ax2.set_title('Comparativa de Brechas Energéticas', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categorias)
        ax2.legend()
        ax2.grid(axis='y', linestyle='--', alpha=0.7)

        # Guardar resultado
        plt.tight_layout()
        plt.savefig('reporte_energetico.png', dpi=300)
        print("✅ Reporte visual generado: reporte_energetico.png")

        # Mantener salida en consola
        print(f"\n🏆 RESUMEN EJECUTIVO - {fecha_final}")
        print(f"Total Generado: {total_dia:.2f} GWh")
        print(f"Brecha FNCER vs Térmica: {g_fncer - g_termica:.2f} GWh")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generar_reporte_visual()
