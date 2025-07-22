import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import date
from io import StringIO

# ────────────────────────────────────────────────────────────────────
# 1. CONFIGURACIÓN PÁGINA
# ────────────────────────────────────────────────────────────────────
st.set_page_config("Dashboard Porteros", layout="wide")
st.title("📊 Dashboard de Rendimiento de Porteros")

# ────────────────────────────────────────────────────────────────────
# 2. CARGA DE DATOS
# ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Sube tu CSV (registro_porteros.csv)", type="csv")
if not uploaded:
    st.info("Sube el CSV para visualizar el dashboard.")
    st.stop()

df = pd.read_csv(uploaded, parse_dates=["fecha"])
df["fecha"] = df["fecha"].dt.date

# ────────────────────────────────────────────────────────────────────
# 3. FILTROS GLOBALES
# ────────────────────────────────────────────────────────────────────
st.sidebar.header("📋 Filtros")
porteros = sorted(df["portero"].unique())
sel_p = st.sidebar.multiselect("Portero(s)", porteros, default=porteros)
min_f, max_f = df["fecha"].min(), df["fecha"].max()
sel_fecha = st.sidebar.date_input("Rango de fechas", [min_f, max_f], min_value=min_f, max_value=max_f)
eventos = sorted(df["evento"].unique())
sel_e = st.sidebar.multiselect("Evento(s)", eventos, default=eventos)

df_f = df[
    df["portero"].isin(sel_p) &
    df["evento"].isin(sel_e) &
    (df["fecha"] >= sel_fecha[0]) &
    (df["fecha"] <= sel_fecha[1])
]

# ────────────────────────────────────────────────────────────────────
# 4. KPIs
# ────────────────────────────────────────────────────────────────────
atajadas = df_f[df_f["evento"]=="Atajada"].shape[0]
goles   = df_f[df_f["evento"]=="Gol Recibido"].shape[0]
# Pases totales y exitosos
p_tot = df_f[df_f["evento"]=="Pase"].shape[0]
p_ok  = df_f[(df_f["evento"]=="Pase") & (df_f["pase_exitoso"]=="Sí")].shape[0]
# Eficacias
ef_atj = f"{(atajadas*100/(atajadas+goles)):.1f}%" if (atajadas+goles)>0 else "—"
ef_pas = f"{(p_ok*100/p_tot):.1f}%" if p_tot>0 else "—"

st.subheader("📌 Indicadores Clave")
c1, c2, c3, c4 = st.columns(4, gap="small")
c1.metric("🧤 Atajadas", atajadas)
c2.metric("🥅 Goles recibidos", goles)
c3.metric("🎯 Eficiencia pases", ef_pas)
c4.metric("✅ Eficacia atajadas", ef_atj)
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5A. SEGMENTO A – Atajadas
# ────────────────────────────────────────────────────────────────────
ata = df_f[df_f["evento"]=="Atajada"]
if not ata.empty:
    st.markdown("### 🧤 Segmento A – Atajadas")
    a1, a2 = st.columns(2, gap="small")
    with a1:
        fig, ax = plt.subplots()
        ata["tipo_intervencion"].value_counts().plot.bar(ax=ax)
        ax.set_title("Tipo de intervención"); ax.set_ylabel("Cantidad")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    with a2:
        fig, ax = plt.subplots()
        ata["resultado_parada"].value_counts().plot.bar(ax=ax)
        ax.set_title("Resultado de la parada"); ax.set_ylabel("Cantidad")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5B. SEGMENTO B – Goles recibidos
# ────────────────────────────────────────────────────────────────────
gol = df_f[df_f["evento"]=="Gol Recibido"]
if not gol.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")

    # 5B.1 Zona de gol 1‑9 como heatmap 3×3
    cnt_gz = gol["zona_gol"].value_counts().reindex(range(1,10), fill_value=0)
    mat = cnt_gz.values.reshape(3,3)[::-1]
    fig, ax = plt.subplots()
    im = ax.imshow(mat, cmap="Reds")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, str(mat[i,j]), ha="center", va="center")
    ax.set_xticks([0,1,2]); ax.set_xticklabels(["1","2","3"])
    ax.set_yticks([0,1,2]); ax.set_yticklabels(["7‑9","4‑6","1‑3"][::-1])
    ax.set_title("Mapa de calor: Zona de gol")
    st.pyplot(fig)

    # 5B.2 Zona de remate 1‑20 con rectángulos
    st.markdown("#### 🔴 Mapa de calor: Zona de remate")
    zone_coords = {
        "1": (0.75,0.8,0.25,0.2),  "2": (0.75,0.6,0.25,0.2),
        "3": (0.75,0.4,0.25,0.2),  "4": (0.75,0.2,0.25,0.2),
        "5": (0.75,0.0,0.25,0.2),  "6": (0.50,0.8,0.25,0.2),
        "7": (0.50,0.6,0.25,0.2),  "8": (0.50,0.4,0.25,0.2),
        "9": (0.50,0.2,0.25,0.2),  "10":(0.50,0.0,0.25,0.2),
        "11":(0.25,0.8,0.25,0.2),"12":(0.25,0.6,0.25,0.2),
        "13":(0.25,0.4,0.25,0.2),"14":(0.25,0.2,0.25,0.2),
        "15":(0.25,0.0,0.25,0.2),"16":(0.00,0.8,0.25,0.2),
        "17a":(0.00,0.6,0.25,0.2),"17b":(0.00,0.4,0.25,0.2),
        "17c":(0.00,0.2,0.25,0.2),"20":(0.00,0.0,0.25,0.2),
        "18a":(0.125,0.6,0.125,0.2),"18b":(0.125,0.4,0.125,0.2),
        "19a":(0.125,0.2,0.125,0.2),"19b":(0.125,0.0,0.125,0.2),
    }
    counts = gol["zona_remate"].value_counts().to_dict()
    mx = max(counts.values()) if counts else 1

    fig, ax = plt.subplots(figsize=(6,4))
    # campo
    ax.add_patch(patches.Rectangle((0,0),1,1,fill=False,linewidth=2))
    # pintar cada zona
    for z, (x,y,w,h) in zone_coords.items():
        cnt = counts.get(z,0)
        col = plt.cm.Reds(cnt/mx)
        ax.add_patch(patches.Rectangle((x,y),w,h,facecolor=col,edgecolor="gray"))
        ax.text(x+w/2, y+h/2, f"{z}\n{cnt}",ha="center",va="center",fontsize=8)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Mapa de calor: Zona de remate")
    st.pyplot(fig)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5C. SEGMENTO C – Pases (Radar Chart)
# ────────────────────────────────────────────────────────────────────
pas = df_f[df_f["evento"]=="Pase"]
if not pas.empty:
    st.markdown("### 🟢 Segmento C – Pases (Radar)")
    tipos = ["Corto","Medio","Largo","Despeje"]
    tasas = [pas[pas["tipo_pase"]==t]["pase_exitoso"].eq("Sí").mean() for t in tipos]

    # Radar
    angles = np.linspace(0, 2*np.pi, len(tipos), endpoint=False).tolist()
    tasas += tasas[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(subplot_kw=dict(polar=True))
    ax.plot(angles, tasas, marker="o")
    ax.fill(angles, tasas, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), tipos)
    ax.set_ylim(0,1)
    ax.set_title("Tasa de éxito por tipo de pase", va="bottom")
    st.pyplot(fig)

# ────────────────────────────────────────────────────────────────────
# 6. TABLA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=300)
buf = StringIO()
df_f.to_csv(buf, index=False)
st.download_button("💾 Descargar CSV", buf.getvalue(), "filtrado.csv", "text/csv")
