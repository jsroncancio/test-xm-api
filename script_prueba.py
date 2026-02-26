import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt

def reporte_maestro_final():
    objetoAPI = nxm.ReadDB()
    hoy = dt.datetime.now().date()
    df_gen, df_meta, fecha_final = None, None, None

    print(f"🔍 Buscando el reporte más reciente disponible...")

    for i in range(2, 16):
        fecha_test = hoy - dt.timedelta(days=i)
        try:
            temp_gen = objetoAPI.request_data("Gene", "Recurso", fecha_test, fecha_test)
            if temp_gen is not None and not temp_gen.empty:
                df_gen, fecha_final = temp_gen, fecha_test
                df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha_test, fecha_test)
                break
        except: continue

    if df_gen is None: return

    try:
        # 1. Normalización y Cruce
        df_gen.columns = [c.lower() for c in df_gen.columns]
        df_meta.columns = [c.lower() for c in df_meta.columns]
        df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
        df['kwh_dia'] = df.sum(axis=1, numeric_only=True)
        
        # 2. Resumen por Fuente (EUREKA)
        resumen = df.groupby('values_enersource')['kwh_dia'].sum().reset_index()
        resumen['gwh'] = resumen['kwh_dia'] / 1_000_000
        total_dia = resumen['gwh'].sum()
        resumen['porcentaje'] = (resumen['gwh'] / total_dia) * 100
        resumen = resumen.sort_values(by='gwh', ascending=False)

        # 3. Bloques Estratégicos
        g_sv = resumen[resumen['values_enersource'].isin(['RAD SOLAR', 'VIENTO'])]['gwh'].sum()
        g_fncer = resumen[resumen['values_enersource'].isin(['RAD SOLAR', 'VIENTO', 'BAGAZO', 'BIOMASA', 'BIOGAS'])]['gwh'].sum()
        g_termica = resumen[resumen['values_enersource'].isin(['GAS', 'CARBON', 'COMBUSTOLEO', 'ACPM', 'FUELOIL'])]['gwh'].sum()
        g_hidro = resumen[resumen['values_enersource'] == 'AGUA']['gwh'].sum()

        def comparativa(val_a, val_b, nom_a, nom_b):
            dif = val_a - val_b
            pct = (abs(dif) / val_b * 100) if val_b > 0 else 0
            if dif > 0:
                return f"✅ {nom_a} superó a {nom_b} por {dif:.2f} GWh (+{pct:.2f}%)"
            elif dif < 0:
                return f"⚠️ {nom_b} superó a {nom_a} por {abs(dif):.2f} GWh (+{pct:.2f}%)"
            else:
                return f"⚖️ Empate exacto entre {nom_a} y {nom_b}"

        # --- SALIDA FINAL INTEGRADA AL RUN ---
        print("\n" + "█"*65)
        print(f" 🏆 MONITOR INTEGRAL DE TRANSICIÓN ENERGÉTICA - {fecha_final}")
        print("█" *
