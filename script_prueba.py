import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def validar_datos_en_run():
    objetoAPI = nxm.ReadDB()
    
    # Usamos 15 días atrás para garantizar éxito en la consulta
    fecha = (dt.datetime.now() - dt.timedelta(days=15)).date()
    
    print(f"--- DIAGNÓSTICO DE CONSOLA PARA EL {fecha} ---")
    
    try:
        # 1. Extracción de datos
        print("📥 Descargando generación (Gene)...")
        df_gen = objetoAPI.request_data("Gene", "Recurso", fecha, fecha)
        
        print("📥 Descargando metadatos (ListadoRecursos)...")
        df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha, fecha)

        if df_gen is not None and not df_gen.empty:
            # 2. Cruce de información
            df = pd.merge(df_gen, df_meta[['Values_Code', 'Values_EnerSource']], on='Values_Code', how='left')
            
            # 3. Suma horizontal de las 24 horas (Lógica exacta de tu Notebook)
            df['kWh_Dia'] = df.sum(axis=1, numeric_only=True)
            
            # 4. Agrupación por tipo de energía
            resumen = df.groupby('Values_EnerSource')['kWh_Dia'].sum().reset_index()
            resumen['GWh'] = resumen['kWh_Dia'] / 1_000_000
            resumen = resumen.sort_values(by='GWh', ascending=False)

            # --- SALIDA VISUAL AL RUN ---
            print("\n" + "="*50)
            print(f"📊 RESULTADOS DE GENERACIÓN REAL EN COLOMBIA")
            print("="*50)
            print(resumen[['Values_EnerSource', 'GWh']].to_string(index=False, float_format="{:.2f}".format))
            print("="*50)
            print(f"TOTAL CALCULADO: {resumen['GWh'].sum():.2f} GWh")
            print("="*50 + "\n")
            
        else:
            print("⚠️ Error: El DataFrame de generación llegó vacío desde el servidor de XM.")

    except Exception as e:
        print(f"❌ Error durante la ejecución del script: {e}")

if __name__ == "__main__":
    validar_datos_en_run()
