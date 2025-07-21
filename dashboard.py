import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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
uploaded_file = st.file_uploader(
    "Sube aquí el CSV desde la app de captura",
    type="csv",
    help="Archivo exportado de tu app – registro_porteros.csv",
)

if not uploaded_file:
    st.info("Espera… sube el CSV para ver el dashboard")
    st.stop()

df = pd.read_csv(uploaded_file)
df['fecha'] = pd.to_datetime(df['fecha']).dt.date

# ────────────────────────────────────────────────────────────────────
# 2. FILTROS GLOBALES
# ────────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")

# Porteros (multi‑selección)
porteros = sorted(df['portero'].unique())
portero_sel = st.sidebar.multiselect(
    "Portero(s)", porteros, default=porteros
)

# Rango de fechas
min_f, max_f = df['fecha'].min(), df['fecha'].max()
fecha_sel = st.sidebar.date_input(
    "Rango de fechas",
    value=(min_f, max_f),
    min_value=min_f,
    max_value=max_f
)

# Tipo de evento
eventos = sorted(df['evento'].unique())
evento_sel = st.sidebar.multiselect(
    "Evento(s)", eventos, default=eventos
)

# Aplicar filtros
df_f = df[
    df['portero'].isin(portero_sel) &
    df['evento'].isin(evento_sel) &
    (df['fecha'] >= fecha_sel[0]) &
    (df['fecha'] <= fecha_sel[1])
]

# ────────────────────────────────────────────────────────────────────
# 3. KPIs GENERALES
# ────────────────────────────────────────────────────────────────────
st.subheader("📌 Indicadores Clave")
col1, col2, col3, col4 = st.columns(4)

atajadas = df_f[df_f['evento']=="Atajada"].shape[0]
goles   = df_f[df_f['evento']=="Gol Recibido"].shape[0]
pases   = df_f[df_f['evento']=="Pase"].shape[0]
tiros   = atajadas + goles
efectividad = f"{(atajadas/tiros*100):.1f}%" if tiros>0 else "–"

col1.metric("🧤 Atajadas", atajadas)
col2.metric("🥅 Goles recibidos", goles)
col3.metric("🎯 Pases", pases)
col4.metric("✅ Efectividad de atajadas", efectividad)

st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 4. SEGMENTOS
# ────────────────────────────────────────────────────────────────────

## 4A: Atajadas
st.markdown("### 🧤 Segmento A – Atajadas")
ata_df = df_f[df_f['evento']=="Atajada"]

# 4A.1 Tipo de intervención
if 'tipo_intervencion' in ata_df:
    fig1, ax1 = plt.subplots(figsize=(4,3))
    sns.countplot(
        data=ata_df,
        x='tipo_intervencion',
        order=ata_df['tipo_intervencion'].value_counts().index,
        ax=ax1
    )
    ax1.set_xlabel("Tipo de intervención")
    ax1.set_ylabel("Cantidad")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig1)

# 4A.2 Resultado de la parada
if 'resultado_parada' in ata_df:
    fig2, ax2 = plt.subplots(figsize=(4,3))
    sns.countplot(
        data=ata_df,
        x='resultado_parada',
        order=ata_df['resultado_parada'].value_counts().index,
        ax=ax2
    )
    ax2.set_xlabel("Resultado de la parada")
    ax2.set_ylabel("Cantidad")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig2)

st.markdown("---")

## 4B: Goles recibidos
st.markdown("### ⚽ Segmento B – Goles recibidos")
gol_df = df_f[df_f['evento']=="Gol Recibido"]

