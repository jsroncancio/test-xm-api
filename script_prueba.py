import pandas as pd
from pydataxm import pydataxm as nxm
import datetime as dt

def prueba_final_nombres():
    objetoAPI = nxm.ReadDB()
    
    # Probamos con una fecha segura de hace 15 días
    # XM a veces bloquea consultas de fechas muy recientes si no están validadas
    fecha = (dt.datetime.now() - dt.timedelta(days=15)).date()
    
    print(f"--- Intentando conexión con métrica 'GeneracionReal' para {fecha} ---")
    
    try:
        # Usamos la combinación que suele ser la más pública: GeneracionReal por Recurso
        df = objetoAPI.request_data("GeneracionReal", "Recurso", fecha, fecha)
        
        if df is not None and not df.empty:
            print("✅ ¡CONEXIÓN EXITOSA!")
            print(f"Se recibieron {len(df)} registros.")
            print("\nColumnas disponibles en el reporte:")
            print(df.columns.tolist())
            
            # Mostramos un ejemplo de qué nombres de plantas o recursos vienen
            if 'Values_Code' in df.columns:
                print("\nEjemplos de códigos de recursos encontrados:")
                print(df['Values_Code'].unique()[:10])
                
        else:
            print("⚠️ El DataFrame llegó vacío. Probando ahora con Entidad 'Sistema'...")
            df_sis = objetoAPI.request_data("GeneracionReal", "Sistema", fecha, fecha)
            if df_sis is not None and not df_sis.empty:
                print("✅ ¡CONEXIÓN EXITOSA con Entidad 'Sistema'!")
                print(df_sis.head())
            else:
                print("❌ Ambas consultas (Recurso y Sistema) devolvieron vacío.")

    except Exception as e:
        print(f"❌ Error técnico: {e}")

if __name__ == "__main__":
    prueba_final_nombres()
