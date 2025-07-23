import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import StringIO
from datetime import date

# ─────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────
st.set_page_config("Federico Miele EDP - Dashboard", layout="wide")
st.title("Federico Miele EDP - Dashboard")
st.markdown("---")

# ─────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────
csv = st.file_uploader("Sube CSV (registro_porteros.csv)", type="csv")
if not csv:
    st.info("Carga el CSV para continuar."); st.stop()

df = pd.read_csv(csv, parse_dates=["fecha"])
df["fecha"] = df["fecha"].dt.date

# ─────────────────────────────
# FILTROS GLOBALES
# ─────────────────────────────
st.sidebar.header("Filtros")
porteros = sorted(df["portero"].unique())
sel_p    = st.sidebar.multiselect("Portero(s)", porteros, default=porteros)

min_d, max_d = df["fecha"].min(), df["fecha"].max()
sel_d = st.sidebar.date_input("Rango fechas", [min_d, max_d],
                              min_value=min_d, max_value=max_d)

eventos = sorted(df["evento"].unique())
sel_e   = st.sidebar.multiselect("Evento(s)", eventos, default=eventos)

df_f = df[
    df["portero"].isin(sel_p) &
    df["evento"].isin(sel_e) &
    (df["fecha"] >= sel_d[0]) &
    (df["fecha"] <= sel_d[1])
]

# ─────────────────────────────
# KPIs PRINCIPALES
# ─────────────────────────────
ata = int(df_f[df_f["evento"]=="Atajada"].shape[0])
gol = int(df_f[df_f["evento"]=="Gol Recibido"].shape[0])
pas = df_f[df_f["evento"]=="Pase"]
tot_p = int(len(pas))
ok_p  = int((pas["pase_exitoso"]=="Sí").sum())
ef_p  = f"{(ok_p*100/tot_p):.1f}%" if tot_p else "—"
ef_a  = f"{(ata*100/(ata+gol)):.1f}%" if (ata+gol) else "—"

k1, k2, k3, k4 = st.columns(4, gap="small")
k1.metric("🧤 Atajadas", ata)
k2.metric("🥅 Goles recibidos", gol)
k3.metric("🎯 Eficiencia pases", ef_p)
k4.metric("✅ Eficacia atajadas", ef_a)
st.markdown("---")

