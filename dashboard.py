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
    st.info("Carga el CSV para continuar.")
    st.stop()

df = pd.read_csv(csv, parse_dates=["fecha"])
df["fecha"] = df["fecha"].dt.date

# ────────────────────────────────────────────────────────────────────
# 3. FILTROS GLOBALES
# ────────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")
porteros = sorted(df["portero"].unique())
sel_p     = st.sidebar.multiselect("Portero(s)", porteros, default=porteros)

min_d, max_d = df["fecha"].min(), df["fecha"].max()
sel_d        = st.sidebar.date_input(
    "Rango fechas", [min_d, max_d],
    min_value=min_d, max_value=max_d
)

eventos = sorted(df["evento"].unique())
sel_e    = st.sidebar.multiselect("Evento(s)", eventos, default=eventos)

df_f = df[
    df["portero"].isin(sel_p) &
    df["evento"].isin(sel_e) &
    (df["fecha"] >= sel_d[0]) &
    (df["fecha"] <= sel_d[1])
]

# ────────────────────────────────────────────────────────────────────
# 4. KPIs
# ────────────────────────────────────────────────────────────────────
ataj = df_f[df_f["evento"]=="Atajada"].shape[0]
gol  = df_f[df_f["evento"]=="Gol Recibido"].shape[0]
pases= df_f[df_f["evento"]=="Pase"]
tot_p= len(pases)
ok_p = (pases["pase_exitoso"]=="Sí").sum()
ef_p = f"{(ok_p*100/tot_p):.1f}%" if tot_p else "—"
ef_a = f"{(ataj*100/(ataj+gol)):.1f}%" if (ataj+gol) else "—"

st.subheader("📌 Indicadores Clave")
c1, c2, c3, c4 = st.columns(4, gap="small")
c1.metric("🧤 Atajadas", ataj)
c2.metric("🥅 Goles recibidos", gol)
c3.metric("🎯 Eficiencia pases", ef_p)
c4.metric("✅ Eficacia atajadas", ef_a)
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5A. SEGMENTO A – Atajadas
# ────────────────────────────────────────────────────────────────────
ata = df_f[df_f["evento"]=="Atajada"]
if not ata.empty:
    st.markdown("### 🧤 Segmento A – Atajadas")
    ca, cb = st.columns(2, gap="small")
    with ca:
        fig, ax = plt.subplots(figsize=(2.5,1.8))
        ata["tipo_intervencion"].value_counts().plot.bar(
            ax=ax, color="#74b9ff", width=0.6
        )
        ax.set_title("Tipo de intervención", pad=4, fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        plt.tight_layout()
        st.pyplot(fig)
    with cb:
        fig, ax = plt.subplots(figsize=(2.5,1.8))
        ata["resultado_parada"].value_counts().plot.bar(
            ax=ax, color="#ff7675", width=0.6
        )
        ax.set_title("Resultado de la parada", pad=4, fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        plt.tight_layout()
        st.pyplot(fig)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5B. SEGMENTO B – Goles Recibidos & Zona de Remate
# ────────────────────────────────────────────────────────────────────
gol_rec = df_f[df_f["evento"]=="Gol Recibido"]
if not gol_rec.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")

    # — Zona 1–9 compacta —
    cnt9 = gol_rec["zona_gol"] \
        .value_counts().reindex(range(1,10), fill_value=0)
    mat9 = cnt9.values.reshape(3,3)[::-1]
    fig, ax = plt.subplots(figsize=(1.5,1.5))
    ax.imshow(mat9, cmap="Reds", aspect='equal')
    for i in range(3):
        for j in range(3):
            ax.text(j, i, mat9[i,j],
                    ha="center", va="center", fontsize=6)
    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)

    # — Zona remate 1–20 (grid 4×5, de izq→der 1→20) —
    st.markdown("#### 🔴 Mapa de calor: Zona remate 1–20")
    xs = [0.125, 0.375, 0.625, 0.875]
    ys = [0.90, 0.70, 0.50, 0.30, 0.10]
    grid = [
        [("1",1),  ("6",1),  ("11",1), ("16",1)],
        [("2",1),  ("7",1),  ("12",1), ("17",3)],
        [("3",1),  ("8",1),  ("13",1), ("18",2)],
        [("4",1),  ("9",1),  ("14",1), ("19",3)],
        [("5",1),  ("10",1), ("15",1), ("20",1)],
    ]
    cnt20 = gol_rec["zona_remate"].value_counts().to_dict()

    fig2, ax2 = plt.subplots(figsize=(4,1.2))
    ax2.add_patch(patches.Rectangle((0,0),1,1,
                       facecolor="#fafafa", edgecolor="none"))
    cell_w, cell_h = 0.23, 0.16

    for r, row in enumerate(grid):
        for c, (z, n) in enumerate(row):
            cx, cy = xs[c], ys[r]
            x0, y0 = cx - cell_w/2, cy - cell_h/2
            subs = np.linspace(x0, x0+cell_w, n+1)[:-1]
            labels = [""] if n==1 else (["b","a"] if n==2 else ["c","b","a"])
            for i, sx in enumerate(subs):
                key   = z + labels[i]
                total = cnt20.get(key, 0)
                color = "#d32f2f" if total>0 else "#fafafa"
                ax2.add_patch(patches.Rectangle(
                    (sx, y0), cell_w/n, cell_h,
                    facecolor=color, edgecolor="#cccccc", lw=0.5
                ))
                lbl = key if n>1 else z
                ax2.text(sx+0.005, y0+cell_h*0.55,
                         lbl, fontsize=6, ha="left", va="center")
                ax2.text(sx+0.005, y0+cell_h*0.30,
                         str(total), fontsize=6, ha="left", va="center")

    ax2.axis("off")
    plt.tight_layout()
    st.pyplot(fig2)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5C. SEGMENTO C – Pases (Mini barra)
# ────────────────────────────────────────────────────────────────────
pas = df_f[df_f["evento"]=="Pase"]
if not pas.empty:
    st.markdown("### 🟢 Segmento C – Pases")
    tasas = (
        pas.groupby("tipo_pase")["pase_exitoso"]
           .apply(lambda s: (s=="Sí").sum()/len(s))
           .sort_index()
    )
    fig, ax = plt.subplots(figsize=(1.8,0.8))
    ax.barh(tasas.index, tasas.values, color="#00bfa5", height=0.3)
    for i, v in enumerate(tasas.values):
        ax.text(v+0.005, i, f"{v*100:.0f}%", va="center", fontsize=6)
    ax.set_xlim(0,1); ax.tick_params(labelsize=6)
    plt.tight_layout()
    st.pyplot(fig)

# ────────────────────────────────────────────────────────────────────
# 6. TABLA DETALLADA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=200)
buf = StringIO(); df_f.to_csv(buf, index=False)
st.download_button("📥 Descargar CSV", buf.getvalue(), "filtrado.csv", "text/csv")
