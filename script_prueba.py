import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def prueba_final_estabilizada():
    print(f"--- Versiones: Pandas {pd.__version__} | Numpy {np.__version__} ---")
    
    objetoAPI = nxm.ReadDB()
    # 15 días atrás para asegurar datos oficiales
    fecha = (dt.datetime.now() - dt.timedelta(days=15)).date()
    
    try:
        print(f"🚀 Consultando 'Gene' por 'Recurso' para {fecha}...")
        df = objetoAPI.request_data("Gene", "Recurso", fecha, fecha)
        
        if df is not None and not df.empty:
            print("✅ ¡CONEXIÓN EXITOSA!")
            # Columnas de horas: de '0' a '23'
            columnas_horas = [str(i) for i in range(24)]
            total_gwh = df[columnas_horas].apply(pd.to_numeric, errors='coerce').sum().sum() / 1e6
            
            print(f"⚡ Generación Total del día: {round(total_gwh, 2)} GWh")
            print("\nMuestra de las primeras plantas:")
            print(df[['Values_Code', '0']].head())
        else:
            print("⚠️ El DataFrame llegó vacío.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    prueba_final_estabilizada()