# ─────────────────────────────
# SEGMENTO A: Atajadas
# ─────────────────────────────
ataja = df_f[df_f["evento"]=="Atajada"]
if not ataja.empty:
    st.markdown("### 🧤 Segmento A – Atajadas")
    col1, col2 = st.columns(2, gap="small")
    with col1:
        fig, ax = plt.subplots(figsize=(2.6,1.8))
        vals = ataja["tipo_intervencion"].value_counts().sort_index()
        ax.bar(vals.index, vals.values, color="#74b9ff", width=0.6)
        ax.set_title("Tipo de intervención", pad=4, fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        for i, v in enumerate(vals.values):
            ax.text(i, v+0.15, f"{int(v)}", ha="center", va="bottom", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
    with col2:
        fig, ax = plt.subplots(figsize=(2.6,1.8))
        vals = ataja["resultado_parada"].value_counts().sort_index()
        ax.bar(vals.index, vals.values, color="#ff7675", width=0.6)
        ax.set_title("Resultado de la parada", pad=4, fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        for i, v in enumerate(vals.values):
            ax.text(i, v+0.15, f"{int(v)}", ha="center", va="bottom", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
    st.markdown("---")

# ─────────────────────────────
# SEGMENTO B: Goles Recibidos
# ─────────────────────────────
goles = df_f[df_f["evento"]=="Gol Recibido"]
if not goles.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")
    col1, col2 = st.columns(2, gap="small")

    # Zona gol 1–9 (3x3)
    with col1:
        cnt9 = goles["zona_gol"].value_counts().reindex(range(1,10), fill_value=0)
        mat9 = cnt9.values.reshape(3,3)[::-1]
        fig, ax = plt.subplots(figsize=(1.5,1.5))
        ax.imshow(mat9, cmap="Reds", aspect='equal')
        for i in range(3):
            for j in range(3):
                ax.text(j, i, mat9[i,j], ha="center", va="center", fontsize=8)
        ax.axis("off")
        plt.tight_layout()
        st.pyplot(fig)
        st.caption("Zona de gol (1–9)")

    # Goles por intervalo de tiempo
    with col2:
        if "intervalo" in goles:
            intervalos = ["0–15","16–30","31–45","46–60","61–75","76–90"]
            goles["intervalo"] = pd.Categorical(goles["intervalo"], categories=intervalos, ordered=True)
            cnt_iv = goles["intervalo"].value_counts().reindex(intervalos, fill_value=0)
            fig, ax = plt.subplots(figsize=(2.6,1.5))
            ax.bar(cnt_iv.index, cnt_iv.values, color="#d35400", width=0.7)
            ax.set_title("Goles por intervalo", pad=5, fontsize=10)
            ax.tick_params(axis='x', rotation=30, labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
            for i, v in enumerate(cnt_iv.values):
                ax.text(i, v+0.1, f"{int(v)}", ha="center", va="bottom", fontsize=8)
            plt.tight_layout()
            st.pyplot(fig)
    st.markdown("")

    # Mapa de calor: Zona de remate 1–20 (ESQUINA SUP DERECHA=1)
    st.markdown("#### 🔴 Mapa de calor: Zona de remate 1–20")
    xs = [0.875, 0.625, 0.375, 0.125]  # derecha→izquierda
    ys = [0.90, 0.70, 0.50, 0.30, 0.10]  # arriba→abajo
    grid = [
        [("1",1),  ("6",1),  ("11",1), ("16",1)],
        [("2",1),  ("7",1),  ("12",1), ("17",3)],
        [("3",1),  ("8",1),  ("13",1), ("18",2)],
        [("4",1),  ("9",1),  ("14",1), ("19",3)],
        [("5",1),  ("10",1), ("15",1), ("20",1)],
    ]
    cnt20 = goles["zona_remate"].value_counts().to_dict()
    fig2, ax2 = plt.subplots(figsize=(4.2,1.3))
    ax2.add_patch(patches.Rectangle((0,0),1,1, facecolor="#fafafa", edgecolor="none"))
    cell_w, cell_h = 0.23, 0.16
    for r, row in enumerate(grid):
        for c, (z, n) in enumerate(row):
            cx, cy = xs[c], ys[r]
            x0, y0 = cx - cell_w/2, cy - cell_h/2
            subs = np.linspace(x0, x0+cell_w, n+1)[:-1]
            labels = [""] if n==1 else (["b","a"] if n==2 else ["c","b","a"])
            for i, sx in enumerate(subs):
                key = z + labels[i]
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
                         str(int(total)), fontsize=6, ha="left", va="center")
    ax2.axis("off")
    plt.tight_layout()
    st.pyplot(fig2)
    st.markdown("---")

# ─────────────────────────────
# SEGMENTO C: Pases
# ─────────────────────────────
pases = df_f[df_f["evento"]=="Pase"]
if not pases.empty:
    st.markdown("### 🟢 Segmento C – Pases")
    tasas = (
        pases.groupby("tipo_pase")["pase_exitoso"]
             .apply(lambda s: (s=="Sí").sum()/len(s))
             .sort_index()
    )
    fig, ax = plt.subplots(figsize=(1.8,0.8))
    ax.barh(tasas.index, (pases["tipo_pase"].value_counts()[tasas.index]).astype(int), color="#00bfa5", height=0.3)
    for i, t in enumerate(tasas.index):
        v = pases["tipo_pase"].value_counts()[t]
        ax.text(v+0.05, i, f"{int(v)}", va="center", fontsize=7)
    ax.set_xlabel("Nº")
    ax.tick_params(labelsize=6)
    plt.tight_layout()
    st.pyplot(fig)

    fig2, ax2 = plt.subplots(figsize=(1.8,0.8))
    ax2.barh(tasas.index, tasas.values*100, color="#0984e3", height=0.3)
    for i, v in enumerate(tasas.values):
        ax2.text(v*100+1, i, f"{v*100:.1f}%", va="center", fontsize=7)
    ax2.set_xlim(0,100)
    ax2.set_xlabel("% éxito")
    ax2.tick_params(labelsize=6)
    plt.tight_layout()
    st.pyplot(fig2)
    st.markdown("---")

# ─────────────────────────────
# TABLA DETALLADA Y DESCARGA
# ─────────────────────────────
st.subheader("📄 Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=200)
buf = StringIO(); df_f.to_csv(buf, index=False)
st.download_button("📥 Descargar CSV", buf.getvalue(), "filtrado.csv", "text/csv")
