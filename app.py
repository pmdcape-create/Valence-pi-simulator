import streamlit as st
import numpy as np
import json
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import tempfile
import os

# Internal engine imports
from radial_engine.config import (
    N_CORE, N_SURFACE, BASELINE_CORE, BASELINE_SURFACE, PROPAGATION_DAMPING
)
from radial_engine.simulation import run_simulation

# Import the Narrative Logic Engine
from radial_engine.narrative_engine import NarrativeEngine

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Valence-Pi Simulator", layout="wide")

# ==========================================
# DATA & ENGINE INITIALIZATION
# ==========================================
# Check for JSON in multiple possible locations
JSON_PATHS = ["stateGuides.json", "radial_engine/stateGuides.json"]
JSON_PATH = next((p for p in JSON_PATHS if os.path.exists(p)), None)

if JSON_PATH:
    try:
        engine = NarrativeEngine(JSON_PATH)
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            state_guides_data = json.load(f)["stateGuides"]
    except Exception as e:
        st.error(f"Error initializing Narrative Engine: {e}")
        state_guides_data = []
else:
    st.error("stateGuides.json not found. Please ensure it is in the root directory.")
    state_guides_data = []

def get_state_guide(state_number):
    for guide in state_guides_data:
        if guide["state"] == state_number:
            return guide
    return None

# ==========================================
# SIDEBAR UI
# ==========================================
st.sidebar.title("Valence-Pi Controls")
st.sidebar.markdown("Adjust baseline potentials to simulate systemic realignment.")

with st.sidebar:
    st.subheader("Core Potentials (1-7)")
    core_baselines = []
    for i in range(N_CORE):
        # The lines below are now properly indented
        val = st.slider(f"State {i+1} Baseline", -1.0, 1.0, BASELINE_CORE[i], 0.05, key=f"core_{i}")
        core_baselines.append(val)

    st.subheader("Surface Potentials (8-22)")
    surf_baselines = []
    for i in range(N_SURFACE):
        # The lines below are now properly indented
        val = st.slider(f"State {i+8} Baseline", -1.0, 1.0, BASELINE_SURFACE[i], 0.05, key=f"surf_{i}")
        surf_baselines.append(val)

    st.divider()
    damping = st.slider("Propagation Damping", 0.0, 1.0, PROPAGATION_DAMPING, 0.01)

# ==========================================
# SIMULATION EXECUTION
# ==========================================
# Combine baselines for simulation
updated_baselines = np.concatenate([core_baselines, surf_baselines])

# Run the simulation logic
final_states, history = run_simulation(updated_baselines, damping)

# ==========================================
# MAIN UI DISPLAY
# ==========================================
st.title("Valence-Pi Systemic Simulator")
st.markdown("---")

# Tabbed interface for Report vs Analytics
tab_rep, tab_vis, tab_data = st.tabs(["📋 Narrative Report", "📊 Visual Analysis", "⚙️ Technical Data"])

with tab_rep:
    st.header("Architect Narrative Analysis")
    st.info("The logic engine translates numerical valence into structural capacity reports.")
    
    # Iterate through all 22 states
    for i, val in enumerate(final_states):
        state_num = i + 1
        guide = get_state_guide(state_num)
        
        if guide:
            # Color-coded metric display
            color = "green" if val >= 0.4 else "red" if val <= -0.4 else "orange"
            
            with st.expander(f"STATE {state_num}: {guide.get('named_state_descriptor', 'Unknown State')}"):
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.metric("Valence", f"{val:.3f}")
                with col2:
                    # FETCH NARRATIVE FROM ENGINE
                    narrative_text = engine.get_narrative(state_num, val)
                    st.write(narrative_text)
                
                st.caption(f"**Function:** {guide['physical_function']} | **Effect:** {guide['instantiation_effect']}")

with tab_vis:
    st.subheader("Systemic Equilibrium Plot")
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#2E86C1' if x >= 0 else '#CB4335' for x in final_states]
    ax.bar(range(1, 23), final_states, color=colors)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xticks(range(1, 23))
    ax.set_xlabel("State ID")
    ax.set_ylabel("Valence Output")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

with tab_data:
    df = pd.DataFrame({
        "State": range(1, 23),
        "Descriptor": [get_state_guide(i+1).get('named_state_descriptor', 'N/A') for i in range(22)],
        "Value": final_states
    })
    st.dataframe(df, use_container_width=True)

# ==========================================
# PDF REPORT GENERATION
# ==========================================
def create_pdf(states):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "Valence-Pi Systemic Realignment Report", ln=True, align='C')
    pdf.ln(10)

    for i, val in enumerate(states):
        state_num = i + 1
        guide = get_state_guide(state_num)
        if guide:
            # State Title
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 8, f"State {state_num}: {guide.get('named_state_descriptor', 'N/A')}", ln=True)
            
            # Sub-header with value
            pdf.set_font("Helvetica", 'I', 10)
            pdf.cell(0, 6, f"Calculated Valence: {val:.3f}", ln=True)
            
            # Narrative from Engine
            pdf.set_font("Helvetica", size=10)
            narrative = engine.get_narrative(state_num, val)
            pdf.multi_cell(0, 5, narrative)
            pdf.ln(4)
            
    return pdf.output(dest='S').encode('latin-1')

# Download Button
if st.button("Export PDF Report"):
    pdf_bytes = create_pdf(final_states)
    st.download_button(
        label="Download Full Narrative Report",
        data=pdf_bytes,
        file_name="Valence_Pi_Report.pdf",
        mime="application/pdf"
    )

st.markdown("---")
st.caption("Valence-pi-simulator | Built on Capacity-Based Field Theory")