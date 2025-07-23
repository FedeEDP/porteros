import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import StringIO
from datetime import date

# ── CONFIGURACIÓN DE PÁGINA ────────────────────────────────
st.set_page_config("Dashboard Porteros – PD1", layout="wide")
st.title("🧤 Dashboard Rendimiento Porteros (Primera División)")
st.markdown("---")

# ── CARGA DE DAT
