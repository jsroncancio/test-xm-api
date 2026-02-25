import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def analizar_transicion_reciente():
    objetoAPI = nxm.ReadDB()
    hoy = dt.datetime.now().date()
    
    df_gen = None
    df_meta = None
    fecha_encontrada = None

    print(f"🔍 Buscando el reporte más reciente disponible...")

    # Buscamos desde hace 2 días (margen mínimo de XM) hasta 15 días atrás
    for i in range(2, 16):
        fecha_test = hoy - dt.timedelta(days=i)
        try:
            temp_gen = objetoAPI.request_data("Gene", "Recurso", fecha_test, fecha_test)
            if temp_gen is not None and not temp_gen.empty:
                df_gen = temp_gen
                fecha_encontrada = fecha_test
                # Si encontramos generación, traemos los metadatos para esa misma fecha
                df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha_test, fecha_test)
                break
        except:
            continue

    if df_gen is None:
        print("❌ No se encontraron datos en los últimos 15 días.")
        return

    try:
        # Normalizar columnas
        df_gen.columns = [c.lower() for c in df_gen.columns]
        df_meta.columns = [c.lower() for c in df_meta.columns]
        
        # Cruce de datos y suma de las 24 horas
        df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
        df['kwh_dia'] = df.sum(axis=1, numeric_only=True)
        
        resumen = df.groupby('values_enersource')['kwh_dia'].sum().reset_index()
        resumen['gwh'] = resumen['kwh_dia'] / 1_000_000
        total_dia = resumen['gwh'].sum()

        # CATEGORÍAS
        fncer_list = ['RAD SOLAR', 'VIENTO', 'BAGAZO', 'BIOMASA', 'BIOGAS']
        termica_list = ['GAS', 'CARBON', 'COMBUSTOLEO', 'ACPM', 'FUELOIL']
        
        g_fncer = resumen[resumen['values_enersource'].isin(fncer_list)]['gwh'].sum()
        g_termica = resumen[resumen['values_enersource'].isin(termica_list)]['gwh'].sum()
        g_hidro = resumen[resumen['values_enersource'] == 'AGUA']['gwh'].sum()

        # INDICADOR DE TRANSICIÓN
        brecha = g_termica - g_fncer
        indice_reemplazo = (g_fncer / g_termica * 100) if g_termica > 0 else 100

        print("\n" + "="*55)
        print(f"🚀 REPORTE DE TRANSICIÓN MÁS RECIENTE: {fecha_encontrada}")
        print("="*55)
        print(f"☀️ FNCER (Sol, Viento, Bio): {g_fncer:8.2f} GWh ({ (g_fncer/total_dia*100):.1f}%)")
        print(f"🔥 TÉRMICAS (Fósiles):       {g_termica:8.2f} GWh ({ (g_termica/total_dia*100):.1f}%)")
        print(f"💧 HIDROELÉCTRICA:           {g_hidro:8.2f} GWh ({ (g_hidro/total_dia*100):.1f}%)")
        print("-" * 55)
        
        if brecha > 0:
            print(f"📉 BRECHA: Faltan {brecha:.2f} GWh para igualar térmicas.")
        else:
            print(f"🏆 ¡HITO! FNCER superaron a las térmicas por {abs(brecha):.2f} GWh.")

        print(f"📊 ÍNDICE DE REEMPLAZO: {indice_reemplazo:.2f}%")
        print("="*55 + "\n")

    except Exception as e:
        print(f"❌ Error al procesar: {e}")

if __name__ == "__main__":
    analizar_transicion_reciente()
