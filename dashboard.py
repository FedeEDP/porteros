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
st.set_page_config("Dashboard Porteros – PD1", layout="wide")
st.title("📊 Dashboard Rendimiento Porteros - Federico Miele EDP")
st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 2. CARGA DE DATOS
# ────────────────────────────────────────────────────────────────────
csv = st.file_uploader("Sube CSV (registro_porteros.csv)", type="csv")
if not csv:
    st.info("Carga el CSV para continuar.")
    st.stop()

df = pd.read_csv(csv, parse_dates=["fecha"])
df["fecha"] = df["fecha"].dt.date

# ────────────────────────────────────────────────────────────────────
# 3. FILTROS GLOBALES
# ────────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")
porteros = sorted(df["portero"].unique())
sel_p    = st.sidebar.multiselect("Portero(s)", porteros, default=porteros)

min_d, max_d = df["fecha"].min(), df["fecha"].max()
sel_d        = st.sidebar.date_input("Rango fechas",
                                     [min_d, max_d],
                                     min_value=min_d,
                                     max_value=max_d)

eventos = sorted(df["evento"].unique())
sel_e   = st.sidebar.multiselect("Evento(s)", eventos, default=eventos)

df_f = df[
    df["portero"].isin(sel_p) &
    df["evento"].isin(sel_e) &
    (df["fecha"] >= sel_d[0]) &
    (df["fecha"] <= sel_d[1])
]

# ────────────────────────────────────────────────────────────────────
# 4. KPIs & Tendencia Eficacia Atajadas
# ────────────────────────────────────────────────────────────────────
a   = df_f[df_f["evento"]=="Atajada"].shape[0]
g   = df_f[df_f["evento"]=="Gol Recibido"].shape[0]
p   = df_f[df_f["evento"]=="Pase"]
tot = len(p)
ok  = (p["pase_exitoso"]=="Sí").sum()
efp = f"{ok*100/tot:.1f}%" if tot else "—"
efa = f"{a*100/(a+g):.1f}%" if (a+g) else "—"

st.subheader("Indicadores Clave")
k1, k2, k3, k4 = st.columns(4, gap="small")
k1.metric("🧤 Atajadas", a)
k2.metric("🥅 Goles Rec.", g)
k3.metric("🎯 Eficiencia Pases", efp)
k4.metric("✅ Eficacia Atajadas", efa)
st.markdown("---")

# Tendencia diaria de eficacia atajadas
df_trend = (
    df_f[df_f["evento"].isin(["Atajada","Gol Recibido"])]
      .groupby(["fecha","evento"])
      .size()
      .unstack(fill_value=0)
)
if "Atajada" in df_trend and "Gol Recibido" in df_trend:
    df_trend["Eficacia"] = (
        df_trend["Atajada"] /
        (df_trend["Atajada"] + df_trend["Gol Recibido"])
    )
    st.line_chart(df_trend["Eficacia"], height=150)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5A. SEGMENTO A – Atajadas (Radar compacto)
