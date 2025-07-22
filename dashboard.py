import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import date
from io import StringIO

# ────────────────────────────────────────────────────────────────────
# 1. CONFIGURAR PÁGINA
# ────────────────────────────────────────────────────────────────────
st.set_page_config("Dashboard Porteros", layout="wide")
st.title("📊 Dashboard de Rendimiento de Porteros")

# ────────────────────────────────────────────────────────────────────
# 2. CARGAR DATOS
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
sel_p = st.sidebar.multiselect("Portero(s)", porteros, default=porteros)
min_f, max_f = df["fecha"].min(), df["fecha"].max()
sel_fecha = st.sidebar.date_input(
    "Rango de fechas", [min_f, max_f], min_value=min_f, max_value=max_f
)
eventos = sorted(df["evento"].unique())
sel_e = st.sidebar.multiselect("Evento(s)", eventos, default=eventos)

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
pases = df_f[df_f["evento"]=="Pase"]
tot_pases = len(pases)
ok_pases  = (pases["pase_exitoso"]=="Sí").sum()
ef_pases  = f"{(ok_pases*100/tot_pases):.1f}%" if tot_pases else "—"
ef_ataj   = f"{(ataj*100/(ataj+gol)):.1f}%" if (ataj+gol) else "—"

st.subheader("📌 Indicadores Clave")
k1, k2, k3, k4 = st.columns(4, gap="small")
k1.metric("🧤 Atajadas", ataj)
k2.metric("🥅 Goles recibidos", gol)
k3.metric("🎯 Eficiencia pases", ef_pases)
k4.metric("✅ Eficacia atajadas", ef_ataj)
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5A. SEGMENTO A – Atajadas
# ────────────────────────────────────────────────────────────────────
ataj = df_f[df_f["evento"]=="Atajada"]
if not ataj.empty:
    st.markdown("### 🧤 Segmento A – Atajadas")
    ca, cb = st.columns(2, gap="small")

    with ca:
        fig, ax = plt.subplots(figsize=(4,2.5))
        ataj["tipo_intervencion"] \
            .value_counts() \
            .plot.bar(ax=ax)
        ax.set_title("Tipo de intervención")
        ax.set_ylabel("Cantidad")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

    with cb:
        fig, ax = plt.subplots(figsize=(4,2.5))
        ataj["resultado_parada"] \
            .value_counts() \
            .plot.bar(ax=ax)
        ax.set_title("Resultado de la parada")
        ax.set_ylabel("Cantidad")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5B. SEGMENTO B – Goles recibidos
# ────────────────────────────────────────────────────────────────────
gol_rec = df_f[df_f["evento"]=="Gol Recibido"]
if not gol_rec.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")
    c1, c2 = st.columns(2, gap="small")

    # Zona de gol 1–9 (3×3)
    with c1:
        cnt = gol_rec["zona_gol"] \
            .value_counts() \
            .reindex(range(1,10), fill_value=0)
        mat = cnt.values.reshape(3,3)[::-1]
        fig, ax = plt.subplots(figsize=(3.5,3.5))
        im = ax.imshow(mat, cmap="Reds")
        for i in range(3):
            for j in range(3):
                ax.text(j, i, mat[i,j], ha="center", va="center")
        ax.set_xticks([0,1,2]); ax.set_xticklabels(["1","2","3"])
        ax.set_yticks([0,1,2]); ax.set_yticklabels(["7‑9","4‑6","1‑3"][::-1])
        ax.set_title("Zona de gol 1–9")
        plt.tight_layout()
        st.pyplot(fig)

    # Zona de remate 1–20 con rectángulos
    with c2:
        st.markdown("#### 🔴 Zona de remate 1–20")
        # Mapeo 4×5
        centers = {
            "16":(0.125,0.9),"11":(0.375,0.9),"6":(0.625,0.9), "1":(0.875,0.9),
            "17a":(0.125,0.7),"18a":(0.375,0.7),"12":(0.625,0.7),"7":(0.875,0.7),
            "17b":(0.125,0.5),"18b":(0.375,0.5),"13":(0.625,0.5),"8":(0.875,0.5),
            "17c":(0.125,0.3),"19a":(0.375,0.3),"14":(0.625,0.3),"9":(0.875,0.3),
            "20":(0.125,0.1),"19b":(0.375,0.1),"15":(0.625,0.1),"10":(0.875,0.1)
        }
        counts = gol_rec["zona_remate"] \
            .value_counts().to_dict()
        mx = max(counts.values()) if counts else 1

        fig, ax = plt.subplots(figsize=(4,2.5))
        cell_w, cell_h = 0.23, 0.16
        # dibujar fondo claro
        ax.add_patch(patches.Rectangle((0,0),1,1,
                        facecolor="#fff5f0", edgecolor="lightgray"))
        for z,(cx,cy) in centers.items():
            x0, y0 = cx-cell_w/2, cy-cell_h/2
            cnt = counts.get(z,0)
            color = plt.cm.Reds(cnt/mx)
            ax.add_patch(patches.Rectangle(
                (x0,y0), cell_w, cell_h,
                facecolor=color, edgecolor="gray"
            ))
            ax.text(cx, cy-0.03, z, ha="center", va="center", fontsize=7)
            ax.text(cx, cy+0.03, str(cnt), ha="center", va="center", fontsize=7)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title("Mapa de calor: Zona de remate", pad=10)
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
    valores = [(pases["tipo_pase"]==t).sum() for t in tipos]
    exitos = [(pases["tipo_pase"]==t & (pases["pase_exitoso"]=="Sí")).sum() for t in tipos]
    tasas = [ex/tot if (tot:=val)>0 else 0 for val,ex in zip(valores,exitos)]

    # Radar chart
    angles = np.linspace(0, 2*np.pi, len(tipos), endpoint=False).tolist()
    tasas += tasas[:1]; angles += angles[:1]
    fig, ax = plt.subplots(figsize=(4,3), subplot_kw=dict(polar=True))
    ax.plot(angles, tasas, marker="o")
    ax.fill(angles, tasas, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), tipos)
    ax.set_ylim(0,1)
    ax.set_title("Tasa de éxito por tipo de pase", pad=15)
    st.pyplot(fig)

# ────────────────────────────────────────────────────────────────────
# 6. TABLA DETALLADA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=240)
buf = StringIO()
df_f.to_csv(buf, index=False)
st.download_button("💾 Descargar CSV", buf.getvalue(), "filtrado.csv", "text/csv")
