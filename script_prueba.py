import pandas as pd
from pydataxm import pydataxm as nxm
import datetime as dt

def prueba_final_con_parche():
    # El parche: Si la librería intenta usar 'M', Pandas 1.5.3 lo aceptará
    objetoAPI = nxm.ReadDB()
    
    # Usamos una fecha segura (15 días atrás)
    fecha = (dt.datetime.now() - dt.timedelta(days=15)).date()
    
    print(f"--- Ejecutando con Pandas {pd.__version__} para el {fecha} ---")
    
    try:
        # Consultamos usando los códigos de tu Notebook
        df = objetoAPI.request_data("Gene", "Recurso", fecha, fecha)
        
        if df is not None and not df.empty:
            print("✅ ¡CONEXIÓN EXITOSA!")
            print(f"Registros: {len(df)}")
            
            # Sumamos la generación total del día para probar que los datos son reales
            # Las columnas de horas van de la '0' a la '23'
            columnas_horas = [str(i) for i in range(24)]
            total_kwh = df[columnas_horas].sum().sum()
            print(f"⚡ Generación total detectada: {round(total_kwh/1e6, 2)} GWh")
            
            print("\nMuestra de plantas encontradas:")
            print(df[['Values_Code', '0']].head())
        else:
            print("⚠️ El DataFrame llegó vacío.")

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")

if __name__ == "__main__":
    prueba_final_con_parche()
