import streamlit as st
import numpy as np
import json
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import os

# Internal engine imports
from radial_engine.config import (
    N_CORE, N_SURFACE, BASELINE_CORE, BASELINE_SURFACE, PROPAGATION_DAMPING
)
from radial_engine.simulation import run_simulation

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Valence-Pi Simulator", layout="wide")

# ==========================================
# DATA LOADING (Corrected Path)
# ==========================================
# We check multiple possible locations to ensure the app finds your JSON
JSON_PATHS = ["radial_engine/stateGuides.json", "stateGuides.json"]
state_guides_data = []

for path in JSON_PATHS:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                state_guides_data = json.load(f)["stateGuides"]
                break # Stop once we find it
        except Exception as e:
            st.sidebar.warning(f"Error reading {path}: {e}")

if not state_guides_data:
    st.sidebar.error("Could not locate stateGuides.json. Please check your GitHub folder structure.")

def get_state_guide(state_number):
    for guide in state_guides_data:
        if guide["state"] == state_number:
            return guide
    return None

# ==========================================
# SIDEBAR & INPUTS
# ==========================================
st.sidebar.title("System Dynamics")
age_cat = st.sidebar.selectbox("Subject Life Stage", options=["Childhood", "Adolescence", "Adulthood", "Early Ageing", "Late Ageing"], index=2)
steps_input = st.sidebar.number_input("Simulation Steps", 1, 100, 10)

st.sidebar.subheader("Simulation Intent")
user_intent = st.sidebar.text_area("Describe your goal:", placeholder="e.g. Improve influence without sole reliance on knowledge...", height=100)

# Sidebar Sliders with Semantic Labels
st.sidebar.subheader("Adjust States")
for i in range(N_CORE):
    guide = get_state_guide(i + 1)
    label = f"C{i+1}: {guide['polarity'] if guide else 'Core'}"
    st.sidebar.slider(label, -1.0, 1.0, step=0.01, key=f"core_{i}", value=0.70)

for i in range(N_SURFACE):
    guide = get_state_guide(i + N_CORE + 1)
    label = f"S{i+N_CORE+1}: {guide['polarity'] if guide else 'Surface'}"
    st.sidebar.slider(label, -1.0, 1.0, step=0.01, key=f"surface_{i}", value=0.65)

run_sim = st.sidebar.button("Run Realignment Simulation")

# ==========================================
# MAIN INTERFACE
# ==========================================
st.title("Valence-Pi Structural Simulator")
st.caption(f"Status: {len(state_guides_data)} semantic states active.")

if run_sim:
    # 1. Prepare Data
    t_core = np.array([st.session_state[f"core_{i}"] for i in range(N_CORE)])
    t_surface = np.array([st.session_state[f"surface_{i}"] for i in range(N_SURFACE)])

    # 2. Run Engine
    history_core, history_surface = run_simulation(
        initial_core=BASELINE_CORE, 
        initial_surface=BASELINE_SURFACE,
        target_core=t_core, 
        target_surface=t_surface,
        steps=int(steps_input), 
        damping=0.886
    )
    
    # 3. Process Results
    final_all = np.concatenate([history_core[-1], history_surface[-1]])
    initial_all = np.concatenate([BASELINE_CORE, BASELINE_SURFACE])
    deltas = final_all - initial_all
    labels = [f"C{i+1}" for i in range(N_CORE)] + [f"S{i+8}" for i in range(N_SURFACE)]

    # 4. HUMAN-CENTRIC INSPECTOR
    st.header("Human-Centric Interpretation")
    # Identify Top 3 absolute Deltas
    impact_indices = np.argsort(np.abs(deltas))[-3:][::-1]
    
    cols = st.columns(3)
    for i, idx in enumerate(impact_indices):
        guide = get_state_guide(idx + 1)
        with cols[i]:
            st.metric(label=labels[idx], value=f"{final_all[idx]:.2f}", delta=f"{deltas[idx]:.3f}")
            if guide:
                st.write(f"**Mood:** {guide.get('mood_description', 'N/A')}")
                st.write(f"**Keywords:** {', '.join(guide.get('keywords', []))}")
                st.info(f"**Physical Function:** {guide.get('physical_function', 'N/A')}")
                st.caption(f"**Manifestation:** {guide.get('manifestation', 'N/A')}")

    # 5. GRAPH
    st.subheader("Field Trajectory")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(np.concatenate([history_core, history_surface], axis=1))
    st.pyplot(fig)

    # 6. PDF EXPORT
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "Valence-Pi Structural Alignment Report", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 5, f"Intent: {user_intent}")
    
    for idx in impact_indices:
        guide = get_state_guide(idx + 1)
        if guide:
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 11)
            pdf.cell(0, 8, f"Shift in {labels[idx]} ({guide['polarity']})", ln=True)
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 5, f"Keywords: {', '.join(guide['keywords'])}")
            pdf.multi_cell(0, 5, f"Function: {guide['physical_function']}")
            pdf.multi_cell(0, 5, f"Effect: {guide['instantiation_effect']}")

    pdf_bytes = pdf.output()
    st.download_button("📥 Download Actionable Guidance Report", data=bytes(pdf_bytes), file_name="ValencePi_Report.pdf")