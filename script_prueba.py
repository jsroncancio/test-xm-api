import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def analisis_indicador_transicion():
    objetoAPI = nxm.ReadDB()
    # Usamos 15 días atrás para datos consolidados
    fecha = (dt.datetime.now() - dt.timedelta(days=15)).date()
    
    print(f"--- INDICADOR CRÍTICO DE TRANSICIÓN: {fecha} ---")
    
    try:
        # 1. Extracción (IDs validados: Gene y ListadoRecursos)
        df_gen = objetoAPI.request_data("Gene", "Recurso", fecha, fecha)
        df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha, fecha)

        if df_gen is not None and not df_gen.empty:
            df_gen.columns = [c.lower() for c in df_gen.columns]
            df_meta.columns = [c.lower() for c in df_meta.columns]
            
            # 2. Cruce y Suma Diaria
            df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
            df['kwh_dia'] = df.sum(axis=1, numeric_only=True)
            
            resumen = df.groupby('values_enersource')['kwh_dia'].sum().reset_index()
            resumen['gwh'] = resumen['kwh_dia'] / 1_000_000
            total_dia = resumen['gwh'].sum()

            # 3. CATEGORIZACIÓN PARA EL INDICADOR
            fncer_list = ['RAD SOLAR', 'VIENTO', 'BAGAZO', 'BIOMASA', 'BIOGAS']
            termica_list = ['GAS', 'CARBON', 'COMBUSTOLEO', 'ACPM', 'FUELOIL']
            
            g_fncer = resumen[resumen['values_enersource'].isin(fncer_list)]['gwh'].sum()
            g_termica = resumen[resumen['values_enersource'].isin(termica_list)]['gwh'].sum()
            g_hidro = resumen[resumen['values_enersource'] == 'AGUA']['gwh'].sum()

            # 4. CÁLCULO DEL INDICADOR DE TRANSICIÓN
            # ¿Qué porcentaje de la generación térmica es cubierto por las FNCER?
            cobertura_fncer = (g_fncer / g_termica * 100) if g_termica > 0 else 100
            brecha_gwh = g_termica - g_fncer
            
            # 5. IMP
