import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def reporte_integral_transicion():
    objetoAPI = nxm.ReadDB()
    hoy = dt.datetime.now().date()
    
    df_gen, df_meta, fecha_final = None, None, None

    print(f"🔍 Buscando el reporte más reciente disponible...")

    # Buscador de frontera de datos
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

    if df_gen is None:
        print("❌ No se encontraron datos recientes.")
        return

    try:
        # 1. Procesamiento y Cruce
        df_gen.columns = [c.lower() for c in df_gen.columns]
        df_meta.columns = [c.lower() for c in df_meta.columns]
        df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
        df['kwh_dia'] = df.sum(axis=1, numeric_only=True)
        
        # 2. Agregación por fuente (Base para Eureka)
        resumen = df.groupby('values_enersource')['kwh_dia'].sum().reset_index()
        resumen['gwh'] = resumen['kwh_dia'] / 1_000_000
        total_dia = resumen['gwh'].sum()
        resumen['porcentaje'] = (resumen['gwh'] / total_dia) * 100
        resumen = resumen.sort_values(by='gwh', ascending=False)

        # 3. Categorización por Bloques (Análisis Estratégico)
        fncer_list = ['RAD SOLAR', 'VIENTO', 'BAGAZO', 'BIOMASA', 'BIOGAS']
        termica_list = ['GAS', 'CARBON', 'COMBUSTOLEO', 'ACPM', 'FUELOIL']
        
        g_fncer = resumen[resumen['values_enersource'].isin(fncer_list)]['gwh'].sum()
        g_termica = resumen[resumen['values_enersource'].isin(termica_list)]['gwh'].sum()
        g_hidro = resumen[resumen['values_enersource'] == 'AGUA']['gwh'].sum()
        
        # Indicadores de Brecha
        brecha = g_termica - g_fncer
        indice_reemplazo = (g_fncer / g_termica * 100) if g_termica > 0 else 100

        # --- SALIDA INTEGRAL AL RUN ---
        print("\n" + "█"*60)
        print(f" 🏆 MONITOR DE TRANSICIÓN ENERGÉTICA COLOMBIA - {fecha_final}")
        print("█" * 60)
        
        print("\n🔹 1. DESGLOSE DETALLADO POR TECNOLOGÍA (EUREKA):")
        print("-" * 60)
        print(resumen[['values_enersource', 'gwh', 'porcentaje']].to_string(index=False, float_format="{:.2f}".format))
        
        print("\n🔹 2. BALANCE ESTRATÉGICO POR BLOQUES:")
        print("-" * 60)
        print(f"☀️ FNCER (Limpia No Conv.):   {g_fncer:8.2f} GWh | {(g_fncer/total_dia*100):.2f}%")
        print(f"💧 HIDROELÉCTRICA (Limpia):   {g_hidro:8.2f} GWh | {(g_hidro/total_dia*100):.2f}%")
        print(f"🔥 TÉRMICA (Fósiles):         {g_termica:8.2f} GWh | {(g_termica/total_dia*100):.2f}%")
        
        print("\n🔹 3. INDICADOR CRÍTICO DE REEMPLAZO (FNCER vs TÉRMICA):")
        print("-" * 60)
        if brecha > 0:
            status = f"📉 BRECHA: Faltan {brecha:.2f} GWh para igualar térmicas."
        else:
            status = f"🏆 ¡HITO! FNCER superaron a las térmicas por {abs(brecha):.2f} GWh."
        
        print(status)
        print(f"📈 ÍNDICE DE REEMPLAZO: {indice_reemplazo:.2f}%")
        print(f"✨ Las renovables modernas ya cubren el {indice_reemplazo:.1f}% de la térmica.")
        
        print("\n" + "█" * 60)
        print(f" GENERACIÓN TOTAL DEL DÍA: {total_dia:.2f} GWh")
        print("█" * 60 + "\n")

    except Exception as e:
        print(f"❌ Error en el reporte integral: {e}")

if __name__ == "__main__":
    reporte_integral_transicion()
