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
st.set_page_config("Dashboard Porteros", layout="wide")
st.title("📊 Dashboard de Rendimiento de Porteros")
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 2. CARGA DE DATOS
# ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Sube tu CSV (registro_porteros.csv)", type="csv")
if not uploaded:
    st.info("Sube el CSV para ver el dashboard.")
    st.stop()

df = pd.read_csv(uploaded, parse_dates=["fecha"])
df["fecha"] = df["fecha"].dt.date

# ────────────────────────────────────────────────────────────────────
# 3. FILTROS GLOBALES
# ────────────────────────────────────────────────────────────────────
st.sidebar.header("📋 Filtros")
ports = sorted(df["portero"].unique())
sel_p = st.sidebar.multiselect("Portero(s)", ports, default=ports)

min_d, max_d = df["fecha"].min(), df["fecha"].max()
sel_d = st.sidebar.date_input(
    "Rango de fechas",
    [min_d, max_d],
    min_value=min_d,
    max_value=max_d
)

evs = sorted(df["evento"].unique())
sel_e = st.sidebar.multiselect("Evento(s)", evs, default=evs)

df_f = df[
    df["portero"].isin(sel_p) &
    df["evento"].isin(sel_e) &
    (df["fecha"] >= sel_d[0]) &
    (df["fecha"] <= sel_d[1])
]

# ────────────────────────────────────────────────────────────────────
# 4. KPIs
# ────────────────────────────────────────────────────────────────────
atjs = df_f[df_f["evento"]=="Atajada"].shape[0]
gls  = df_f[df_f["evento"]=="Gol Recibido"].shape[0]
ps   = df_f[df_f["evento"]=="Pase"]
tot_ps = len(ps)
ok_ps  = (ps["pase_exitoso"]=="Sí").sum()
ef_ps  = f"{(ok_ps*100/tot_ps):.1f}%" if tot_ps else "—"
ef_at  = f"{(atjs*100/(atjs+gls)):.1f}%" if (atjs+gls) else "—"

st.subheader("📌 Indicadores Clave")
c1, c2, c3, c4 = st.columns(4, gap="small")
c1.metric("🧤 Atajadas", atjs)
c2.metric("🥅 Goles recibidos", gls)
c3.metric("🎯 Eficiencia pases", ef_ps)
c4.metric("✅ Eficacia atajadas", ef_at)
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5A. SEGMENTO A – Atajadas
# ────────────────────────────────────────────────────────────────────
ata = df_f[df_f["evento"]=="Atajada"]
if not ata.empty:
    st.markdown("### 🧤 Segmento A – Atajadas")
    ca, cb = st.columns(2, gap="small")
    with ca:
        fig, ax = plt.subplots(figsize=(3,2))
        ata["tipo_intervencion"].value_counts().plot.bar(
            ax=ax, color="#74b9ff", width=0.6
        )
        ax.set_title("Tipo de intervención", fontsize=10, pad=6)
        ax.tick_params(axis='x', rotation=45, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        plt.tight_layout()
        st.pyplot(fig)
    with cb:
        fig, ax = plt.subplots(figsize=(3,2))
        ata["resultado_parada"].value_counts().plot.bar(
            ax=ax, color="#ff7675", width=0.6
        )
        ax.set_title("Resultado de la parada", fontsize=10, pad=6)
        ax.tick_params(axis='x', rotation=45, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        plt.tight_layout()
        st.pyplot(fig)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5B. SEGMENTO B – Goles recibidos & Zona de remate
# ────────────────────────────────────────────────────────────────────
gol = df_f[df_f["evento"]=="Gol Recibido"]
if not gol.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")

    # (a) Zona de gol 1–9
    cnt9 = gol["zona_gol"].value_counts().reindex(range(1,10), fill_value=0)
    mat9 = cnt9.values.reshape(3,3)[::-1]
    fig, ax = plt.subplots(figsize=(3,3))
    ax.imshow(mat9, cmap="Reds", aspect='equal')
    for i in range(3):
        for j in range(3):
            ax.text(j, i, mat9[i,j], ha="center", va="center", fontsize=9)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Zona de gol 1–9", fontsize=11, pad=6)
    plt.tight_layout()
    st.pyplot(fig)

    # (b) Zona de remate full–width con subdivisiones
    st.markdown("#### 🔴 Segmento B – Mapa de calor: Zona de remate 1–20")
    xs = [0.875, 0.625, 0.375, 0.125]  # columnas de derecha→izquierda
    ys = [0.90,   0.70,   0.50,   0.30,   0.10]  # filas arriba→abajo
    zone_map = {
        **{str(i): (xs[0], ys[i-1]) for i in range(1,6)},   # 1–5
        **{str(i): (xs[1], ys[i-6]) for i in range(6,11)},  # 6–10
        **{str(i): (xs[2], ys[i-11]) for i in range(11,16)},# 11–15
        "16": (xs[3], ys[0]), "17": (xs[3], ys[1]),
        "18": (xs[3], ys[2]), "19": (xs[3], ys[3]),
        "20": (xs[3], ys[4]),
    }
    cnt20 = gol["zona_remate"].value_counts().to_dict()
    mx20  = max(cnt20.values()) if cnt20 else 1

    fig, ax = plt.subplots(figsize=(8,2))
    ax.add_patch(patches.Rectangle((0,0),1,1, facecolor="#fff5f0", edgecolor="none"))
    w, h = 0.23, 0.17

    for z, (cx, cy) in zone_map.items():
        x0 = cx - w/2
        y0 = cy - h/2
        # subdividir
        if   z in ("17","19"): n = 3
        elif z == "18":       n = 2
        else:                 n = 1
        subs_x = np.linspace(x0, x0 + w, n+1)[:-1]
        total = cnt20.get(z, 0)
        color = plt.cm.Reds(total/mx20)
        for i, sx in enumerate(subs_x):
            ax.add_patch(patches.Rectangle(
                (sx, y0), w/n, h,
                facecolor=color, edgecolor="#cccccc", lw=0.7
            ))
            label = z if n==1 else f"{z}{['a','b','c'][i]}"
            ax.text(sx + 0.01, y0 + h*0.55, label,
                    fontsize=8, ha="left", va="center")
            ax.text(sx + 0.01, y0 + h*0.30, str(total),
                    fontsize=8, ha="left", va="center")

    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5C. SEGMENTO C – Pases (Mini barra horizontal)
# ────────────────────────────────────────────────────────────────────
p = df_f[df_f["evento"]=="Pase"]
if not p.empty:
    st.markdown("### 🟢 Segmento C – Pases")
    # Tasa de éxito por tipo de pase
    tasas = (
        p.groupby("tipo_pase")["pase_exitoso"]
         .apply(lambda s: (s=="Sí").sum()/len(s))
         .sort_index()
    )
    fig, ax = plt.subplots(figsize=(4,1.5))
    ax.barh(tasas.index, tasas.values, color="#55efc4")
    for i, v in enumerate(tasas.values):
        ax.text(v + 0.01, i, f"{v*100:.0f}%", va="center", fontsize=8)
    ax.set_xlim(0,1)
    ax.set_xlabel("Eficacia de pase", fontsize=8)
    ax.tick_params(axis='x', labelsize=7)
    ax.tick_params(axis='y', labelsize=8)
    plt.tight_layout()
    st.pyplot(fig)

# ────────────────────────────────────────────────────────────────────
# 6. TABLA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=200)
buf = StringIO()
df_f.to_csv(buf, index=False)
st.download_button("💾 Descargar CSV", buf.getvalue(),
                   "filtrado.csv", "text/csv")