# ────────────────────────────────────────────────────────────────────
ata = df_f[df_f["evento"]=="Atajada"]
if not ata.empty:
    st.markdown("### 🧤 Segmento A – Atajadas (Radar)")
    tipi = ata["tipo_intervencion"].unique().tolist()
    resu = ata["resultado_parada"].unique().tolist()
    cats = tipi + resu

    cnt_i = [ata["tipo_intervencion"].eq(c).sum() for c in cats]
    cnt_r = [ata["resultado_parada"].eq(c).sum()  for c in cats]

    angles = np.linspace(0,2*np.pi,len(cats),endpoint=False).tolist()
    angles += angles[:1]
    cnt_i += cnt_i[:1]; cnt_r += cnt_r[:1]

    fig, ax = plt.subplots(figsize=(2.5,2.5), subplot_kw=dict(polar=True))
    ax.plot(angles, cnt_i, marker="o", color="#3399ff", linewidth=1)
    ax.fill(angles, cnt_i, alpha=0.2, color="#3399ff")
    ax.plot(angles, cnt_r, marker="o", color="#ff3333", linewidth=1)
    ax.fill(angles, cnt_r, alpha=0.2, color="#ff3333")
    ax.set_thetagrids(np.degrees(angles[:-1]), cats, fontsize=6)
    ax.tick_params(colors="#444444")
    ax.grid(color="#cccccc", linestyle="--", linewidth=0.5)
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5B. SEGMENTO B – Goles Recibidos & Zona Remate
# ────────────────────────────────────────────────────────────────────
gol = df_f[df_f["evento"]=="Gol Recibido"]
if not gol.empty:
    st.markdown("### ⚽ Segmento B – Goles Recibidos")

    # Zona 1–9 mini
    cnt9 = gol["zona_gol"].value_counts().reindex(range(1,10), fill_value=0)
    mat9 = cnt9.values.reshape(3,3)[::-1]
    fig, ax = plt.subplots(figsize=(2,2))
    ax.imshow(mat9, cmap="Reds", aspect="equal")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, mat9[i,j], ha="center", va="center", fontsize=7)
    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)

    # Zona remate 1–20 compacto
    st.markdown("#### 🔴 Mapa Calor: Zona Remate 1–20")
    xs = [0.875,0.625,0.375,0.125]
    ys = [0.90,0.70,0.50,0.30,0.10]
    zone_map = {
        **{str(i):(xs[0], ys[i-1]) for i in range(1,6)},
        **{str(i):(xs[1], ys[i-6]) for i in range(6,11)},
        **{str(i):(xs[2], ys[i-11]) for i in range(11,16)},
        "16":(xs[3],ys[0]), "17":(xs[3],ys[1]),
        "18":(xs[3],ys[2]), "19":(xs[3],ys[3]), "20":(xs[3],ys[4])
    }
    cnt20 = gol["zona_remate"].value_counts().to_dict()
    mx20  = max(cnt20.values()) if cnt20 else 1

    fig, ax = plt.subplots(figsize=(5,1.8))
    ax.add_patch(patches.Rectangle((0,0),1,1,facecolor="#fafafa",edgecolor="none"))
    w,h = 0.23,0.16

    for z,(cx,cy) in zone_map.items():
        x0,y0 = cx-w/2, cy-h/2
        # subdivisiones
        if   z in ("17","19"): n=3
        elif z=="18":          n=2
        else:                  n=1
        subs = np.linspace(x0, x0+w, n+1)[:-1]
        total = cnt20.get(z,0)
        for i, sx in enumerate(subs):
            color = "#d32f2f" if total>0 else "#fafafa"
            ax.add_patch(patches.Rectangle(
                (sx,y0), w/n, h,
                facecolor=color, edgecolor="#bbbbbb", lw=0.6
            ))
            # lettering de derecha→izq
            if z=="18":
                letters = ['b','a']
            else:
                letters = ['c','b','a'][:n]
            label = z if n==1 else f"{z}{letters[i]}"
            ax.text(sx+0.005, y0+h*0.55, label,
                    fontsize=7, ha="left", va="center")
            ax.text(sx+0.005, y0+h*0.30, str(total),
                    fontsize=7, ha="left", va="center")

    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("---")

# ────────────────────────────────────────────────────────────────────
# 5C. SEGMENTO C – Pases (barra horizontal muy pequeña)
# ────────────────────────────────────────────────────────────────────
pas = df_f[df_f["evento"]=="Pase"]
if not pas.empty:
    st.markdown("### 🟢 Segmento C – Pases")
    tasas = (
        pas.groupby("tipo_pase")["pase_exitoso"]
           .apply(lambda s: (s=="Sí").sum()/len(s))
           .sort_index()
    )
    fig, ax = plt.subplots(figsize=(2,0.8))
    ax.barh(tasas.index, tasas.values, color="#00bfa5", height=0.3)
    for i,v in enumerate(tasas.values):
        ax.text(v+0.005, i, f"{v*100:.0f}%",
                va="center", fontsize=6)
    ax.set_xlim(0,1)
    ax.tick_params(labelsize=6)
    plt.tight_layout()
    st.pyplot(fig)

# ────────────────────────────────────────────────────────────────────
# 6. TABLA DETALLADA Y DESCARGA
# ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Eventos filtrados")
st.dataframe(df_f, use_container_width=True, height=200)
buf = StringIO(); df_f.to_csv(buf, index=False)
st.download_button("📥 Descargar CSV", buf.getvalue(), "filtrado.csv", "text/csv")
