import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def reporte_refinado_transicion():
    objetoAPI = nxm.ReadDB()
    hoy = dt.datetime.now().date()
    df_gen, df_meta, fecha_final = None, None, None

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
        df_gen.columns = [c.lower() for c in df_gen.columns]
        df_meta.columns = [c.lower() for c in df_meta.columns]
        df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
        df['kwh_dia'] = df.sum(axis=1, numeric_only=True)
        
        resumen = df.groupby('values_enersource')['kwh_dia'].sum().reset_index()
        resumen['gwh'] = resumen['kwh_dia'] / 1_000_000
        total_dia = resumen['gwh'].sum()

        # BLOQUES DE ANÁLISIS
        g_sol_viento = resumen[resumen['values_enersource'].isin(['RAD SOLAR', 'VIENTO'])]['gwh'].sum()
        g_fncer = resumen[resumen['values_enersource'].isin(['RAD SOLAR', 'VIENTO', 'BAGAZO', 'BIOMASA', 'BIOGAS'])]['gwh'].sum()
        g_termica = resumen[resumen['values_enersource'].isin(['GAS', 'CARBON', 'COMBUSTOLEO', 'ACPM', 'FUELOIL'])]['gwh'].sum()
        g_hidro = resumen[resumen['values_enersource'] == 'AGUA']['gwh'].sum()

        def calcular_comparativa(valor_a, valor_b, nombre_a, nombre_b):
            diferencia = valor_a - valor_b
            porcentaje = (abs(diferencia) / valor_b * 100) if valor_b > 0 else 0
            if diferencia > 0:
                return f"✅ {nombre_a} generó {diferencia:.2f} GWh más que {nombre_b} (+{porcentaje:.2f}%)"
            elif diferencia < 0:
                return f"⚠️ {nombre_b} generó {abs(diferencia):.2f} GWh más que {nombre_a} (+{porcentaje:.2f}%)"
            else:
                return f"⚖️ Empate exacto entre {nombre_a} y {nombre_b}"

        print("\n" + "█"*65)
        print(f" 🏆 MONITOR DE TRANSICIÓN ENERGÉTICA - {fecha_final}")
        print("█" * 65)
        
        print(f"\n⚡ GENERACIÓN TOTAL: {total_dia:.2f} GWh")
        print("-" * 65)
        print(f"☀️💨 SOL+VIENTO: {g_sol_viento:8.2f} GWh | 🌱 FNCER: {g_fncer:8.2f} GWh")
        print(f"🔥 TÉRMICA:     {g_termica:8.2f} GWh | 💧 HIDRO: {g_hidro:8.2f} GWh")

        print("\n📈 ANÁLISIS DE BRECHAS Y COBERTURA:")
        print("-" * 65)
        
        # Comparativa 1: FNCER vs TÉRMICA
        print(f"🚀 FNCER vs TÉRMICA:")
        print(f"   {calcular_comparativa(g_fncer, g_termica, 'FNCER', 'Térmica')}")
        print(f"   Cobertura: {(g_fncer/g_termica*100):.2f}%")
        
        # Comparativa 2: SOL+VIENTO vs TÉRMICA
        print(f"\n⚡ SOL+VIENTO vs TÉRMICA:")
        print(f"   {calcular_comparativa(g_sol_viento, g_termica, 'Sol+Viento', 'Térmica')}")
        print(f"   Cobertura: {(g_sol_viento/g_termica*100):.2f}%")
        
        print("\n" + "█" * 65 + "\n")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reporte_refinado_transicion()
