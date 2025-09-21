import streamlit as st
import pandas as pd
from datetime import date
from io import StringIO
import math

# ── CONFIG PÁGINA ──────────────────────────────────────────────
st.set_page_config("Federico Miele - Análisis de rendimiento", layout="wide")
st.markdown("""
<style>
.stButton > button {height:50px;font-size:1.05rem;font-weight:600;width:100%;}
.small-btn > button {height:36px;font-size:.8rem;padding:0 4px;}
.card {background:#fafafa;border:1px solid #e0e0e0;border-radius:8px;
       padding:1rem;margin-bottom:1rem;box-shadow:0 2px 6px rgba(0,0,0,.05);}
.bg-atajada{border-left:6px solid #74b9ff;}
.bg-gol    {border-left:6px solid #ff7675;}
.bg-pase   {border-left:6px solid #55efc4;}
thead tr th, tbody tr td {font-size:.85rem;}
</style>
""", unsafe_allow_html=True)

# ── ESTADO ─────────────────────────────────────────────────────
st.session_state.setdefault("registros", [])
st.session_state.setdefault("zg", 1)
st.session_state.setdefault("evento", "Atajada")

# ── HELPER: selector en cuadrícula con 1 clic ──────────────────
def grid_selector(label, options, key, cols=3, small=False):
    st.markdown(f"**{label}**")
    rows = math.ceil(len(options) / cols)
    for r in range(rows):
        cols_obj = st.columns(cols)
        for c in range(cols):
            idx = r * cols + c
            if idx >= len(options):
                cols_obj[c].empty()
                continue
            opt = options[idx]
            is_selected = st.session_state.get(key) == opt
            btn_label = f"✅ {opt}" if is_selected else str(opt)

            with cols_obj[c]:
                if small:
                    st.markdown("""
                        <style>
                        div.stButton > button {
                            height: 36px;
                            font-size: .8rem;
                            padding: 0 6px;
                            margin-bottom: 5px;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                if st.button(btn_label, key=f"{key}_{opt}"):
                    st.session_state[key] = opt
    st.markdown("")

# ── ENCABEZADO Y CONTROLES PRINCIPALES ─────────────────────────
st.title("🧤 Federico Miele – Análisis de rendimiento de porteros")
st.date_input("📅 Fecha", value=st.session_state.get("fecha", date.today()), key="fecha")

# Cambiado: opciones de Portero -> José y Nico
grid_selector("🧍 Portero", ["José","Nico"], key="portero", cols=2)

grid_selector("🎯 Tipo de evento", ["Atajada","Gol Recibido","Pase"], key="evento", cols=3)
evento = st.session_state.evento
st.markdown("")

# ── PANEL DETALLE SEGÚN EVENTO ─────────────────────────────────
if evento == "Atajada":
    st.markdown('<div class="card bg-atajada">', unsafe_allow_html=True)
    st.subheader("Detalle Atajada")
    grid_selector("⚙️ Tipo de intervención",
                  ["Reacción","Anticipación","Mano a Mano","Tiro Lejano",
                   "Cabezazo","Juego aéreo"], key="ti", cols=2)

    # Cambiado: se eliminó "Gran parada"
    grid_selector("📈 Resultado de la parada",
                  ["Despeje","Bloqueo","De vuelta al contrario","Envío fuera"],
                  key="rp", cols=2)

    grid_selector("✋ Parte del cuerpo",
                  ["Con las manos","Con las piernas","Otras partes"],
                  key="pc", cols=3)

    # Cambiado: se agregan Centro lateral y Centro frontal
    grid_selector("🧩 Origen",
                  ["Jugada","Segunda jug
