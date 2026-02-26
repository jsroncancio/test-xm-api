import pandas as pd
import numpy as np
from pydataxm import pydataxm as nxm
import datetime as dt
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def reporte_integral_v2():
    objetoAPI = nxm.ReadDB()
    hoy = dt.datetime.now().date()
    df_gen, df_meta, fecha_final = None, None, None

    print(f"🔍 Buscando el reporte más reciente...")

    for i in range(2, 16):
        fecha_test = hoy - dt.timedelta(days=i)
        try:
            temp_gen = objetoAPI.request_data("Gene", "Recurso", fecha_test, fecha_test)
            if temp_gen is not None and not temp_gen.empty:
                df_gen = temp_gen
                fecha_final = fecha_test
                df_meta = objetoAPI.request_data("ListadoRecursos", "Sistema", fecha_test, fecha_test)
                break
        except:
            continue

    if df_gen is None: return

    try:
        # 1. Procesamiento Base
        df_gen.columns = [c.lower() for c in df_gen.columns]
        df_meta.columns = [c.lower() for c in df_meta.columns]
        df = pd.merge(df_gen, df_meta[['values_code', 'values_enersource']], on='values_code', how='left')
        df['kwh_dia'] = df.sum(axis=1, numeric_only=True)
        
        # 2. Resumen Detallado (EUREKA)
        resumen = df.groupby('values_enersource')['kwh_dia'].sum().reset_index()
        resumen['gwh'] = resumen['kwh_dia'] / 1_000_000
        total_dia = resumen['gwh'].sum()
        resumen['%'] = (resumen['gwh'] / total_dia) * 100
        resumen = resumen.sort_values(by='gwh', ascending=False)

        # 3. Categorías Técnicas para Bloques
        sol_viento_list = ['RAD SOLAR', 'VIENTO']
        fncer_total_list = ['RAD SOLAR', 'VIENTO', 'BAGAZO', 'BIOMASA', 'BIOGAS']
        termica_list = ['GAS', 'CARBON', 'COMBUSTOLEO', 'ACPM', 'FUELOIL']
        
        g_sol_viento = resumen[resumen['values_enersource'].isin(sol_viento_list)]['gwh'].sum()
        g_fncer = resumen[resumen['values_enersource'].isin(fncer_total_list)]['gwh'].sum()
        g_termica = resumen[resumen['values_enersource'].isin(termica_list)]['gwh'].sum()
        g_hidro = resumen[resumen['values_enersource'] == 'AGUA']['gwh'].sum()

        # 4. Función Auxiliar para Narrativa de Brechas
        def comparativa(val_a, val_b, nom_a, nom_b):
            dif = val_a - val_b
            pct = (abs(dif) / val_b * 100) if val_b > 0 else 0
            if dif > 0:
                return f"✅ {nom_a} generó {dif:.2f} GWh más que {nom_b} (+{pct:.2f}%)"
            elif dif < 0:
                return f"⚠️ {nom_b} generó {abs(dif):.2f} GWh más que {nom_a} (+{pct:.2f}%)"
            return f"⚖️ Empate exacto entre {nom_a} y {nom_b}"

        # --- SALIDA AL RUN ---
        sep = "█" * 60
        print(f"\n{sep}")
        print(f" 🏆 MONITOR DE TRANSICIÓN ENERGÉTICA - {fecha_final}")
        print(sep)
        
        print("\n📊 1. DESGLOSE DETALLADO (EUREKA):")
        print("-" * 60)
        print(resumen[['values_enersource', 'gwh', '%']].to_string(index=False, float_format="{:.2f}".format))

        print("\n📊 2. BALANCE POR BLOQUES:")
        print(f"{'BLOQUE':<25} | {'GWh':<8} | {'%':<5}")
        print("-" * 45)
        print(f"{'☀️💨 SOL + VIENTO':<25} | {g_sol_viento:<8.2f} | {(g_sol_viento/total_dia*100):.2f}%")
        print(f"{'🌱 FNCER TOTAL':<25} | {g_fncer:<8.2f} | {(g_fncer/total_dia*100):.2f}%")
        print(f"{'💧 HIDROELÉCTRICA':<25} | {g_hidro:<8.2f} | {(g_hidro/total_dia*100):.2f}%")
        print(f"{'🔥 TÉRMICA FÓSIL':<25} | {g_termica:<8.2f} | {(g_termica/total_dia*100):.2f}%")
        
        print("\n📈 3. ANÁLISIS DINÁMICO DE BRECHAS:")
        print("-" * 60)
        
        # FNCER vs Térmica
        print(f"🚀 FNCER vs TÉRMICA:")
        print(f"   {comparativa(g_fncer, g_termica, 'FNCER', 'Térmica')}")
        indice = (g_fncer / g_termica * 100) if g_termica > 0 else 100
        print(f"   Cobertura: {indice:.2f}%")
        
        # Sol+Viento vs Térmica
        print(f"\n⚡ SOL+VIENTO vs TÉRMICA:")
        print(f"   {comparativa(g_sol_viento, g_termica, 'Sol+Viento', 'Térmica')}")
        indice_sv = (g_sol_viento / g_termica * 100) if g_termica > 0 else 100
        print(f"   Cobertura: {indice_sv:.2f}%")

        # Cambios de Sofi*********************************************************
        
        matplotlib.use("Agg")  # backend sin pantalla (clave en GitHub Actions)

        # Cargar Poppins
        font_path_regular = "Poppins-Regular.ttf"
        font_path_bold = "Poppins-Bold.ttf"
        
        fm.fontManager.addfont(font_path_regular)
        fm.fontManager.addfont(font_path_bold)
        
        prop_regular = fm.FontProperties(fname=font_path_regular)
        prop_bold = fm.FontProperties(fname=font_path_bold)
        
        plt.rcParams["font.family"] = prop_regular.get_name()
        
        # Datos base
        res = resumen.copy()
        res["values_enersource"] = res["values_enersource"].fillna("SIN_CLASIFICAR")
        
        # Para que la torta no quede ilegible con demasiadas porciones,
        # agrupo las fuentes muy pequeñas en "OTROS" (ajusta el umbral si quieres).
        umbral_pct = 1.0  # todo lo menor a 1% va a OTROS
        res["pct"] = (res["gwh"] / total_dia * 100) if total_dia > 0 else 0.0
        
        res_grande = res[res["pct"] >= umbral_pct].copy()
        res_peq = res[res["pct"] < umbral_pct].copy()
        
        if not res_peq.empty:
            otros_gwh = float(res_peq["gwh"].sum())
            otros_pct = float(res_peq["pct"].sum())
            fila_otros = pd.DataFrame([{
                "values_enersource": "OTROS",
                "kwh_dia": np.nan,
                "gwh": otros_gwh,
                "%": np.nan,
                "pct": otros_pct
            }])
            res_plot = pd.concat([res_grande, fila_otros], ignore_index=True)
        else:
            res_plot = res_grande
        
        res_plot = res_plot.sort_values("gwh", ascending=False)
        
        # Carbón vs Solar
        g_carbon = float(res.loc[res["values_enersource"] == "CARBON", "gwh"].sum())
        g_solar  = float(res.loc[res["values_enersource"] == "RAD SOLAR", "gwh"].sum())
        
        # Figura con dos paneles (arriba torta, abajo barras)
        fig = plt.figure(figsize=(10, 10))
        gs = fig.add_gridspec(2, 1, height_ratios=[3, 2])
        
        # 1) Torta de participación por fuente
        ax1 = fig.add_subplot(gs[0, 0])
        labels = res_plot["values_enersource"].astype(str).tolist()
        sizes = res_plot["gwh"].astype(float).tolist()
        
        def autopct_fmt(p):
            return f"{p:.1f}%" if p >= 3 else ""  # solo etiqueta porcentajes >=3% para no saturar
        
        ax1.pie(
            sizes,
            labels=None,              # labels en leyenda para que sea más legible
            autopct=autopct_fmt,
            startangle=90
        )
        ax1.set_title(f"Participación diaria por fuente (GWh) – {fecha_final}\nTotal: {total_dia:.2f} GWh")
        
        # Leyenda a la derecha con GWh
        legend_txt = [f"{lab}: {val:.2f} GWh" for lab, val in zip(labels, sizes)]
        ax1.legend(legend_txt, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
        
        # 2) Barra Carbón vs Solar
        ax2 = fig.add_subplot(gs[1, 0])
        bars = ax2.bar(["CARBÓN", "SOLAR"], [g_carbon, g_solar])
        ax2.set_title("Comparación diaria: Carbón vs Solar")
        ax2.set_ylabel("GWh")
        ax2.grid(axis="y", alpha=0.3)
        
        for b in bars:
            h = b.get_height()
            ax2.text(b.get_x() + b.get_width()/2, h, f"{h:.2f}", ha="center", va="bottom", fontsize=10)
        fuente = (
            "Fuente: XM"
            "Elaboración propia."
        )
        
        fig.text(
            0.01, 0.01,
            fuente,
            ha="left",
            va="bottom",
            fontsize=9,
            alpha=0.85
        )
        
        plt.tight_layout(rect=[0, 0.03, 1, 1])
        plt.savefig("dashboard_generacion.png", dpi=200, bbox_inches="tight")
        plt.close()
        
        # Guardar dashboard
        plt.tight_layout()
        plt.savefig("dashboard_generacion.png", dpi=200, bbox_inches="tight")
        plt.close()
        
        print("🖼️ Dashboard generado: dashboard_generacion.png")

        # Cambios de Sofi*********************************************************

        
        print(f"\n{sep}")
        print(f" GENERACIÓN TOTAL: {total_dia:.2f} GWh")
        print(f"{sep}\n")

        

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reporte_integral_v2()
