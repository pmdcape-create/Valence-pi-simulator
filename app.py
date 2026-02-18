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

# ==========================================
# SIDEBAR & RESET LOGIC
# ==========================================
st.sidebar.title("Valence-Pi Controls")

# Initialize Session State for sliders if not present
if 'c_slider_vals' not in st.session_state:
    st.session_state.c_slider_vals = list(BASELINE_CORE)
if 's_slider_vals' not in st.session_state:
    st.session_state.s_slider_vals = list(BASELINE_SURFACE)

def reset_values():
    st.session_state.c_slider_vals = list(BASELINE_CORE)
    st.session_state.s_slider_vals = list(BASELINE_SURFACE)
    st.session_state.final_states = np.concatenate([BASELINE_CORE, BASELINE_SURFACE])

inspector_mode = st.sidebar.radio("Inspector Mode", ["Architect Report", "Systemic Debugger"])

with st.sidebar:
    if st.button("🔄 Reset to Societal Baseline"):
        reset_values()
        st.rerun()

    st.divider()
    st.subheader("Core Potentials (1-7)")
    c_vals = []
    for i in range(N_CORE):
        v = st.slider(f"State {i+1}", -1.0, 1.0, float(st.session_state.c_slider_vals[i]), 0.05, key=f"c_slide_{i}")
        c_vals.append(v)
    
    st.subheader("Surface Potentials (8-22)")
    s_vals = []
    for i in range(N_SURFACE):
        v = st.slider(f"State {i+8}", -1.0, 1.0, float(st.session_state.s_slider_vals[i]), 0.05, key=f"s_slide_{i}")
        s_vals.append(v)
    
    st.divider()
    num_steps = st.number_input("No. of Steps", min_value=10, max_value=1000, value=100)
    run_btn = st.button("🚀 Run Systemic Simulation")

# ==========================================
# SIMULATION
# ==========================================
if 'final_states' not in st.session_state:
    st.session_state.final_states = np.concatenate([BASELINE_CORE, BASELINE_SURFACE])

if run_btn:
    # Update saved slider values in session state
    st.session_state.c_slider_vals = c_vals
    st.session_state.s_slider_vals = s_vals
    
    with st.spinner("Calculating equilibrium..."):
        final, _ = run_simulation(
            initial_core=np.array(c_vals), 
            initial_surface=np.array(s_vals), 
            steps=num_steps
        )
        st.session_state.final_states = final

# ==========================================
# MAIN UI
# ==========================================
st.title("Valence-Pi Systemic Simulator")

if inspector_mode == "Architect Report":
    tab_rep, tab_vis = st.tabs(["📋 Narrative Report", "📊 Visual Analysis"])
    
    with tab_rep:
        # NEW: Personality Style Header (To be automated in next step)
        st.info("### Current System Style: **Balanced Architect**")
        st.markdown("*The system is currently operating within standard societal parameters.*")
        st.divider()
        
        for i, val in enumerate(st.session_state.final_states):
            guide = get_state_guide(i+1)
            if guide:
                with st.expander(f"STATE {i+1}: {guide.get('named_state_descriptor', 'N/A')}"):
                    col1, col2 = st.columns([1, 4])
                    col1.metric("Valence", f"{val:.3f}")
                    col2.write(engine.get_narrative(i+1, val))
    
    with tab_vis:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(range(1, 23), st.session_state.final_states, color=['#2E86C1' if x >= 0 else '#CB4335' for x in st.session_state.final_states])
        ax.set_ylim(-1.1, 1.1)
        st.pyplot(fig)

elif inspector_mode == "Systemic Debugger":
    st.header("Systemic Debugger")
    df = pd.DataFrame({
        "State ID": range(1, 23),
        "Descriptor": [get_state_guide(i+1).get('named_state_descriptor', 'N/A') for i in range(22)],
        "Final Valence": st.session_state.final_states
    })
    st.table(df)