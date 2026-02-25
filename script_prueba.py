import pandas as pd
from pydataxm import pydataxm as nxm

def descubrir_nombres_reales():
    objetoAPI = nxm.ReadDB()
    
    print("--- INVESTIGACIÓN DE MÉTRICAS DISPONIBLES ---")
    
    try:
        # Intentamos obtener el inventario básico que toda instancia de ReadDB debería tener
        # Si get_metrics no funciona, usaremos el endpoint de catálogos
        df_metricas = objetoAPI.get_collections() 
        
        if df_metricas is not None and not df_metricas.empty:
            print(f"✅ Se encontraron {len(df_metricas)} métricas disponibles.")
            
            # Buscamos cualquier cosa que se parezca a Generación
            busqueda = df_metricas[df_metricas['MetricName'].str.contains('Gen', case=False, na=False)]
            
            print("\n📋 LISTA DE MÉTRICAS DE GENERACIÓN DISPONIBLES (Usa el MetricId):")
            print(busqueda[['MetricName', 'MetricId', 'Entity']])
        else:
            print("⚠️ El catálogo de colecciones llegó vacío.")

    except Exception as e:
        print(f"❌ Error al consultar colecciones: {e}")
        print("\n--- INTENTANDO INSPECCIÓN DE MÉTODOS ---")
        # Esto nos dirá qué funciones SI existen en la librería
        import inspect
        metodos = [m[0] for m in inspect.getmembers(objetoAPI, predicate=inspect.ismethod)]
        print(f"Métodos disponibles en objetoAPI: {metodos}")

if __name__ == "__main__":
    descubrir_nombres_reales()
