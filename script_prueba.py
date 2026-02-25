import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def analisis_avanzado_transicion():
    objetoAPI = nxm.ReadDB()
    # Mantenemos los 15 días de margen para seguridad de datos
    fecha = (dt.datetime.now() - dt.timedelta(days=15)).date()
    
    print(f"--- ANALISIS DE MATRIZ ENERGETICA: {fecha} ---")
    
    try:
        # 1. Extracción de datos (Lógica validada)
        df_gen = objetoAPI.request_data("Gene", "Recurso", fecha, fecha)
        df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha, fecha)

        if df_gen is not None and not df_gen.empty:
            df_gen.columns = [c.lower() for c in df_gen.columns]
            df_meta.columns = [c.lower() for c in df_meta.columns]
            
            # 2. Cruce y Suma Diaria
            df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
            df['kwh_dia'] = df.sum(axis=1, numeric_only=True)
            
            # 3. Agrupación detallada inicial
            resumen = df.groupby('values_enersource')['kwh_dia'].sum().reset_index()
            resumen['gwh'] = resumen['kwh_dia'] / 1_000_000
            total_dia = resumen['gwh'].sum()

            # 4. DEFINICIÓN DE CATEGORÍAS (Análisis solicitado)
            # Definimos quién es quién según los nombres que nos dio XM
            fncer_list = ['RAD SOLAR', 'VIENTO', 'BAGAZO', 'BIOMASA', 'BIOGAS']
            termica_list = ['GAS', 'CARBON', 'COMBUSTOLEO', 'ACPM', 'FUELOIL']
            hidro_list = ['AGUA']

            # Cálculos de los 3 bloques
            g_fncer = resumen[resumen['values_enersource'].isin(fncer_list)]['gwh'].sum()
            g_hidro = resumen[resumen['values_enersource'].isin(hidro_list)]['gwh'].sum()
            g_termica = resumen[resumen['values_enersource'].isin(termica_list)]['gwh'].sum()
            
            g_renov_con_agua = g_hidro + g_fncer
            
            # 5. IMPRESIÓN DE RESULTADOS EN EL RUN
            print("\n" + "="*55)
            print(f"       📊 BALANCE DE TRANSICIÓN ENERGÉTICA")
            print("="*55)
            print(f"{'CATEGORÍA':<30} | {'GWh':<8} | {'%':<5}")
            print("-" * 55)
            
            # Bloque 1: Renovables SIN Agua (FNCER)
            p_fncer = (g_fncer / total_dia) * 100
            print(f"{'1. Renovables SIN Agua (FNCER)':<30} | {g_fncer:<8.2f} | {p_fncer:.2f}%")
            
            # Bloque 2: Renovables CON Agua (Total Limpias)
            p_renov_total = (g_renov_con_agua / total_dia) * 100
            print(f"{'2. Renovables CON Agua':<30} | {g_renov_con_agua:<8.2f} | {p_renov_total:.2f}%")
            
            # Bloque 3: Térmica (Fósiles)
            p_termica = (g_termica / total_dia) * 100
            print(f"{'3. Generación Térmica':<30} | {g_termica:<8.2f} | {p_termica:.2f}%")
            
            print("="*55)
            print(f"{'TOTAL GENERACIÓN DEL DÍA':<30} | {total_dia:<8.2f} | 100.00%")
            print("="*55)

            # Detalle por tecnología para doble verificación
            print("\n🔍 DESGLOSE DETALLADO POR TECNOLOGÍA:")
            resumen['%_relativo'] = (resumen['gwh'] / total_dia) * 100
            print(resumen[['values_enersource', 'gwh', '%_relativo']].sort_values(by='gwh', ascending=False).to_string(index=False, float_format="{:.2f}".format))

        else:
            print("⚠️ No se pudieron obtener los datos de XM.")

    except Exception as e:
        print(f"❌ Error en el análisis: {e}")

if __name__ == "__main__":
    analisis_avanzado_transicion()
