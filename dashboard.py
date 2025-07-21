import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config("Dashboard Porteros", layout="wide")

st.title("📊 Dashboard de Rendimiento de Porteros")

# ── Subir archivo o leer por defecto ────────────────────────────
uploaded_file = st.file_uploader("Sube el archivo CSV exportado desde la app", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['fecha'] = pd.to_datetime(df['fecha'])

    # ── Filtros ───────────────────────────────────────────────
    st.sidebar.header("Filtros")
    porteros = df['portero'].unique().tolist()
    portero_sel = st.sidebar.multiselect("Portero", porteros, default=porteros)

    fechas = pd.to_datetime(df['fecha']).dt.date
    min_f, max_f = fechas.min(), fechas.max()
    fecha_sel = st.sidebar.date_input("Rango de Fechas", [min_f, max_f])

    evento_sel = st.sidebar.multiselect("Tipo de evento", df['evento'].unique(), default=df['evento'].unique())

    df_f = df[
        (df['portero'].isin(portero_sel)) &
        (df['evento'].isin(evento_sel)) &
        (df['fecha'].dt.date >= fecha_sel[0]) &
        (df['fecha'].dt.date <= fecha_sel[1])
    ]

    # ── KPIs ───────────────────────────────────────────────
    st.subheader("📌 Indicadores Clave")
    col1, col2, col3 = st.columns(3)
    col1.metric("🧤 Atajadas", df_f[df_f["evento"] == "Atajada"].shape[0])
    col2.metric("🥅 Goles Recibidos", df_f[df_f["evento"] == "Gol Recibido"].shape[0])
    col3.metric("🎯 Pases", df_f[df_f["evento"] == "Pase"].shape[0])

    # ── Visualización: Tipo de Intervención (si hay atajadas) ─────────────
    if "tipo_intervencion" in df_f.columns:
        st.subheader("Distribución de Tipo de Intervención")
        fig, ax = plt.subplots()
        sns.countplot(data=df_f[df_f["evento"] == "Atajada"], x="tipo_intervencion", ax=ax)
        ax.set_ylabel("Cantidad")
        ax.set_xlabel("Tipo de Intervención")
        st.pyplot(fig)

    # ── Visualización: Zona Gol (mapa de calor básico) ─────────────
    if "zona_gol" in df_f.columns:
        st.subheader("📍 Zona de Gol")
        zg_data = df_f[df_f["evento"] == "Gol Recibido"]['zona_gol'].value_counts().sort_index()
        fig, ax = plt.subplots()
        zg_data.plot(kind='bar', ax=ax, color="#ff7675")
        ax.set_xlabel("Zona")
        ax.set_ylabel("Goles Recibidos")
        st.pyplot(fig)

    # ── Visualización: Línea de tiempo de eventos ─────────────
    st.subheader("📅 Eventos por fecha")
    df_date = df_f.groupby(['fecha', 'evento']).size().unstack().fillna(0)
    st.line_chart(df_date)

    # ── Tabla ───────────────────────────────────────────────
    st.subheader("📄 Tabla de Eventos")
    st.dataframe(df_f, use_container_width=True)

else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
