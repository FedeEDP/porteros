import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import StringIO
from datetime import date

# ────────────────────────────────────────────────────────────────────
# 1. CONFIGURACIÓN DE PÁGINA
# ────────────────────────────────────────────────────────────────────
st.set_page_config("Dashboard Porteros – PD1", layout="wide")
st.title("📊 Dashboard Rendimiento Porteros (1ª División)")
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 2. CARGA DE DATOS
# ────────────────────────────────────────────────────────────────────
csv = st.file_uploader("Sube CSV (registro_porteros.csv)", type="csv")
if not csv:
    st.info("Carga el CSV para continuar."); st.stop()

df = pd.read_csv(csv, parse_dates=["fecha"])
df["fecha"] = df["fecha"].dt.date

# ────────────────────────────────────────────────────────────────────
# 3. FILTROS GLOBALES
# ────────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")
porteros = sorted(df["portero"].unique())
sel_p     = st.sidebar.multiselect("Portero(s)", porteros, default=porteros)

min_d, max_d = df["fecha"].min(), df["fecha"].max()
sel_d        = st.sidebar.date_input("Rango fechas",
                                     [min_d, max_d],
                                     min_value=min_d,
                                     max_value=max_d)

eventos = sorted(df["evento"].unique())
sel_e   = st.sidebar.multiselect("Evento(s)", eventos, default=eventos)

df_f = df[
    df["portero"].isin(sel_p) &
    df["evento"].isin(sel_e) &
    (df["fecha"] >= sel_d[0]) &
    (df["fecha"] <= sel_d[1])
]

# ────────────────────────────────────────────────────────────────────
# 4. CÁLCULO DE TASAS
# ────────────────────────────────────────────────────────────────────
atajadas = df_f[df_f["evento"]=="Atajada"].shape[0]
g_rec    = df_f[df_f["evento"]=="Gol Recibido"].shape[0]
pases    = df_f[df_f["evento"]=="Pase"]
tot_p    = len(pases)
ok_p     = (pases["pase_exitoso"]=="Sí").sum()
tasa_p   = ok_p/ tot_p if tot_p else 0
tasa_a   = atajadas / (atajadas + g_rec) if (atajadas + g_rec) else 0

# ────────────────────────────────────────────────────────────────────
# 5A. SEGMENTO A – Tasas de eficacia
# ────────────────────────────────────────────────────────────────────
st.subheader("🧤 Segmento A – Eficacia de Atajadas")
st.metric("✅ Eficacia Atajadas", f"{tasa_a*100:.1f}%")
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5B. SEGMENTO B – Goles Recibidos & Zona Remate
# ────────────────────────────────────────────────────────────────────
gol = df_f[df_f["evento"]=="Gol Recibido"]
if not gol.empty:
    st.subheader("⚽ Segmento B – Goles Recibidos")

    # (a) Zona 1–9 (compacta)
    cnt9 = gol["zona_gol"].value_counts() \
               .reindex(range(1,10), fill_value=0)
    mat9 = cnt9.values.reshape(3,3)[::-1]
    fig1, ax1 = plt.subplots(figsize=(1.5,1.5))
    ax1.imshow(mat9, cmap="Reds", aspect="equal")
    for i in range(3):
        for j in range(3):
            ax1.text(j, i, mat9[i,j],
                     ha="center", va="center", fontsize=6)
    ax1.axis("off")
    plt.tight_layout()
    st.pyplot(fig1)

    # (b) Zona remate 1–20 (invertido horizontalmente)
    st.markdown("#### 🔴 Mapa Calor: Zona Remate 1–20")
    # columnas de izquierda→derecha (1…5)
    xs = [0.125, 0.375, 0.625, 0.875]
    ys = [0.90, 0.70, 0.50, 0.30, 0.10]
    grid = [
        [("1",1),  ("6",1),  ("11",1), ("16",1)],
        [("2",1),  ("7",1),  ("12",1), ("17",3)],
        [("3",1),  ("8",1),  ("13",1), ("18",2)],
        [("4",1),  ("9",1),  ("14",1), ("19",3)],
        [("5",1),  ("10",1), ("15",1), ("20",1)],
    ]
    cnt20 = gol["zona_remate"].value_counts().to_dict()

    fig2, ax2 = plt.subplots(figsize=(4,1.2))
    ax2.add_patch(patches.Rectangle((0,0),1,1,
                       facecolor="#fafafa", edgecolor="none"))
    w, h = 0.23, 0.16

    for r, row in enumerate(grid):
        for c, (z, n) in enumerate(row):
            cx, cy = xs[c], ys[r]
            x0, y0 = cx - w/2, cy - h/2
            subs = np.linspace(x0, x0 + w, n+1)[:-1]
            # etiquetas de derecha→izq
            if n==1:
                lets = [""]
            elif n==2:
                lets = ["b","a"]
            else:  # n==3
                lets = ["c","b","a"]
            for i, sx in enumerate(subs):
                key   = z + lets[i]
                total = cnt20.get(key, 0)
                color = "#d32f2f" if total>0 else "#fafafa"
                ax2.add_patch(patches.Rectangle(
                    (sx,y0), w/n, h,
                    facecolor=color, edgecolor="#cccccc", lw=0.5
                ))
                lbl = key if n>1 else z
                ax2.text(sx+0.005, y0+h*0.55,
                         lbl, fontsize=6, ha="left", va="center")
                ax2.text(sx+0.005, y0+h*0.30,
                         str(total), fontsize=6, ha="left", va="center")

    ax2.axis("off")
    plt.tight_layout()
    st.pyplot(fig2)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5C. SEGMENTO C – Tasa de eficacia de Pases
# ────────────────────────────────────────────────────────────────────
st.subheader("🟢 Segmento C – Eficacia de Pases")
st.metric("✅ Eficacia Pases", f"{tasa_p*100:.1f}%")
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 6. TABLA DETALLADA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.subheader("📄 Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=200)
buf = StringIO(); df_f.to_csv(buf, index=False)
st.download_button("📥 Descargar CSV", buf.getvalue(), "filtrado.csv", "text/csv")
