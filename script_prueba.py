import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def reporte_integral_v2():
    objetoAPI = nxm.ReadDB()
    hoy = dt.datetime.now().date()
    df_gen, df_meta, fecha_final = None, None, None

    print(f"🔍 Buscando el reporte más reciente...")

    for i in range(2, 16):
        fecha_test = hoy - dt.timedelta(days=i)
        try:
            temp_gen = objetoAPI.request_data("Gene", "Recurso", fecha_test, fecha_test)
            if temp_gen is not None and not temp_gen.empty:
                df_gen = temp_gen
                fecha_final = fecha_test
                df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha_test, fecha_test)
                break
        except:
            continue

    if df_gen is None: return

    try:
        df_gen.columns = [c.lower() for c in df_gen.columns]
        df_meta.columns = [c.lower() for c in df_meta.columns]
        df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
        df['kwh_dia'] = df.sum(axis=1, numeric_only=True)
        
        resumen = df.groupby('values_enersource')['kwh_dia'].sum().reset_index()
        resumen['gwh'] = resumen['kwh_dia'] / 1_000_000
        total_dia = resumen['gwh'].sum()

        # CATEGORÍAS TÉCNICAS
        sol_viento_list = ['RAD SOLAR', 'VIENTO']
        fncer_total_list = ['RAD SOLAR', 'VIENTO', 'BAGAZO', 'BIOMASA', 'BIOGAS']
        termica_list = ['GAS', 'CARBON', 'COMBUSTOLEO', 'ACPM', 'FUELOIL']
        
        g_sol_viento = resumen[resumen['values_enersource'].isin(sol_viento_list)]['gwh'].sum()
        g_fncer = resumen[resumen['values_enersource'].isin(fncer_total_list)]['gwh'].sum()
        g_termica = resumen[resumen['values_enersource'].isin(termica_list)]['gwh'].sum()
        g_hidro = resumen[resumen['values_enersource'] == 'AGUA']['gwh'].sum()

        # --- SALIDA AL RUN ---
        print("\n" + "█"*60)
        print(f" 🏆 MONITOR DE TRANSICIÓN ENERGÉTICA - {fecha_final}")
        print("█" * 60)
        
        print("\n📊 1. DESGLOSE POR BLOQUES:")
        print(f"{'BLOQUE':<25} | {'GWh':<8} | {'%':<5}")
        print("-" * 45)
        print(f"{'☀️💨 SOL + VIENTO':<25} | {g_sol_viento:<8.2f} | {(g_sol_viento/total_dia*100):.2f}%")
        print(f"{'🌱 FNCER TOTAL':<25} | {g_fncer:<8.2f} | {(g_fncer/total_dia*100):.2f}%")
        print(f"{'💧 HIDROELÉCTRICA':<25} | {g_hidro:<8.2f} | {(g_hidro/total_dia*100):.2f}%")
        print(f"{'🔥 TÉRMICA FÓSIL':<25} | {g_termica:<8.2f} | {(g_termica/total_dia*100):.2f}%")
        
        print("\n📈 2. INDICADORES DE SUSTITUCIÓN:")
        print("-" * 45)
        # Índice de Reemplazo (FNCER vs Térmica)
        indice = (g_fncer / g_termica * 100) if g_termica > 0 else 100
        print(f"🚀 FNCER vs TÉRMICA: {indice:.2f}% de cobertura")
        
        # Nueva métrica: Sol+Viento vs Térmica
        indice_sv = (g_sol_viento / g_termica * 100) if g_termica > 0 else 100
        print(f"⚡ SOL+VIENTO vs TÉRMICA: {indice_sv:.2f}% de cobertura")
        
        if g_sol_viento > g_termica:
            print("✨ ¡HITO! El Sol y el Viento solos ya superan a toda la Térmica.")
            
        print("\n" + "█" * 60)
        print(f" GENERACIÓN TOTAL: {total_dia:.2f} GWh")
        print("█" * 60 + "\n")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reporte_integral_v2()
