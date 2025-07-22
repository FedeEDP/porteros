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
st.markdown("—" * 50)

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
sel_fecha = st.sidebar.date_input(
    "Rango de fechas", [min_f, max_f], min_value=min_f, max_value=max_f
)
eventos = sorted(df["evento"].unique())
sel_e   = st.sidebar.multiselect("Evento(s)", eventos, default=eventos)

df_f = df[
    df["portero"].isin(sel_p) &
    df["evento"].isin(sel_e) &
    (df["fecha"] >= sel_fecha[0]) &
    (df["fecha"] <= sel_fecha[1])
]

# ────────────────────────────────────────────────────────────────────
# 4. KPIs
# ────────────────────────────────────────────────────────────────────
ataj = df_f[df_f["evento"]=="Atajada"].shape[0]
gol  = df_f[df_f["evento"]=="Gol Recibido"].shape[0]
pas  = df_f[df_f["evento"]=="Pase"]
tot_p = len(pas)
ok_p  = (pas["pase_exitoso"]=="Sí").sum()
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
        ata["tipo_intervencion"].value_counts().plot.bar(ax=ax, color="#74b9ff")
        ax.set_title("Tipo de intervención", pad=6)
        ax.set_ylabel("Nº", fontsize=8)
        plt.xticks(rotation=45, ha="right", fontsize=7)
        plt.yticks(fontsize=7)
        plt.tight_layout()
        st.pyplot(fig)
    with cb:
        fig, ax = plt.subplots(figsize=(3,2))
        ata["resultado_parada"].value_counts().plot.bar(ax=ax, color="#ff7675")
        ax.set_title("Resultado de la parada", pad=6)
        ax.set_ylabel("Nº", fontsize=8)
        plt.xticks(rotation=45, ha="right", fontsize=7)
        plt.yticks(fontsize=7)
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

    # — Zona 1–9 (3×3) —
    with d1:
        cnt9 = gol_rec["zona_gol"].value_counts().reindex(range(1,10), fill_value=0)
        mat  = cnt9.values.reshape(3,3)[::-1]
        fig, ax = plt.subplots(figsize=(3,3))
        ax.imshow(mat, cmap="Reds")
        for i in range(3):
            for j in range(3):
                ax.text(j, i, mat[i,j], ha="center", va="center", fontsize=8)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title("Zona de gol 1–9", pad=6)
        plt.tight_layout()
        st.pyplot(fig)

    # — Zona remate 1–20 (4×5 rectángulos) —
    with d2:
        st.markdown("#### 🔴 Zona de remate 1–20")
        # mapeo 4 columnas × 5 filas
        zone_map = {
            # fila 1 (arriba)
            "16":(0.05,0.80), "11":(0.30,0.80), "6":(0.55,0.80), "1":(0.80,0.80),
            # fila 2
            "17a":(0.05,0.60), "12":(0.30,0.60), "7":(0.55,0.60), "2":(0.80,0.60),
            # fila 3
            "17b":(0.05,0.40), "13":(0.30,0.40), "8":(0.55,0.40), "3":(0.80,0.40),
            # fila 4
            "17c":(0.05,0.20), "14":(0.30,0.20), "9":(0.55,0.20), "4":(0.80,0.20),
            # fila 5 (abajo)
            "20":(0.05,0.05), "15":(0.30,0.05), "10":(0.55,0.05), "5":(0.80,0.05),
        }
        cnt20 = gol_rec["zona_remate"].value_counts().to_dict()
        mx20 = max(cnt20.values()) if cnt20 else 1

        fig, ax = plt.subplots(figsize=(4,2.5))
        # fondo muy suave
        ax.add_patch(patches.Rectangle((0,0),1,1,facecolor="#fff5f0",edgecolor="none"))
        for z,(cx,cy) in zone_map.items():
            c = cnt20.get(z,0)
            clr = plt.cm.Reds(c/mx20)
            # rectángulo
            ax.add_patch(patches.Rectangle(
                (cx-0.13, cy-0.08), 0.26, 0.16,
                facecolor=clr, edgecolor="gray", lw=0.5
            ))
            ax.text(cx-0.05, cy+0.01, z, fontsize=7, ha="left", va="center")
            ax.text(cx-0.05, cy-0.04, str(c), fontsize=7, ha="left", va="center")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title("Mapa calor: zona remate", pad=6)
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5C. SEGMENTO C – Pases (Radar)
# ────────────────────────────────────────────────────────────────────
pases = df_f[df_f["evento"]=="Pase"]
if not pases.empty:
    st.markdown("### 🟢 Segmento C – Pases (Radar)")
    tipos = ["Corto","Medio","Largo","Despeje"]
    tasas = [( (pases["tipo_pase"]==t) & (pases["pase_exitoso"]=="Sí") ).sum() /
             max(1, (pases["tipo_pase"]==t).sum())
             for t in tipos]

    angles = np.linspace(0, 2*np.pi, len(tipos), endpoint=False).tolist()
    tasas += tasas[:1]; angles += angles[:1]

    fig, ax = plt.subplots(figsize=(3.5,2.5), subplot_kw=dict(polar=True))
    ax.plot(angles, tasas, marker="o", color="#55efc4")
    ax.fill(angles, tasas, alpha=0.3, color="#55efc4")
    ax.set_thetagrids(np.degrees(angles[:-1]), tipos, fontsize=8)
    ax.set_ylim(0,1)
    ax.set_yticks([0,0.5,1]); ax.set_yticklabels(["0%","50%","100%"], fontsize=7)
    ax.set_title("Tasa éxito por tipo de pase", pad=8, fontsize=10)
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
st.download_button("💾 Descargar CSV", buf.getvalue(), "filtrado.csv", "text/csv")
