import streamlit as st
import numpy as np
import json
import matplotlib.pyplot as plt
import pandas as pd
import os
from radial_engine.config import N_CORE, N_SURFACE, BASELINE_CORE, BASELINE_SURFACE, PROPAGATION_DAMPING
from radial_engine.simulation import run_simulation
from radial_engine.narrative_engine import NarrativeEngine

st.set_page_config(page_title="Valence-Pi Simulator", layout="wide")

# INITIALIZATION
JSON_PATH = "stateGuides.json" if os.path.exists("stateGuides.json") else "radial_engine/stateGuides.json"
try:
    engine = NarrativeEngine(JSON_PATH)
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        state_guides_data = json.load(f)["stateGuides"]
except Exception as e:
    st.error(f"Initialization Error: {e}")
    state_guides_data = []

def get_state_guide(n):
    return next((g for g in state_guides_data if g["state"] == n), None)

# SIDEBAR
st.sidebar.title("Valence-Pi Controls")
with st.sidebar:
    st.subheader("Core Potentials (1-7)")
    c_vals = [st.slider(f"State {i+1}", -1.0, 1.0, float(BASELINE_CORE[i]), 0.05, key=f"c{i}") for i in range(N_CORE)]
    
    st.subheader("Surface Potentials (8-22)")
    s_vals = [st.slider(f"State {i+8}", -1.0, 1.0, float(BASELINE_SURFACE[i]), 0.05, key=f"s{i}") for i in range(N_SURFACE)]
    
    damping = st.slider("Propagation Damping", 0.0, 1.0, PROPAGATION_DAMPING, 0.01)

# SIMULATION - Triggers on every slider move
final_states, _ = run_simulation(initial_core=np.array(c_vals), initial_surface=np.array(s_vals), damping=damping)

# UI DISPLAY
st.title("Valence-Pi Systemic Simulator")
tab1, tab2 = st.tabs(["📋 Narrative Report", "📊 Visual Analysis"])

with tab1:
    st.header("Architect Narrative Analysis")
    for i, val in enumerate(final_states):
        guide = get_state_guide(i+1)
        if guide:
            with st.expander(f"STATE {i+1}: {guide.get('named_state_descriptor', 'N/A')}"):
                col1, col2 = st.columns([1, 4])
                col1.metric("Valence", f"{val:.3f}")
                col2.write(engine.get_narrative(i+1, val))

with tab2:
    st.subheader("Systemic Equilibrium Plot")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(range(1, 23), final_states, color=['#2E86C1' if x >= 0 else '#CB4335' for x in final_states])
    ax.set_ylim(-1.1, 1.1)
    ax.set_ylabel("Equilibrium Valence")
    ax.set_xlabel("State ID")
    st.pyplot(fig)