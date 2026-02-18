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

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Valence-Pi Simulator", layout="wide")

# ==========================================
# DATA LOADING
# ==========================================
JSON_PATHS = ["radial_engine/stateGuides.json", "stateGuides.json"]
state_guides_data = []

for path in JSON_PATHS:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                state_guides_data = json.load(f)["stateGuides"]
                break
        except Exception as e:
            st.sidebar.warning(f"Error reading {path}: {e}")

def get_state_guide(state_number):
    for guide in state_guides_data:
        if guide["state"] == state_number:
            return guide
    return None

# ==========================================
# SIDEBAR UI
# ==========================================
st.sidebar.title("System Dynamics")
age_cat = st.sidebar.selectbox("Subject Life Stage", options=["Childhood", "Adolescence", "Adulthood", "Early Ageing", "Late Ageing"], index=2)
steps_input = st.sidebar.number_input("Simulation Steps", 1, 100, 10)

st.sidebar.subheader("Simulation Intent")
user_intent = st.sidebar.text_area("Describe your goal:", height=100)

st.sidebar.subheader("Adjust States (Baseline)")
for i in range(N_CORE):
    guide = get_state_guide(i + 1)
    label = f"C{i+1}: {guide['polarity'].split(' / ')[0] if guide else 'Core'}"
    st.sidebar.slider(label, -1.0, 1.0, step=0.01, key=f"core_{i}", value=0.70)

for i in range(N_SURFACE):
    guide = get_state_guide(i + N_CORE + 1)
    label = f"S{i+N_CORE+1}: {guide['polarity'].split(' / ')[0] if guide else 'Surface'}"
    st.sidebar.slider(label, -1.0, 1.0, step=0.01, key=f"surface_{i}", value=0.65)

run_sim = st.sidebar.button("Run Realignment Simulation")

# ==========================================
# MAIN INTERFACE & LOGIC
# ==========================================
st.title("Valence-Pi Structural Simulator")
st.caption(f"Status: {len(state_guides_data)} semantic states active.")

if run_sim:
    # 1. Capture Inputs from Sliders
    t_core = np.array([st.session_state[f"core_{i}"] for i in range(N_CORE)])
    t_surface = np.array([st.session_state[f"surface_{i}"] for i in range(N_SURFACE)])

    # 2. Run Engine (Correctly Indented)
    try:
        history_core, history_surface = run_simulation(
            BASELINE_CORE, 
            BASELINE_SURFACE, 
            t_core, 
            t_surface
        )
    except Exception as e:
        st.error(f"Simulation Engine Error: {e}")
        st.stop()

    # --- SAFETY GATE ---
    if history_core is not None and len(history_core) > 0:
        # 3. Process Results (Flatten and Align)
        core_final = np.atleast_1d(history_core[-1]).flatten()
        surf_final = np.atleast_1d(history_surface[-1]).flatten()
        
        all_final = np.concatenate([core_final, surf_final])
        all_initial = np.concatenate([
            np.atleast_1d(BASELINE_CORE).flatten(), 
            np.atleast_1d(BASELINE_SURFACE).flatten()
        ])

        # Resolve length mismatches before subtraction
        min_len = min(len(all_final), len(all_initial))
        all_final_aligned = all_final[:min_len]
        all_initial_aligned = all_initial[:min_len]
        
        deltas = all_final_aligned - all_initial_aligned
        
        # Define dynamic labels
        full_labels = [f"C{i+1}" for i in range(len(core_final))] + \
                      [f"S{i+len(core_final)+1}" for i in range(len(surf_final))]
        labels = full_labels[:min_len]
                
        # 4. THE INSPECTOR
        st.header("Human-Centric Interpretation")
        impact_indices = np.argsort(np.abs(deltas))[-3:][::-1]
        cols = st.columns(3)
        for i, idx in enumerate(impact_indices):
            guide = get_state_guide(idx + 1)
            with cols[i]:
                st.metric(label=labels[idx], value=f"{all_final[idx]:.2f}", delta=f"{deltas[idx]:.3f}")
                if guide:
                    st.write(f"**Mood:** {guide.get('mood_description', 'N/A')}")
                    st.write(f"**Keywords:** {', '.join(guide.get('keywords', []))}")
                    st.info(f"**Function:** {guide.get('physical_function', 'N/A')}")

        # 5. GRAPHS DASHBOARD
        st.markdown("---")
        st.header("Visual Field Analysis")
        tab1, tab2, tab3 = st.tabs(["Combined Trajectory", "Core Stability", "Surface Alignment"])
        
        with tab1:
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            for i in range(N_CORE): ax1.plot(history_core[:, i], label=f"C{i+1}")
            for j in range(N_SURFACE): ax1.plot(history_surface[:, j], linestyle='--', label=f"S{j+N_CORE+1}")
            ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
            st.pyplot(fig1)

        with tab2:
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            for i in range(N_CORE): ax2.plot(history_core[:, i], label=f"C{i+1}")
            ax2.legend(loc='best')
            st.pyplot(fig2)

        with tab3:
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            for j in range(N_SURFACE): ax3.plot(history_surface[:, j], label=f"S{j+N_CORE+1}")
            ax3.legend(loc='best')
            st.pyplot(fig3)

        # 6. PDF REPORT
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, "Valence-Pi Structural Alignment Report", ln=True, align='C')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            fig1.savefig(tmp.name, bbox_inches='tight')
            pdf.image(tmp.name, x=10, w=180)

        pdf_path = tempfile.mktemp(suffix=".pdf")
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download Research Report", data=f.read(), file_name="ValencePi_Report.pdf")

    else:
        st.error("The simulation completed but returned no data.")
        st.stop()