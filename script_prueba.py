import pandas as pd
from pydataxm import pydataxm as nxm
import datetime as dt

def prueba_maestra():
    objetoAPI = nxm.ReadDB()
    # Usamos 10 días atrás para asegurar que la base de datos esté llena
    fecha = (dt.datetime.now() - dt.timedelta(days=10)).date()
    
    print(f"--- Probando IDs técnicos para el {fecha} ---")
    
    # Intento 1: Por Sistema (Resumen por tecnología)
    print("\n1. Probando 'GeneSist' (Generación por Sistema)...")
    try:
        df_sis = objetoAPI.request_data("GeneSist", "Sistema", fecha, fecha)
        if df_sis is not None and not df_sis.empty:
            print("✅ ¡LOGRADO! Datos de Sistema recibidos.")
            print(df_sis[['Nombre', 'Value']].head())
        else:
            print("❌ 'GeneSist' devolvió vacío.")
    except Exception as e:
        print(f"❌ Error con 'GeneSist': {e}")

    # Intento 2: Por Recurso (Detalle por planta)
    print("\n2. Probando 'GeneRecu' (Generación por Recurso)...")
    try:
        df_rec = objetoAPI.request_data("GeneRecu", "Recurso", fecha, fecha)
        if df_rec is not None and not df_rec.empty:
            print("✅ ¡LOGRADO! Datos de Recurso recibidos.")
            # Mostramos las columnas para saber cómo clasificar
            print("Columnas:", df_rec.columns.tolist())
        else:
            print("❌ 'GeneRecu' devolvió vacío.")
    except Exception as e:
        print(f"❌ Error con 'GeneRecu': {e}")

if __name__ == "__main__":
    prueba_maestra()
