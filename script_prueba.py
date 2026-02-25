import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def prueba_final_columnas():
    # Mantenemos las versiones: Pandas 1.5.3 | Numpy 1.23.5
    print(f"--- Iniciando con lógica de tu Notebook (Pandas {pd.__version__}) ---")
    
    objetoAPI = nxm.ReadDB()
    # Usamos 15 días atrás para asegurar datos validados
    fecha = (dt.datetime.now() - dt.timedelta(days=15)).date()
    
    try:
        print(f"🚀 Consultando 'Gene' por 'Recurso' para {fecha}...")
        df = objetoAPI.request_data("Gene", "Recurso", fecha, fecha)
        
        if df is not None and not df.empty:
            print("✅ ¡CONEXIÓN EXITOSA!")
            
            # TÉCNICA DEL NOTEBOOK: Sumar horizontalmente (axis=1) solo columnas numéricas
            # Esto captura automáticamente de Values_Hour01 a Values_Hour24
            generacion_diaria_por_planta = df.sum(axis=1, numeric_only=True)
            
            # Sumamos todas las plantas y convertimos a GWh
            total_gwh = generacion_diaria_por_planta.sum() / 1e6
            
            print(f"⚡ Generación Total del país el {fecha}: {round(total_gwh, 2)} GWh")
            
            print("\nColumnas reales detectadas en el servidor:")
            # Mostramos las primeras 10 columnas para confirmar el nombre 'Values_HourXX'
            print(df.columns.tolist()[:10])
            
            if 'Values_Code' in df.columns:
                print("\nMuestra de plantas (Código | Generación diaria):")
                df['Total_Dia_kWh'] = generacion_diaria_por_planta
                print(df[['Values_Code', 'Total_Dia_kWh']].head())
        else:
            print("⚠️ El DataFrame llegó vacío.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    prueba_final_columnas()
