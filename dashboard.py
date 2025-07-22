import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import date
from io import StringIO

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
porteros = sorted(df["portero"].unique())
sel_p    = st.sidebar.multiselect("Portero(s)", porteros, default=porteros)
min_f, max_f = df["fecha"].min(), df["fecha"].max()
sel_fecha = st.sidebar.date_input("Rango de fechas",
                                  [min_f, max_f],
                                  min_value=min_f,
                                  max_value=max_f)
eventos = sorted(df["evento"].unique())
sel_e   = st.sidebar.multiselect("Evento(s)", eventos, default=eventos)

df_f = df[
    df["portero"].isin(sel_p) &
    df["evento"].isin(sel_e) &
    (df["fecha"] >= sel_fecha[0]) &
    (df["fecha"] <= sel_fecha[1])
]

# ────────────────────────────────────────────────────────────────────
# 4. KPIs PRINCIPALES
# ────────────────────────────────────────────────────────────────────
ataj = df_f[df_f["evento"]=="Atajada"].shape[0]
gol  = df_f[df_f["evento"]=="Gol Recibido"].shape[0]
pases_df = df_f[df_f["evento"]=="Pase"]
tot_p = len(pases_df)
ok_p  = (pases_df["pase_exitoso"]=="Sí").sum()
ef_p  = f"{(ok_p*100/tot_p):.1f}%" if tot_p else "—"
ef_a  = f"{(ataj*100/(ataj+gol)):.1f}%" if (ataj+gol) else "—"

st.subheader("📌 Indicadores Clave")
k1,k2,k3,k4 = st.columns(4, gap="small")
k1.metric("🧤 Atajadas", ataj)
k2.metric("🥅 Goles recibidos", gol)
k3.metric("🎯 Eficiencia pases", ef_p)
k4.metric("✅ Eficacia atajadas", ef_a)
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
        ax.set_title("Tipo de intervención", pad=6, fontsize=10)
        ax.set_ylabel("Nº", fontsize=8)
        ax.tick_params(axis='x', labelrotation=45, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        plt.tight_layout()
        st.pyplot(fig)
    with cb:
        fig, ax = plt.subplots(figsize=(3,2))
        ata["resultado_parada"].value_counts().plot.bar(
            ax=ax, color="#ff7675", width=0.6
        )
        ax.set_title("Resultado de la parada", pad=6, fontsize=10)
        ax.set_ylabel("Nº", fontsize=8)
        ax.tick_params(axis='x', labelrotation=45, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        plt.tight_layout()
        st.pyplot(fig)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5B. SEGMENTO B – Goles recibidos
# ────────────────────────────────────────────────────────────────────
gol_rec = df_f[df_f["evento"]=="Gol Recibido"]
if not gol_rec.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")
    d1, d2 = st.columns(2, gap="small")

    # — Zona gol 1–9 (3×3) —
    with d1:
        cnt9 = gol_rec["zona_gol"] \
            .value_counts() \
            .reindex(range(1,10), fill_value=0)
        mat  = cnt9.values.reshape(3,3)[::-1]
        fig, ax = plt.subplots(figsize=(3,3))
        ax.imshow(mat, cmap="Reds", aspect='equal')
        for i in range(3):
            for j in range(3):
                ax.text(j, i, mat[i,j],
                        ha="center", va="center", fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title("Zona de gol 1–9", pad=6, fontsize=12)
        plt.tight_layout()
        st.pyplot(fig)

    # — Zona remate 1–20 (4×5) fuera de columnas —
    st.markdown("")  # separador
    st.markdown("#### 🔴 Mapa de calor: Zona de remate 1–20 (full width)")
    # Definir grid 4×5
    xs = [0.125, 0.375, 0.625, 0.875]
    ys = [0.90, 0.70, 0.50, 0.30, 0.10]
    zone_map = {
        "16": (xs[0], ys[0]), "11": (xs[1], ys[0]),
        "6":  (xs[2], ys[0]), "1":  (xs[3], ys[0]),
        "17a":(xs[0], ys[1]), "12": (xs[1], ys[1]),
        "7":  (xs[2], ys[1]), "2":  (xs[3], ys[1]),
        "17b":(xs[0], ys[2]), "13": (xs[1], ys[2]),
        "8":  (xs[2], ys[2]), "3":  (xs[3], ys[2]),
        "17c":(xs[0], ys[3]), "14": (xs[1], ys[3]),
        "9":  (xs[2], ys[3]), "4":  (xs[3], ys[3]),
        "20": (xs[0], ys[4]), "15": (xs[1], ys[4]),
        "10": (xs[2], ys[4]), "5":  (xs[3], ys[4]),
    }
    cnt20 = gol_rec["zona_remate"].value_counts().to_dict()
    mx20  = max(cnt20.values()) if cnt20 else 1

    fig, ax = plt.subplots(figsize=(8,2.5))
    # fondo muy claro
    ax.add_patch(patches.Rectangle((0,0),1,1,
                    facecolor="#fff5f0", edgecolor="none"))
    cell_w, cell_h = 0.22, 0.16
    for z,(cx,cy) in zone_map.items():
        cnt = cnt20.get(z,0)
        col = plt.cm.Reds(cnt/mx20)
        ax.add_patch(patches.Rectangle(
            (cx-cell_w/2, cy-cell_h/2),
            cell_w, cell_h,
            facecolor=col, edgecolor="#cccccc", lw=0.7
        ))
        # texto zona y conteo
        ax.text(cx-0.06, cy+0.03, z, fontsize=8, ha="left", va="center")
        ax.text(cx-0.06, cy-0.03, str(cnt), fontsize=8, ha="left", va="center")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_title("", pad=0)
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
    # cerrar el radar
    angles = np.linspace(0, 2*np.pi, len(tipos), endpoint=False).tolist()
    tasas += tasas[:1]; angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4,2.5),
                           subplot_kw=dict(polar=True))
    ax.plot(angles, tasas, marker="o", color="#55efc4", linewidth=2)
    ax.fill(angles, tasas, alpha=0.3, color="#55efc4")
    ax.set_thetagrids(np.degrees(angles[:-1]), tipos, fontsize=8)
    ax.set_ylim(0,1)
    ax.set_yticks([0,0.5,1]); ax.set_yticklabels(["0%","50%","100%"], fontsize=7)
    ax.grid(color="#aaaaaa", linestyle="--", linewidth=0.5)
    ax.set_title("Tasa éxito por tipo de pase", pad=8, fontsize=11)
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
