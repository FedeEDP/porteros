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
    "Rango fechas", [min_d, max_d], min_value=min_d, max_value=max_d
)

eventos = sorted(df["evento"].unique())
sel_e   = st.sidebar.multiselect("Evento(s)", eventos, default=eventos)

df_f = df[
    df["portero"].isin(sel_p) &
    df["evento"].isin(sel_e) &
    (df["fecha"] >= sel_d[0]) &
    (df["fecha"] <= sel_d[1])
]

# ────────────────────────────────────────────────────────────────────
# 4. KPIs
# ────────────────────────────────────────────────────────────────────
a   = df_f[df_f["evento"]=="Atajada"].shape[0]
g   = df_f[df_f["evento"]=="Gol Recibido"].shape[0]
p   = df_f[df_f["evento"]=="Pase"]
tot = len(p)
ok  = (p["pase_exitoso"]=="Sí").sum()
efp = f"{ok*100/tot:.1f}%" if tot else "—"
efa = f"{a*100/(a+g):.1f}%" if (a+g) else "—"

st.subheader("Indicadores Clave")
k1,k2,k3,k4 = st.columns(4, gap="small")
k1.metric("🧤 Atajadas", a)
k2.metric("🥅 Goles Rec.", g)
k3.metric("🎯 Eficiencia Pases", efp)
k4.metric("✅ Eficacia Atajadas", efa)
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5A. SEGMENTO A – Atajadas (Radar compacto)
# ────────────────────────────────────────────────────────────────────
ata = df_f[df_f["evento"]=="Atajada"]
if not ata.empty:
    st.markdown("### 🧤 Segmento A – Atajadas (Radar)")
    tipos = ata["tipo_intervencion"].unique().tolist()
    resu  = ata["resultado_parada"].unique().tolist()
    cats  = tipos + resu

    cnt_i = [ata["tipo_intervencion"].eq(c).sum() for c in cats]
    cnt_r = [ata["resultado_parada"].eq(c).sum()  for c in cats]

    # cerrar radar
    angles = np.linspace(0,2*np.pi,len(cats),endpoint=False).tolist()
    angles += angles[:1]
    cnt_i += cnt_i[:1]
    cnt_r += cnt_r[:1]

    fig, ax = plt.subplots(
        figsize=(2,2),
        subplot_kw=dict(polar=True)
    )
    ax.plot(angles, cnt_i, marker="o", color="#3399ff", linewidth=1)
    ax.fill(angles, cnt_i, alpha=0.2, color="#3399ff")
    ax.plot(angles, cnt_r, marker="o", color="#ff3333", linewidth=1)
    ax.fill(angles, cnt_r, alpha=0.2, color="#ff3333")
    ax.set_thetagrids(np.degrees(angles[:-1]), cats, fontsize=6)
    ax.grid(color="#cccccc", linestyle="--", linewidth=0.5)
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5B. SEGMENTO B – Goles Recibidos & Zona Remate
# ────────────────────────────────────────────────────────────────────
gol = df_f[df_f["evento"]=="Gol Recibido"]
if not gol.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")

    # (a) Zona 1–9 mini
    cnt9 = gol["zona_gol"].value_counts().reindex(range(1,10), fill_value=0)
    mat9 = cnt9.values.reshape(3,3)[::-1]
    fig, ax = plt.subplots(figsize=(2,2))
    ax.imshow(mat9, cmap="Reds", aspect="equal")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, mat9[i,j], ha="center", va="center", fontsize=7)
    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)

    # (b) Zona remate compacto
    st.markdown("#### 🔴 Mapa Calor: Zona Remate 1–20")
    # filas y columnas
    xs = [0.875, 0.625, 0.375, 0.125]
    ys = [0.90,   0.70,   0.50,   0.30,   0.10]
    # configuración de celdas con subdivisiones
    grid = [
        [("16",1), ("11",1), ("6",1), ("1",1)],
        [("17",3), ("12",1), ("7",1), ("2",1)],
        [("18",2), ("13",1), ("8",1), ("3",1)],
        [("19",3), ("14",1), ("9",1), ("4",1)],
        [("20",1), ("15",1), ("10",1), ("5",1)],
    ]
    cnt20 = gol["zona_remate"].value_counts().to_dict()
    fig, ax = plt.subplots(figsize=(5,1.5))
    ax.add_patch(patches.Rectangle((0,0),1,1,
                    facecolor="#fafafa", edgecolor="none"))
    cell_w, cell_h = 0.23, 0.16

    for row_idx, row in enumerate(grid):
        for col_idx, (z, n) in enumerate(row):
            cx, cy = xs[col_idx], ys[row_idx]
            x0, y0 = cx - cell_w/2, cy - cell_h/2
            subs = np.linspace(x0, x0+cell_w, n+1)[:-1]
            # letras de derecha→izquierda
            if n == 1:
                lets = [""]
            elif n == 2:
                lets = ["b","a"]
            else:  # n==3
                lets = ["c","b","a"]
            for i, sx in enumerate(subs):
                key = z + lets[i]
                total = cnt20.get(key, 0)
                color = "#d32f2f" if total>0 else "#fafafa"
                ax.add_patch(patches.Rectangle(
                    (sx, y0), cell_w/n, cell_h,
                    facecolor=color, edgecolor="#cccccc", lw=0.5
                ))
                label = key if n>1 else z
                ax.text(sx + 0.005, y0 + cell_h*0.55,
                        label, fontsize=7, ha="left", va="center")
                ax.text(sx + 0.005, y0 + cell_h*0.30,
                        str(total), fontsize=7, ha="left", va="center")

    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)
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
    fig, ax = plt.subplots(figsize=(2,0.6))
    ax.barh(tasas.index, tasas.values, color="#00bfa5", height=0.25)
    for i, v in enumerate(tasas.values):
        ax.text(v + 0.003, i, f"{v*100:.0f}%",
                va="center", fontsize=6)
    ax.set_xlim(0,1)
    ax.tick_params(labelsize=6)
    plt.tight_layout()
    st.pyplot(fig)

# ────────────────────────────────────────────────────────────────────
# 6. TABLA DETALLADA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=200)
buf = StringIO(); df_f.to_csv(buf, index=False)
st.download_button("📥 Descargar CSV", buf.getvalue(), "filtrado.csv", "text/csv")
