import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def test_visualizacion_datos():
    # Inicializamos la API
    objetoAPI = nxm.ReadDB()
    
    # Usamos 15 días atrás para que los datos estén 100% validados por XM
    fecha = (dt.datetime.now() - dt.timedelta(days=15)).date()
    
    print(f"--- INICIANDO CAPTURA DE DATOS PARA: {fecha} ---")
    
    try:
        # 1. Pedir Generación Real por Recurso (ID: Gene)
        df_gen = objetoAPI.request_data("Gene", "Recurso", fecha, fecha)
        
        # 2. Pedir Listado de Recursos para cruzar con la Fuente (Agua, Sol, etc.)
        df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha, fecha)

        if df_gen is not None and not df_gen.empty:
            # 3. Cruzar tablas usando 'Values_Code' (como en tu Notebook)
            df = pd.merge(df_gen, df_meta[['Values_Code', 'Values_EnerSource']], on='Values_Code', how='left')
            
            # 4. Sumar las 24 horas (columnas numéricas) para tener el total diario por planta
            df['kWh_Dia'] = df.sum(axis=1, numeric_only=True)
            
            # 5. Agrupar por Fuente de Energía y convertir a GWh
            resumen = df.groupby('Values_EnerSource')['kWh_Dia'].sum().reset_index()
            resumen['GWh'] = resumen['kWh_Dia'] / 1_000_000
            resumen = resumen.sort_values(by='GWh', ascending=False)

            # --- LO QUE VERÁS EN EL RUN ---
            print("\n" + "="*45)
            print(f"       TABLA DE GENERACIÓN REAL")
            print("="*45)
            print(resumen[['Values_EnerSource', 'GWh']].to_string(index=False))
            print("="*45)
            print(f"TOTAL DEL DÍA: {resumen['GWh'].sum():.2f} GWh\n")
            
        else:
            print("⚠️ No se encontraron datos. Verifica la conexión con XM.")

    except Exception as e:
        print(f"❌ Error en el script: {e}")

if __name__ == "__main__":
    test_visualizacion_datos()
