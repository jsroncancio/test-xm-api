import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt
import requests

# --- CONFIGURACIÓN ---
TOKEN = "8699187963:AAHiVYGqwc9wK24fYxmJ9xY1p9bCW-kb6tA"
CHAT_ID = "8283386526"

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensaje, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload, timeout=10)

def monitor_energetico():
    objetoAPI = nxm.ReadDB()
    
    # Intentamos buscar datos desde ayer hacia atrás hasta encontrar el reporte más reciente
    df_gen = None
    fecha_final = None
    
    for i in range(1, 15): # Busca hasta 14 días atrás
        fecha_prueba = (dt.datetime.now() - dt.timedelta(days=i)).date()
        try:
            temp_df = objetoAPI.request_data("Gene", "Recurso", fecha_prueba, fecha_prueba)
            if temp_df is not None and not temp_df.empty:
                df_gen = temp_df
                fecha_final = fecha_prueba
                break
        except:
            continue
            
    if df_gen is None:
        enviar_telegram("⚠️ No se encontraron datos de generación en los últimos 14 días.")
        return

    try:
        # Obtenemos el mapeo de plantas para saber la fuente de energía
        df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha_final, fecha_final)
        
        # Unimos la generación con la fuente de energía
        df = pd.merge(df_gen, df_meta[['Values_Code', 'Values_EnerSource']], on='Values_Code', how='left')
        
        # Sumamos las 24 horas usando la lógica de tu Notebook
        df['Total_kWh'] = df.sum(axis=1, numeric_only=True)
        
        # Clasificamos y sumamos por fuente (convertimos a GWh)
        def suma_fuente(nombre):
            return df[df['Values_EnerSource'].str.contains(nombre, case=False, na=False)]['Total_kWh'].sum() / 1e6

        hidro = suma_fuente('AGUA')
        solar = suma_fuente('RAD SOLAR')
        eolica = suma_fuente('VIENTO')
        biomasa = suma_fuente('BIOMASA')
        
        carbon = suma_fuente('CARBON')
        gas = suma_fuente('GAS')
        otros_fosiles = (df[df['Values_EnerSource'].str.contains('ACPM|OLEO|FUEL', case=False, na=False)]['Total_kWh'].sum() / 1e6)

        # Totales
        renovables = hidro + solar + eolica + biomasa
        fosiles = carbon + gas + otros_fosiles
        total = renovables + fosiles
        
        # Porcentajes y Brecha
        p_solar = (solar / total * 100) if total > 0 else 0
        p_eolica = (eolica / total * 100) if total > 0 else 0
        p_fncer = p_solar + p_eolica + ((biomasa/total*100) if total > 0 else 0)
        
        balance = renovables - fosiles
        
        # Mensaje
        msg = (
            f"🏆 *REPORTE DE GENERACIÓN XM*\n"
            f"📅 Fecha: {fecha_final}\n"
            f"---"
            f"\n🟢 *Renovables:* {round(renovables, 1)} GWh"
            f"\n🔴 *Fósiles:* {round(fosiles, 1)} GWh"
            f"\n\n"
            f"💧 Hidro: {round(hidro, 1)} GWh\n"
            f"☀️ Solar: {round(solar, 1)} GWh ({round(p_solar, 1)}%)\n"
            f"🌬️ Eólica: {round(eolica, 1)} GWh ({round(p_eolica, 1)}%)\n"
            f"🪨 Carbón: {round(carbon, 1)} GWh\n"
            f"🔥 Gas: {round(gas, 1)} GWh\n"
            f"---"
            f"\n📊 *Part. FNCER:* {round(p_fncer, 2)}%"
            f"\n\n" + ("🌱 *Renovables dominan*" if balance > 0 else f"⚖️ *Brecha:* Faltan {round(abs(balance), 1)} GWh para superar fósiles")
        )
        
        enviar_telegram(msg)
        
    except Exception as e:
        enviar_telegram(f"❌ Error procesando datos: {str(e)[:100]}")

if __name__ == "__main__":
    monitor_energetico()
