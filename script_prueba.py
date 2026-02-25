import pandas as pd
from pydataxm import pydataxm as nxm
import datetime as dt

def prueba_definitiva_gene():
    objetoAPI = nxm.ReadDB()
    
    # Probamos con una fecha de hace 10 días para asegurar datos
    fecha = (dt.datetime.now() - dt.timedelta(days=10)).date()
    
    print(f"--- Usando códigos del Notebook para el {fecha} ---")
    
    try:
        # 1. Probamos con 'Gene' y 'Recurso' (Tal cual está en tu celda 623)
        print("\n🚀 Intentando: MetricId='Gene', Entity='Recurso'...")
        df = objetoAPI.request_data("Gene", "Recurso", fecha, fecha)
        
        if df is not None and not df.empty:
            print("✅ ¡EXITO TOTAL! Datos recibidos.")
            print(f"Número de registros: {len(df)}")
            print("\nPrimeras filas del reporte:")
            # Mostramos las columnas para confirmar nombres
            print(df[['Values_Code', '0', '1', '2']].head())
            
            # Guardamos una pequeña muestra para que veas que sí hay datos
            df.head(10).to_csv("muestra_datos_xm.csv")
            print("\n💾 Se ha generado un archivo 'muestra_datos_xm.csv' con la prueba.")
        else:
            print("⚠️ 'Gene' por 'Recurso' llegó vacío. Intentando por 'Sistema'...")
            df_sis = objetoAPI.request_data("Gene", "Sistema", fecha, fecha)
            if df_sis is not None and not df_sis.empty:
                print("✅ ¡EXITO! 'Gene' por 'Sistema' funcionó.")
                print(df_sis.head())
            else:
                print("❌ No se encontraron datos con el ID 'Gene'.")

    except Exception as e:
        print(f"❌ Error técnico: {e}")

if __name__ == "__main__":
    prueba_definitiva_gene():
