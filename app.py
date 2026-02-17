import streamlit as st
import numpy as np
import json
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import tempfile
import os

from radial_engine.config import (
    N_CORE, N_SURFACE, BASELINE_CORE, BASELINE_SURFACE, PROPAGATION_DAMPING
)
from radial_engine.simulation import run_simulation

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Valence-Pi Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# RESEARCH-ALIGNED DEFAULT VALUES
# ==========================================
DEFAULT_CORE_VAL = 0.70
DEFAULT_SURFACE_AVG = 0.65

CUSTOM_DEFAULTS = {
    "core_0": 0.70, "core_1": 0.70, "core_2": 0.70, "core_3": 0.70, 
    "core_4": 0.70, "core_5": 0.70, "core_6": 0.70,
    "surface_4": 0.80,  # S12: Knowledge (Anchor)
    "surface_7": 0.40,  # S15: Strategy (Focus)
    "surface_10": 0.40, # S18: Influence (Focus)
}

# ==========================================
# LOAD STATE GUIDES
# ==========================================
try:
    with open("radial_engine/stateGuides.json", "r", encoding="utf-8") as f:
        state_guides_data = json.load(f)["stateGuides"]
except Exception:
    state_guides_data = []

def get_state_guide(state_number):
    for guide in state_guides_data:
        if guide["state"] == state_number:
            return guide
    return None

# ==========================================
# SESSION STATE INIT
# ==========================================
for i in range(N_CORE):
    key = f"core_{i}"
    if key not in st.session_state:
        st.session_state[key] = CUSTOM_DEFAULTS.get(key, DEFAULT_CORE_VAL)

for i in range(N_SURFACE):
    key = f"surface_{i}"
    if key not in st.session_state:
        st.session_state[key] = CUSTOM_DEFAULTS.get(key, DEFAULT_SURFACE_AVG)

# ==========================================
# TITLE
# ==========================================
st.title("Valence-Pi Simulator")
st.info(f"System loaded with Baseline Integrity ({DEFAULT_CORE_VAL}) and User Profile anchors.")

# ==========================================
# SIDEBAR SETTINGS
# ==========================================
st.sidebar.header("System Dynamics")

age_cat = st.sidebar.selectbox(
    "Subject Life Stage (Plasticity)",
    options=[
        "Childhood (Birth – Age 9)", 
        "Adolescence (Ages 9 – 32)", 
        "Adulthood (Ages 32 – 66)", 
        "Early Ageing (Ages 66 – 83)", 
        "Late Ageing (Age 83+)"
    ],
    index=2
)

plasticity_map = {
    "Childhood (Birth – Age 9)": 0.90, 
    "Adolescence (Ages 9 – 32)": 0.60,
    "Adulthood (Ages 32 – 66)": 0.30, 
    "Early Ageing (Ages 66 – 83)": 0.15,
    "Late Ageing (Age 83+)": 0.05
}

alpha = plasticity_map.get(age_cat, 0.30)
effective_damping = PROPAGATION_DAMPING + (1.0 - PROPAGATION_DAMPING) * (1.0 - alpha)

steps_input_val = st.sidebar.number_input("Simulation Steps", min_value=1, max_value=200, value=10)

st.sidebar.markdown("---")
st.sidebar.header("Simulation Mode")
use_target = st.sidebar.radio("Mode", options=["Incremental adjustment", "Target states (user-defined)"], index=1)

# Sliders
st.sidebar.header("Core States (Backbone)")
for i in range(N_CORE):
    state_num = i + 1
    guide = get_state_guide(state_num)
    label = f"C{state_num} — {guide['polarity']}" if guide else f"Core {state_num}"
    st.sidebar.slider(label, -1.0, 1.0, step=0.01, key=f"core_{i}")

st.sidebar.header("Surface States (Circumference)")
for i in range(N_SURFACE):
    state_num = N_CORE + i + 1
    guide = get_state_guide(state_num)
    label = f"S{state_num} — {guide['polarity']}" if guide else f"Surface {state_num}"
    st.sidebar.slider(label, -1.0, 1.0, step=0.01, key=f"surface_{i}")

# --- ADDED INTENT TEXT AREA FOR STRESS TESTING ---
st.sidebar.markdown("---")
st.sidebar.subheader("Simulation Intent")
user_intent = st.sidebar.text_area(
    "Describe your goal or the situation you are testing:",
    placeholder="e.g., I want to test how C7 handles a radical shift in influence strategies...",
    height=150
)

run_sim = st.sidebar.button("Run Simulation")

# ==========================================
# SIMULATION EXECUTION & RESULTS
# ==========================================
if run_sim:
    # (Rest of the code remains the same as your original provided app.py)
    # ...