### 4B.1 Heatmap 3×3 – Zona Gol 1‑9
if 'zona_gol' in gol_df:
    counts_gz = gol_df['zona_gol'].value_counts().to_dict()
    # Matriz 3x3 posicionando según la numeración de zonas
    matrix = [
        [counts_gz.get(3,0), counts_gz.get(6,0), counts_gz.get(9,0)],
        [counts_gz.get(2,0), counts_gz.get(5,0), counts_gz.get(8,0)],
        [counts_gz.get(1,0), counts_gz.get(4,0), counts_gz.get(7,0)],
    ]
    fig3, ax3 = plt.subplots(figsize=(4,4))
    sns.heatmap(
        matrix, annot=True, fmt="d", cmap="Reds", cbar=False,
        xticklabels=["Izq","Centro","Der"], yticklabels=["Aux","Med","Inf"],
        ax=ax3
    )
    ax3.set_title("Mapa de calor: Zona de gol")
    st.pyplot(fig3)

### 4B.2 Heatmap libre – Zona de remate 1‑20
st.markdown("#### 🔴 Mapa de calor: Zona de remate 1–20")
def plot_remate_heatmap(df_sub):
    counts = df_sub['zona_remate'].value_counts().to_dict()
    # Coordenadas normalizadas (x,y,w,h) para c/u (ajusta si necesitas)
    zone_coords = {
        '1':(0.85,0.66,0.15,0.33), '2':(0.85,0.33,0.15,0.33), '3':(0.85,0.00,0.15,0.33),
        '4':(0.70,0.66,0.15,0.33), '5':(0.70,0.33,0.15,0.33), '6':(0.70,0.00,0.15,0.33),
        '7':(0.55,0.66,0.15,0.33), '8':(0.55,0.33,0.15,0.33), '9':(0.55,0.00,0.15,0.33),
        '10':(0.40,0.00,0.15,0.33), '11':(0.40,0.66,0.15,0.33), '12':(0.40,0.33,0.15,0.33),
        '13':(0.25,0.33,0.15,0.33), '14':(0.25,0.00,0.15,0.33), '15':(0.25,0.66,0.15,0.33),
        '16':(0.10,0.66,0.15,0.33), '17a':(0.10,0.33,0.15,0.33), '17b':(0.10,0.20,0.15,0.13),
        '17c':(0.10,0.00,0.15,0.20),'18a':(0.00,0.66,0.15,0.33), '18b':(0.00,0.33,0.15,0.33),
        '19a':(0.00,0.20,0.15,0.13),'19b':(0.00,0.00,0.15,0.20),'19c':(0.00,0.00,0.15,0.20),
        '20':(0.10,0.00,0.15,0.33),
    }
    fig, ax = plt.subplots(figsize=(6,4))
    # Campo base
    ax.add_patch(patches.Rectangle((0,0),1,1,edgecolor='black', facecolor='none', lw=2))
    # Pintar zonas
    mx = max(counts.values()) if counts else 1
    for z, (x,y,w,h) in zone_coords.items():
        cnt = counts.get(z,0)
        color = plt.cm.Reds(cnt/mx)
        ax.add_patch(patches.Rectangle((x,y), w, h, facecolor=color, edgecolor='gray'))
        ax.text(x+w/2, y+h/2, f"{z}\n{cnt}", ha='center', va='center', fontsize=8)
    ax.axis('off')
    return fig

fig4 = plot_remate_heatmap(gol_df)
st.pyplot(fig4)

st.markdown("---")

## 4C: Pases
st.markdown("### 🟢 Segmento C – Pases")
pas_df = df_f[df_f['evento']=="Pase"]

# 4C.1 Precisión por tipo de pase
if 'tipo_pase' in pas_df:
    fig5, ax5 = plt.subplots(figsize=(4,3))
    sns.countplot(
        data=pas_df, x='tipo_pase',
        hue='pase_exitoso',
        order=pas_df['tipo_pase'].value_counts().index,
        ax=ax5
    )
    ax5.set_xlabel("Tipo de pase"); ax5.set_ylabel("Cantidad")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig5)

# ────────────────────────────────────────────────────────────────────
# 5. TABLA DETALLADA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Tabla de eventos filtrados")
st.dataframe(df_f, use_container_width=True)

# Botón CSV
csv_buf = df_f.to_csv(index=False).encode('utf-8')
st.download_button(
    "💾 Descargar CSV filtrado",
    data=csv_buf,
    file_name="registro_filtrado.csv",
    mime="text/csv"
)
