import pandas as pd
from pydataxm import pydataxm as nxm
import datetime as dt

def prueba_definitiva_gene():
    objetoAPI = nxm.ReadDB()
    
    # Probamos con una fecha de hace 15 días para garantizar que el dato sea oficial
    fecha = (dt.datetime.now() - dt.timedelta(days=15)).date()
    
    print(f"--- Usando códigos del Notebook para el {fecha} ---")
    
    try:
        # Según tu Notebook, el ID es 'Gene' y la entidad es 'Recurso'
        print("\n🚀 Consultando MetricId='Gene', Entity='Recurso'...")
        df = objetoAPI.request_data("Gene", "Recurso", fecha, fecha)
        
        if df is not None and not df.empty:
            print("✅ ¡ÉXITO! Datos recibidos de XM.")
            print(f"Registros encontrados: {len(df)}")
            
            # Mostramos las primeras columnas para ver los nombres de las plantas y horas
            print("\nColumnas del reporte:")
            print(df.columns.tolist())
            
            print("\nPrimeras filas (Muestra):")
            # Mostramos la columna de identificación y las primeras 3 horas
            cols_ver = ['Values_Code', '0', '1', '2']
            print(df[cols_ver].head())
            
        else:
            print("⚠️ El DataFrame llegó vacío. Intentando con Entidad='Sistema'...")
            df_sis = objetoAPI.request_data("Gene", "Sistema", fecha, fecha)
            if df_sis is not None and not df_sis.empty:
                print("✅ ¡ÉXITO! Datos de Sistema recibidos.")
                print(df_sis.head())
            else:
                print("❌ No se obtuvieron datos con el ID 'Gene'.")

    except Exception as e:
        print(f"❌ Error técnico durante la ejecución: {e}")

if __name__ == "__main__":
    # Llamada correcta sin los dos puntos al final
    prueba_definitiva_gene()
    
