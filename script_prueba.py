import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def validar_datos_en_run():
    objetoAPI = nxm.ReadDB()
    # Usamos 15 días atrás
    fecha = (dt.datetime.now() - dt.timedelta(days=15)).date()
    
    print(f"--- DIAGNÓSTICO DE COLUMNAS PARA EL {fecha} ---")
    
    try:
        df_gen = objetoAPI.request_data("Gene", "Recurso", fecha, fecha)
        df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha, fecha)

        if df_gen is not None and not df_gen.empty:
            # Normalizamos los nombres de las columnas a minúsculas para evitar el error 'Values_Code'
            df_gen.columns = [c.lower() for c in df_gen.columns]
            df_meta.columns = [c.lower() for c in df_meta.columns]
            
            print(f"Columnas en Generación: {df_gen.columns.tolist()[:5]}")
            print(f"Columnas en Metadatos: {df_meta.columns.tolist()[:5]}")

            # El cruce ahora se hace con 'values_code' en minúsculas
            df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
            
            # Suma de las 24 horas (lógica de tu Notebook)
            df['kwh_dia'] = df.sum(axis=1, numeric_only=True)
            
            # Agrupación por fuente
            resumen = df.groupby('values_enersource')['kwh_dia'].sum().reset_index()
            resumen['gwh'] = resumen['kwh_dia'] / 1_000_000
            resumen = resumen.sort_values(by='gwh', ascending=False)

            print("\n" + "="*50)
            print(f"📊 RESULTADOS DE GENERACIÓN REAL EN COLOMBIA")
            print("="*50)
            print(resumen[['values_enersource', 'gwh']].to_string(index=False, float_format="{:.2f}".format))
            print("="*50)
            print(f"TOTAL: {resumen['gwh'].sum():.2f} GWh\n")
            
        else:
            print("⚠️ No hay datos en la respuesta de XM.")

    except Exception as e:
        print(f"❌ Error detallado: {e}")
        if 'df_gen' in locals(): print(f"Columnas gen encontradas: {df_gen.columns}")
        if 'df_meta' in locals(): print(f"Columnas meta encontradas: {df_meta.columns}")

if __name__ == "__main__":
    validar_datos_en_run()
