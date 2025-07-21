import os
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
    "Sube tu CSV (registro_porteros.csv)", type="csv"
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
porteros = sorted(df["portero"].unique())
sel_p = st.sidebar.multiselect("Portero(s)", porteros, default=porteros)
min_f, max_f = df["fecha"].min(), df["fecha"].max()
sel_fecha = st.sidebar.date_input("Rango de fechas", [min_f, max_f],
                                  min_value=min_f, max_value=max_f)
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
k4.metric("✅ Efectividad de atajadas", ef)
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 4A: Atajadas
# ────────────────────────────────────────────────────────────────────
ata = df_f[df_f["evento"] == "Atajada"]
if not ata.empty:
    st.markdown("### 🧤 Segmento A – Atajadas")
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

# ────────────────────────────────────────────────────────────────────
# 4B: Goles recibidos
# ────────────────────────────────────────────────────────────────────
gol = df_f[df_f["evento"] == "Gol Recibido"]
if not gol.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")

    # 4B.1 Heatmap 3×3 – Zona Gol
    cnt_gz = gol["zona_gol"].value_counts().reindex(range(1,10), fill_value=0)
    matrix = cnt_gz.values.reshape(3,3)[::-1]  # invertimos filas
    fig1 = px.imshow(
        matrix,
        labels=dict(x="Columna", y="Fila", color="Goles"),
        x=["1","2","3"], y=["7‑9","4‑6","1‑3"],
        color_continuous_scale="Reds",
        text_auto=True
    )
    fig1.update_layout(margin=dict(t=30,b=0), height=350)
    st.plotly_chart(fig1, use_container_width=True)

    # 4B.2 Mapa de calor sobre diagrama personalizado
    st.markdown("#### 🔴 Mapa de calor: Zona de remate 1–20")
    # Carga imagen
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(BASE_DIR, "static", "zonas_remate.png")
    img = Image.open(img_path)

    # Posiciones normalizadas de cada zona (x_norm, y_norm)
    positions = {
        "1":(.93,.15), "2":(.81,.15), "3":(.69,.15), "4":(.57,.15),
        "5":(.45,.15), "6":(.33,.15), "7":(.21,.15), "8":(.09,.15),
        "9":(.93,.45), "10":(.81,.45), "11":(.69,.45), "12":(.57,.45),
        "13":(.45,.45), "14":(.33,.45), "15":(.21,.45), "16":(.09,.45),
        "17a":(.93,.75),"17b":(.81,.75),"17c":(.69,.75),
        "18a":(.57,.75),"18b":(.45,.75),
        "19a":(.33,.75),"19b":(.21,.75),"19c":(.09,.75),
        "20":(.57,.95)
    }

    cnt = gol["zona_remate"].value_counts().to_dict()
    maxc = max(cnt.values()) if cnt else 1

    fig2 = go.Figure()
    fig2.add_layout_image(
        dict(source=img, xref="x", yref="y",
             x=0, y=1, sizex=1, sizey=1,
             sizing="stretch", layer="below")
    )
    show_axes = st.sidebar.checkbox("Mostrar ejes de zona_remate", value=False)
    for z, (x,y) in positions.items():
        c = cnt.get(z, 0)
        fig2.add_trace(go.Scatter(
            x=[x], y=[1-y],
            mode="markers+text",
            text=[f"{z}\n{c}" if c else ""],
            textfont=dict(size=10, color="black"),
            marker=dict(
                size=10 + (c/maxc)*20,
                color="red" if c else "rgba(0,0,0,0)",
                line=dict(width=1, color="black")
            ),
            hoverinfo="text",
            hovertext=f"Zona {z}: {c} goles"
        ))

    fig2.update_xaxes(visible=show_axes, range=[0,1])
    fig2.update_yaxes(visible=show_axes, range=[0,1])
    fig2.update_layout(
        margin=dict(t=30,b=0),
        height=400,
        title="Mapa de calor: Zona de remate"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 4C: Pases – TASA DE EFECTIVIDAD
# ────────────────────────────────────────────────────────────────────
pas = df_f[df_f["evento"] == "Pase"]
if not pas.empty:
    st.markdown("### 🟢 Segmento C – Pases")

    # Calcula tasa de éxito por tipo
    grp = pas.groupby("tipo_pase")["pase_exitoso"]
    tasa = (grp.apply(lambda s: (s=="Sí").sum() / s.count())
            .reset_index(name="tasa_exito"))

    fig3 = px.bar(
        tasa, x="tipo_pase", y="tasa_exito",
        text=tasa["tasa_exito"].apply(lambda v: f"{v*100:.1f}%"),
        title="Tasa de efectividad por tipo de pase",
        labels={"tasa_exito":"Tasa de éxito"}
    )
    fig3.update_layout(margin=dict(t=30,b=0), height=350, yaxis_tickformat=".0%")
    fig3.update_traces(marker_color="green")
    st.plotly_chart(fig3, use_container_width=True)

# ────────────────────────────────────────────────────────────────────
# 5. TABLA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=300)
csv = df_f.to_csv(index=False).encode("utf-8")
st.download_button(
    "💾 Descargar CSV filtrado",
    data=csv,
    file_name="filtrado.csv",
    mime="text/csv"
)
