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
f = st.file_uploader("Sube tu CSV (registro_porteros.csv)", type="csv")
if not f:
    st.info("Sube el CSV para ver el dashboard.")
    st.stop()

df = pd.read_csv(f, parse_dates=["fecha"])
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
# 5B. SEGMENTO B – Goles recibidos
# ────────────────────────────────────────────────────────────────────
gol = df_f[df_f["evento"]=="Gol Recibido"]
if not gol.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")

    # (a) Zona gol 1–9 (3×3)
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

    # (b) Zona remate 1–20 FULL WIDTH con subdivisiones
    st.markdown("#### 🔴 Segmento B – Mapa de calor: Zona de remate 1–20")
    xs = [0.875, 0.625, 0.375, 0.125]  # columnas de derecha a izquierda
    ys = [0.90, 0.70, 0.50, 0.30, 0.10]  # filas de arriba a abajo
    zone_map = {
        "1":  (xs[0], ys[0]), "2":  (xs[0], ys[1]),
        "3":  (xs[0], ys[2]), "4":  (xs[0], ys[3]),
        "5":  (xs[0], ys[4]),
        "6":  (xs[1], ys[0]), "7":  (xs[1], ys[1]),
        "8":  (xs[1], ys[2]), "9":  (xs[1], ys[3]),
        "10": (xs[1], ys[4]),
        "11": (xs[2], ys[0]), "12": (xs[2], ys[1]),
        "13": (xs[2], ys[2]), "14": (xs[2], ys[3]),
        "15": (xs[2], ys[4]),
        "16": (xs[3], ys[0]), "17": (xs[3], ys[1]),
        "18": (xs[3], ys[2]), "19": (xs[3], ys[3]),
        "20": (xs[3], ys[4]),
    }
    cnt20 = gol["zona_remate"].value_counts().to_dict()
    mx20  = max(cnt20.values()) if cnt20 else 1

    fig, ax = plt.subplots(figsize=(8,2))
    ax.add_patch(patches.Rectangle((0,0),1,1, facecolor="#fff5f0", edgecolor="none"))
    cell_w, cell_h = 0.23, 0.17

    for z, (cx, cy) in zone_map.items():
        x0 = cx - cell_w/2
        y0 = 1 - cy - cell_h/2  # invertir Y para colocar fila superior arriba

        # determinar subdivisiones
        if z in ("17","19"):
            n = 3
        elif z == "18":
            n = 2
        else:
            n = 1

        subs = np.linspace(x0, x0 + cell_w, n+1)[:-1]
        cnt = cnt20.get(z, 0)
        col = plt.cm.Reds(cnt/mx20)

        for idx, sx in enumerate(subs):
            w = cell_w / n
            ax.add_patch(patches.Rectangle(
                (sx, y0), w, cell_h,
                facecolor=col, edgecolor="#cccccc", lw=0.7
            ))
            # etiqueta en primera subcelda
            if idx == 0:
                label = z if n == 1 else f"{z}{'abc'[idx]}"
                ax.text(sx + 0.01, y0 + cell_h*0.55, label,
                        fontsize=8, ha="left", va="center")
                ax.text(sx + 0.01, y0 + cell_h*0.30, str(cnt),
                        fontsize=8, ha="left", va="center")

    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5C. SEGMENTO C – Pases (Radar)
# ────────────────────────────────────────────────────────────────────
p = df_f[df_f["evento"]=="Pase"]
if not p.empty:
    st.markdown("### 🟢 Segmento C – Pases (Radar)")
    tipos = ["Corto","Medio","Largo","Despeje"]
    tasas = [
        ((p["tipo_pase"]==t) & (p["pase_exitoso"]=="Sí")).sum() /
        max(1, (p["tipo_pase"]==t).sum())
        for t in tipos
    ]
    angles = np.linspace(0, 2*np.pi, len(tipos), endpoint=False).tolist()
    tasas += tasas[:1]; angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4,2), subplot_kw=dict(polar=True))
    ax.plot(angles, tasas, marker="o", color="#55efc4", linewidth=1.5)
    ax.fill(angles, tasas, alpha=0.3, color="#55efc4")
    ax.set_thetagrids(np.degrees(angles[:-1]), tipos, fontsize=8)
    ax.set_ylim(0,1); ax.set_yticks([0,0.5,1])
    ax.set_yticklabels(["0%","50%","100%"], fontsize=7)
    ax.grid(color="#aaaaaa", linestyle="--", linewidth=0.5)
    plt.tight_layout()
    st.pyplot(fig)

# ────────────────────────────────────────────────────────────────────
# 6. TABLA DETALLADA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=200)
buf = StringIO()
df_f.to_csv(buf, index=False)
st.download_button("💾 Descargar CSV", buf.getvalue(), "filtrado.csv", "text/csv")
