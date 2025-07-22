import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from datetime import date

# ────────────────────────────────────────────────────────────────────
# 1. CONFIGURACIÓN DE PÁGINA
# ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard Porteros", layout="wide")
st.title("📊 Dashboard de Rendimiento de Porteros")

# ────────────────────────────────────────────────────────────────────
# 2. CARGA DE DATOS
# ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Sube tu CSV (registro_porteros.csv)", type="csv")
if not uploaded:
    st.info("Sube el CSV exportado desde la app para ver el dashboard.")
    st.stop()

df = pd.read_csv(uploaded, parse_dates=["fecha"])
df["fecha"] = df["fecha"].dt.date

# ────────────────────────────────────────────────────────────────────
# 3. FILTROS GLOBALES
# ────────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")
# Porteros
porteros = sorted(df["portero"].unique())
sel_p = st.sidebar.multiselect("Portero(s)", porteros, default=porteros)
# Fechas
min_f, max_f = df["fecha"].min(), df["fecha"].max()
sel_fecha = st.sidebar.date_input(
    "Rango de fechas", [min_f, max_f], min_value=min_f, max_value=max_f
)
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
# 4. KPIs PRINCIPALES
# ────────────────────────────────────────────────────────────────────
atajadas = df_f[df_f["evento"]=="Atajada"].shape[0]
goles   = df_f[df_f["evento"]=="Gol Recibido"].shape[0]
pases_tot = df_f[df_f["evento"]=="Pase"].shape[0]
pases_ok  = df_f[
    (df_f["evento"]=="Pase") & (df_f["pase_exitoso"]=="Sí")
].shape[0]
# Eficacia de pases
pass_rate = f"{(pases_ok*100/pases_tot):.1f}%" if pases_tot else "—"
# Eficacia de atajadas
tiros = atajadas + goles
save_rate = f"{(atajadas*100/tiros):.1f}%" if tiros else "—"

st.subheader("📌 Indicadores Clave")
c1, c2, c3, c4 = st.columns(4, gap="small")
c1.metric("🧤 Atajadas", atajadas)
c2.metric("🥅 Goles recibidos", goles)
c3.metric("🎯 Eficiencia pases", pass_rate)
c4.metric("✅ Eficacia atajadas", save_rate)
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5A. SEGMENTO A – Atajadas
# ────────────────────────────────────────────────────────────────────
ata = df_f[df_f["evento"]=="Atajada"]
if not ata.empty:
    st.markdown("### 🧤 Segmento A – Atajadas")
    a1, a2 = st.columns(2, gap="small")
    with a1:
        fig = px.histogram(
            ata, x="tipo_intervencion", text_auto=True,
            title="Tipo de intervención"
        )
        fig.update_layout(margin=dict(t=30,b=0), height=300,
                          xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    with a2:
        fig = px.histogram(
            ata, x="resultado_parada", text_auto=True,
            title="Resultado de la parada"
        )
        fig.update_layout(margin=dict(t=30,b=0), height=300,
                          xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5B. SEGMENTO B – Goles recibidos
# ────────────────────────────────────────────────────────────────────
gol = df_f[df_f["evento"]=="Gol Recibido"]
if not gol.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")

    # 5B.1 Heatmap 3×3: Zona de gol (1–9)
    cnt_gz = gol["zona_gol"].value_counts().reindex(range(1,10), fill_value=0)
    matrix = cnt_gz.values.reshape(3,3)[::-1]
    fig1 = px.imshow(
        matrix, color_continuous_scale="Reds", text_auto=True,
        labels=dict(x="Columna", y="Fila", color="Goles"),
        x=["1","2","3"], y=["7‑9","4‑6","1‑3"]
    )
    fig1.update_layout(margin=dict(t=30,b=0), height=350)
    st.plotly_chart(fig1, use_container_width=True)

    # 5B.2 Heatmap sobre diagrama – Zona de remate 1–20
    st.markdown("#### 🔴 Mapa de calor: Zona de remate")
    # Carga imagen
    base = os.path.dirname(os.path.abspath(__file__))
    img = Image.open(os.path.join(base, "static/zonas_remate.png"))

    # Posiciones preajustadas (x_norm, y_norm)
    pos = {
        "1":(.92,.90), "2":(.77,.90), "3":(.62,.90), "4":(.47,.90), "5":(.32,.90),
        "6":(.17,.90), "7":(.17,.65), "8":(.32,.65), "9":(.47,.65), "10":(.62,.65),
        "11":(.77,.65), "12":(.92,.65), "13":(.92,.40), "14":(.77,.40), "15":(.62,.40),
        "16":(.47,.40), "17a":(.32,.40),"17b":(.17,.40),"17c":(.02,.40),
        "18a":(.02,.15),"18b":(.17,.15),"19a":(.32,.15),"19b":(.47,.15),
        "19c":(.62,.15),"20":(.77,.15)
    }

    cnt = gol["zona_remate"].value_counts().to_dict()
    maxc = max(cnt.values()) if cnt else 1

    fig2 = go.Figure()
    fig2.add_layout_image(
        dict(source=img, xref="x", yref="y",
             x=0, y=1, sizex=1, sizey=1,
             sizing="stretch", layer="below")
    )
    for z,(x,y) in pos.items():
        c = cnt.get(z, 0)
        fig2.add_trace(go.Scatter(
            x=[x], y=[1-y],
            mode="markers+text",
            text=[f"{c}" if c else ""],
            textfont=dict(size=9,color="black"),
            marker=dict(
                size=8 + (c/maxc)*24,
                color="red" if c else "rgba(0,0,0,0)",
                line=dict(width=1,color="black")
            ),
            hoverinfo="text",
            hovertext=f"Zona {z}: {c} goles"
        ))
    fig2.update_xaxes(visible=False, range=[0,1])
    fig2.update_yaxes(visible=False, range=[0,1])
    fig2.update_layout(margin=dict(t=30,b=0), height=380)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5C. SEGMENTO C – Pases (tasa de éxito)
# ────────────────────────────────────────────────────────────────────
pas = df_f[df_f["evento"]=="Pase"]
if not pas.empty:
    st.markdown("### 🟢 Segmento C – Pases")
    grp = pas.groupby("tipo_pase")["pase_exitoso"]
    tasa = grp.apply(lambda s: (s=="Sí").sum()/s.count()).reset_index(name="tasa_exito")
    fig3 = px.bar(
        tasa, x="tipo_pase", y="tasa_exito",
        text=tasa["tasa_exito"].apply(lambda v: f"{v*100:.1f}%"),
        title="Tasa de éxito por tipo de pase",
        labels={"tasa_exito":"Eficacia"}
    )
    fig3.update_layout(margin=dict(t=30,b=0), height=330, yaxis_tickformat=".0%")
    fig3.update_traces(marker_color="green")
    st.plotly_chart(fig3, use_container_width=True)

# ────────────────────────────────────────────────────────────────────
# 6. TABLA DETALLADA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=300)
csv = df_f.to_csv(index=False).encode("utf-8")
st.download_button("💾 Descargar CSV", data=csv, file_name="filtrado.csv")
