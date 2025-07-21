import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from datetime import date

# ────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Porteros",
    layout="wide",
)

st.title("📊 Dashboard de Rendimiento de Porteros")

# ────────────────────────────────────────────────────────────────────
# 1. CARGA DE DATOS
# ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Sube tu CSV (registro_porteros.csv)", type="csv", key="uploader"
)
if not uploaded:
    st.info("Sube el CSV exportado desde la app para visualizar el dashboard.")
    st.stop()

df = pd.read_csv(uploaded, parse_dates=["fecha"])
df["fecha"] = df["fecha"].dt.date

# ────────────────────────────────────────────────────────────────────
# 2. FILTROS GLOBALES
# ────────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")
# Porteros (multi)
porteros = sorted(df["portero"].unique())
sel_p = st.sidebar.multiselect("Portero(s)", porteros, default=porteros)
# Fechas
min_f, max_f = df["fecha"].min(), df["fecha"].max()
sel_fecha = st.sidebar.date_input("Rango de fechas", [min_f, max_f], min_value=min_f, max_value=max_f)
# Eventos
eventos = sorted(df["evento"].unique())
sel_e = st.sidebar.multiselect("Evento(s)", eventos, default=eventos)

df_f = df[
    df["portero"].isin(sel_p) &
    df["evento"].isin(sel_e) &
    (df["fecha"] >= sel_fecha[0]) &
    (df["fecha"] <= sel_fecha[1])
]

# ────────────────────────────────────────────────────────────────────
# 3. KPIs
# ────────────────────────────────────────────────────────────────────
st.subheader("📌 Indicadores Clave")
a = df_f[df_f["evento"] == "Atajada"].shape[0]
g = df_f[df_f["evento"] == "Gol Recibido"].shape[0]
p = df_f[df_f["evento"] == "Pase"].shape[0]
t = a + g
ef = f"{a*100/t:.1f}%" if t else "—"

k1, k2, k3, k4 = st.columns(4, gap="small")
k1.metric("🧤 Atajadas", a)
k2.metric("🥅 Goles recibidos", g)
k3.metric("🎯 Pases", p)
k4.metric("✅ Efectividad", ef)
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 4. SEGMENTOS
# ────────────────────────────────────────────────────────────────────

## 4A: Atajadas
ata = df_f[df_f["evento"] == "Atajada"]
if not ata.empty:
    st.markdown("### 🧤 Atajadas")
    c1, c2 = st.columns(2, gap="small")
    with c1:
        fig = px.histogram(
            ata, x="tipo_intervencion",
            title="Tipo de intervención",
            text_auto=True
        )
        fig.update_layout(margin=dict(t=30,b=0), height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(
            ata, x="resultado_parada",
            title="Resultado de la parada",
            text_auto=True
        )
        fig.update_layout(margin=dict(t=30,b=0), height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

## 4B: Goles recibidos
gol = df_f[df_f["evento"] == "Gol Recibido"]
if not gol.empty:
    st.markdown("### ⚽ Goles Recibidos")

    # 4B.1 Zona de gol 1–9 como heatmap 3×3
    cnt_gz = gol["zona_gol"].value_counts().reindex(range(1,10), fill_value=0)
    matrix = cnt_gz.values.reshape(3,3)[::-1]  # invertir filas
    fig = px.imshow(
        matrix,
        labels=dict(x="Columna", y="Fila", color="Goles"),
        x=["1","2","3"], y=["7‑9","4‑6","1‑3"],
        color_continuous_scale="Reds",
        text_auto=True
    )
    fig.update_layout(margin=dict(t=30,b=0), height=350)
    st.plotly_chart(fig, use_container_width=True)

    # 4B.2 Zona de remate 1–20 sobre tu diagrama
    st.markdown("#### 🔴 Zonas de remate")
    img = Image.open("static/zonas_remate.png")
    fig2 = go.Figure()
    fig2.add_layout_image(
        dict(source=img, xref="x", yref="y", x=0, y=1, sizex=1, sizey=1, sizing="stretch", layer="below")
    )
    cnt = gol["zona_remate"].value_counts().to_dict()
    maxc = max(cnt.values()) if cnt else 1
    # posiciones normalizadas (ajusta si hiciera falta)
    positions = {
        "1":(.93,.85), "2":(.81,.85), "3":(.69,.85), "4":(.57,.85),
        "5":(.45,.85), "6":(.33,.85), "7":(.21,.85), "8":(.09,.85),
        "9":(.93,.55), "10":(.81,.55), "11":(.69,.55), "12":(.57,.55),
        "13":(.45,.55), "14":(.33,.55), "15":(.21,.55), "16":(.09,.55),
        "17a":(.93,.25),"17b":(.81,.25),"17c":(.69,.25),
        "18a":(.57,.25),"18b":(.45,.25),
        "19a":(.33,.25),"19b":(.21,.25),"19c":(.09,.25),
        "20":(.57,.05)
    }
    for z, (x,y) in positions.items():
        c = cnt.get(z, 0)
        fig2.add_trace(go.Scatter(
            x=[x], y=[1-y],
            mode="markers+text",
            text=[f"{c}" if c else ""],
            textfont=dict(size=10,color="black"),
            marker=dict(size=10 + (c/maxc)*20, color="red", opacity=0.6),
            hoverinfo="text",
            hovertext=f"Zona {z}: {c} goles"
        ))
    fig2.update_xaxes(visible=False, range=[0,1])
    fig2.update_yaxes(visible=False, range=[0,1])
    fig2.update_layout(margin=dict(t=30,b=0), height=400, title="Mapa de calor: Zona de remate")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")

## 4C: Pases
pas = df_f[df_f["evento"] == "Pase"]
if not pas.empty:
    st.markdown("### 🟢 Pases")
    fig = px.histogram(
        pas, x="tipo_pase", color="pase_exitoso",
        title="Precisión por tipo de pase",
        text_auto=True, barmode="group"
    )
    fig.update_layout(margin=dict(t=30,b=0), height=350, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────────────────────────
# 5. TABLA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=300)
csv = df_f.to_csv(index=False).encode("utf-8")
st.download_button("💾 Descargar CSV", data=csv, file_name="filtrado.csv", mime="text/csv")
