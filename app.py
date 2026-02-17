import streamlit as st
import numpy as np
import json
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import tempfile
import os

# Internal engine imports - assuming these remain in your local repository
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
# DATA LOADING (stateGuides.json)
# ==========================================
try:
    with open("stateGuides.json", "r", encoding="utf-8") as f:
        state_guides_data = json.load(f)["stateGuides"]
except Exception as e:
    st.error(f"Error loading stateGuides.json: {e}")
    state_guides_data = []

def get_state_guide(state_number):
    """Retrieves the human-centric guide for a specific state index."""
    for guide in state_guides_data:
        if guide["state"] == state_number:
            return guide
    return None

# ==========================================
# SESSION STATE & DEFAULTS
# ==========================================
# Research-aligned anchors from your profile
CUSTOM_DEFAULTS = {
    "surface_4": 0.80,  # S12: Knowledge (Anchor)
    "surface_7": 0.40,  # S15: Strategy (Focus)
    "surface_10": 0.40, # S18: Influence (Focus)
}

for i in range(N_CORE):
    key = f"core_{i}"
    if key not in st.session_state:
        st.session_state[key] = 0.70  # Baseline Integrity

for i in range(N_SURFACE):
    key = f"surface_{i}"
    if key not in st.session_state:
        st.session_state[key] = CUSTOM_DEFAULTS.get(key, 0.65)

# ==========================================
# HEADER & SIDEBAR UI
# ==========================================
st.title("Valence-Pi Structural Simulator")
st.markdown("---")

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

# Map age to damping physics
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
st.sidebar.subheader("Simulation Intent")
user_intent = st.sidebar.text_area(
    "Describe the situation or goal you are testing:",
    placeholder="e.g., Increasing influence (S18) without relying on validated knowledge (S12)...",
    height=150
)

st.sidebar.markdown("---")
st.sidebar.header("Input States")
for i in range(N_CORE):
    guide = get_state_guide(i + 1)
    label = f"C{i+1}: {guide['polarity'] if guide else 'Core'}"
    st.sidebar.slider(label, -1.0, 1.0, step=0.01, key=f"core_{i}")

for i in range(N_SURFACE):
    guide = get_state_guide(N_CORE + i + 1)
    label = f"S{N_CORE + i + 1}: {guide['polarity'] if guide else 'Surface'}"
    st.sidebar.slider(label, -1.0, 1.0, step=0.01, key=f"surface_{i}")

run_sim = st.sidebar.button("Run Realignment Simulation")

# ==========================================
# EXECUTION & RESULTS
# ==========================================
if run_sim:
    # 1. Capture User Inputs
    t_core = np.array([st.session_state[f"core_{i}"] for i in range(N_CORE)])
    t_surface = np.array([st.session_state[f"surface_{i}"] for i in range(N_SURFACE)])

    # 2. Run Engine
    history_core, history_surface = run_simulation(
        initial_core=BASELINE_CORE, 
        initial_surface=BASELINE_SURFACE,
        target_core=t_core, 
        target_surface=t_surface,
        steps=int(steps_input_val), 
        damping=effective_damping
    )

    # 3. Calculate Deltas
    final_core, final_surface = history_core[-1, :], history_surface[-1, :]
    all_final = np.concatenate([final_core, final_surface])
    all_initial = np.concatenate([BASELINE_CORE, BASELINE_SURFACE])
    deltas = all_final - all_initial
    labels = [f"C{i+1}" for i in range(N_CORE)] + [f"S{i+8}" for i in range(N_SURFACE)]

    # 4. HUMAN-CENTRIC INTERPRETATION (The Inspector)
    st.subheader("Human-Centric Interpretation: The System Dictate")
    impact_indices = np.argsort(np.abs(deltas))[-3:][::-1] # Top 3 shifts
    
    cols = st.columns(3)
    for i, idx in enumerate(impact_indices):
        guide = get_state_guide(idx + 1)
        with cols[i]:
            st.metric(label=labels[idx], value=f"{all_final[idx]:.2f}", delta=f"{deltas[idx]:.3f}")
            if guide:
                st.write(f"**Mood:** {guide.get('mood_description', 'N/A')}")
                st.write(f"**Keywords:** {', '.join(guide.get('keywords', []))}")
                st.info(f"**Function:** {guide.get('physical_function', 'N/A')}")
                st.caption(f"**Manifestation:** {guide.get('manifestation', 'N/A')}")

    # 5. VISUAL ANALYSIS
    st.markdown("---")
    st.subheader("Field Stability & Trajectory")
    
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    for i in range(N_CORE):
        ax1.plot(history_core[:, i], label=f"C{i+1}", alpha=0.7)
    for j in range(N_SURFACE):
        ax1.plot(history_surface[:, j], linestyle='--', label=f"S{j+8}", alpha=0.5)
    ax1.set_title("Temporal Path toward Instantiation")
    st.pyplot(fig1)

    # 6. PDF REPORT GENERATION
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "Valence-Pi Structural Alignment Report", ln=True, align='C')
    
    pdf.set_font("Helvetica", size=10)
    pdf.ln(5)
    pdf.multi_cell(0, 7, f"Life Stage: {age_cat}")
    pdf.multi_cell(0, 7, f"Intent: {user_intent}")
    pdf.ln(10)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Top 3 Semantic Shifts (Actionable Guidance)", ln=True)
    pdf.set_font("Helvetica", size=10)
    
    for idx in impact_indices:
        guide = get_state_guide(idx + 1)
        if guide:
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(0, 8, f"{labels[idx]} - {guide['polarity']}", ln=True)
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 5, f"Emotional Cluster: {', '.join(guide['keywords'])}")
            pdf.multi_cell(0, 5, f"Physical Function: {guide['physical_function']}")
            pdf.multi_cell(0, 5, f"Instantiation Effect: {guide['instantiation_effect']}")
            pdf.ln(4)

    pdf_bytes = pdf.output()
    st.download_button(
        label="📥 Download Research Guidance Report", 
        data=bytes(pdf_bytes), 
        file_name="ValencePi_Human_Report.pdf", 
        mime="application/pdf"
    )

else:
    st.info("Adjust the sliders in the sidebar and click 'Run Realignment Simulation' to view the semantic breakdown.")