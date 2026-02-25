import pandas as pd
from pydataxm import pydataxm as nxm
from datetime import datetime, timedelta

def probar_conexion():
    objetoAPI = nxm.ReadDB()
    
    # Probamos con 10 días atrás para ir sobre seguro
    fecha = (datetime.now() - timedelta(days=10)).date()
    
    print(f"--- Iniciando prueba para la fecha: {fecha} ---")
    
    try:
        # Intentamos la métrica más básica: Generación por Sistema
        df = objetoAPI.request_data("Generacion", "Sistema", fecha, fecha)
        
        if df is not None and not df.empty:
            print("✅ ¡CONEXIÓN EXITOSA!")
            print("\nPrimeras filas del reporte recibido:")
            print(df.head())
            
            # Resumen de lo encontrado
            resumen = df.groupby('Nombre')['Value'].sum() / 1e6
            print("\nGeneración total por tecnología (GWh):")
            print(resumen)
        else:
            print("⚠️ El servidor respondió pero el DataFrame está vacío.")
            print("Esto suele pasar si la métrica o la fecha no coinciden en la base de datos.")

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")

if __name__ == "__main__":
    probar_conexion()
