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
grid_selector("🧍 Portero", ["Portero 1","Portero 2","Portero 3"], key="portero", cols=3)
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
    grid_selector("📈 Resultado de la parada",
                  ["Despeje","Bloqueo","De vuelta al contrario",
                   "Envío fuera","Gran parada"], key="rp", cols=2)
    grid_selector("✋ Parte del cuerpo",
                  ["Con las manos","Con las piernas","Otras partes"],
                  key="pc", cols=3)
    grid_selector("🧩 Origen",
                  ["Jugada","Segunda jugada","Penal","Falta","Córner"],
                  key="og", cols=3)
    st.markdown("</div>", unsafe_allow_html=True)

elif evento == "Gol Recibido":
    st.markdown('<div class="card bg-gol">', unsafe_allow_html=True)
    st.subheader("Detalle Gol Recibido")
    grid_selector("📍 Zona Gol", list(range(1, 10)), key="zg", cols=3)

    zona_remate = (
        [str(i) for i in range(1, 17)] +
        [f"17{l}" for l in "abc"] +
        [f"18{l}" for l in "ab"] +  # 18c eliminado
        [f"19{l}" for l in "abc"] +
        ["20"]
    )
    grid_selector("🎯 Zona Remate", zona_remate, key="zr", cols=5, small=True)

    grid_selector("⚽ Tipo de Gol",
                  ["Jugada","Segunda jugada","Penal","Falta","Córner"],
                  key="tg", cols=3)
    grid_selector("⏱️ Intervalo",
                  ["0–15","16–30","31–45","46–60","61–75","76–90"],
                  key="iv", cols=3)
    grid_selector("🧩 Origen del Error",
                  ["Propio","Defensor","Buena jugada rival","Rebote"],
                  key="oe", cols=2)
    grid_selector("🔍 Intervención",
                  ["Reacción","Anticipación","Mano a Mano","Tiro Lejano",
                   "Cabezazo","Juego aéreo","Ninguna"],
                  key="ig", cols=3)
    st.markdown("</div>", unsafe_allow_html=True)

else:  # Pase
    st.markdown('<div class="card bg-pase">', unsafe_allow_html=True)
    st.subheader("Detalle Pase")
    grid_selector("🛠️ Tipo de Pase",
                  ["Corto","Medio","Largo","Despeje"], key="tp", cols=2)
    grid_selector("✅ Pase Exitoso", ["Sí","No"], key="pe", cols=2)
    st.markdown("</div>", unsafe_allow_html=True)

# ── BOTONES DE ACCIÓN / CSV / BORRADO ──────────────────────────
col_reg, col_dl, col_del = st.columns(3)

with col_reg:
    if st.button("➡️ Registrar evento", type="primary"):
        if evento == "Atajada":
            st.session_state.registros.append({
                "fecha":   st.session_state.fecha,
                "portero": st.session_state.portero,
                "evento":  evento,
                "tipo_intervencion": st.session_state.ti,
                "resultado_parada":  st.session_state.rp,
                "parte_cuerpo":      st.session_state.pc,
                "origen":            st.session_state.og,
            })
        elif evento == "Gol Recibido":
            st.session_state.registros.append({
                "fecha":   st.session_state.fecha,
                "portero": st.session_state.portero,
                "evento":  evento,
                "zona_gol":      st.session_state.zg,
                "zona_remate":   st.session_state.zr,
                "tipo_gol":      st.session_state.tg,
                "intervalo":     st.session_state.iv,
                "origen_error":  st.session_state.oe,
                "intervencion":  st.session_state.ig,
            })
        else:
            st.session_state.registros.append({
                "fecha":   st.session_state.fecha,
                "portero": st.session_state.portero,
                "evento":  evento,
                "tipo_pase":    st.session_state.tp,
                "pase_exitoso": st.session_state.pe,
            })
        st.success("Evento registrado ✅")

with col_dl:
    if st.session_state.registros:
        buf = StringIO()
        pd.DataFrame(st.session_state.registros).to_csv(buf, index=False)
        st.download_button("💾 CSV", buf.getvalue(),
                           "registro_porteros.csv", mime="text/csv",
                           type="secondary")

with col_del:
    borrar = st.checkbox("Confirmar borrado")
    if st.button("🗑️ Borrar todo", disabled=not borrar, type="secondary"):
        st.session_state.registros.clear()
        st.success("Registros eliminados 🗑️")

st.markdown("---")

# ── TABLA DE REGISTROS ────────────────────────────────────────
if st.session_state.registros:
    st.subheader("Registros")
    st.dataframe(pd.DataFrame(st.session_state.registros),
                 use_container_width=True, hide_index=True, height=350)
else:
    st.info("Sin registros por ahora.")
