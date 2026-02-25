import pandas as pd
from pydataxm import pydataxm as nxm

def buscar_metricas():
    objetoAPI = nxm.ReadDB()
    
    print("--- Buscando nombres oficiales de métricas en XM ---")
    
    try:
        # Pedimos el inventario de métricas disponibles
        df_metricas = objetoAPI.get_metrics()
        
        # Filtramos las que contengan la palabra 'Generacion'
        filtro = df_metricas[df_metricas['MetricName'].str.contains('Generacion', case=False, na=False)]
        
        if not filtro.empty:
            print("✅ Métricas encontradas con el nombre 'Generacion':")
            # Mostramos el MetricId que es el que necesitamos para el código
            print(filtro[['MetricName', 'Entity', 'MetricId']])
        else:
            print("❌ No se encontraron métricas con ese nombre. Aquí están las primeras 10 disponibles:")
            print(df_metricas['MetricName'].head(10))

    except Exception as e:
        print(f"❌ Error al consultar el inventario: {e}")

if __name__ == "__main__":
    buscar_metricas()
