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
    # 1. Run Simulation
    t_core = np.array([st.session_state[f"core_{i}"] for i in range(N_CORE)])
    t_surface = np.array([st.session_state[f"surface_{i}"] for i in range(N_SURFACE)])

    history_core, history_surface = run_simulation(
        initial_core=BASELINE_CORE, initial_surface=BASELINE_SURFACE,
        target_core=t_core, target_surface=t_surface,
        steps=int(steps_input), damping=0.886
    )
    
    # 2. Results & Deltas
    all_final = np.concatenate([history_core[-1], history_surface[-1]])
    all_initial = np.concatenate([BASELINE_CORE, BASELINE_SURFACE])
    deltas = all_final - all_initial
    labels = [f"C{i+1}" for i in range(N_CORE)] + [f"S{i+8}" for i in range(N_SURFACE)]

    # 3. THE INSPECTOR (Top 3 Semantic Shifts)
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
                st.info(f"**Physical Function:** {guide.get('physical_function', 'N/A')}")
                st.caption(f"**Manifestation:** {guide.get('manifestation', 'N/A')}")

    # 4. GRAPHS DASHBOARD (Restored all 3 graphs)
    st.markdown("---")
    st.header("System Realignment Visuals")
    tab1, tab2, tab3 = st.tabs(["Combined Trajectory", "Core Stability", "Surface Alignment"])
    
    # Figure 1: Combined
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    for i in range(N_CORE): ax1.plot(history_core[:, i], label=f"C{i+1}")
    for j in range(N_SURFACE): ax1.plot(history_surface[:, j], linestyle='--', label=f"S{j+8}")
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
    ax1.set_title("Full Field Realignment")

    # Figure 2: Core
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    for i in range(N_CORE): ax2.plot(history_core[:, i], label=f"C{i+1}")
    ax2.legend(loc='best')
    ax2.set_title("Core (C1-C7) Stability Path")

    # Figure 3: Surface
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    for j in range(N_SURFACE): ax3.plot(history_surface[:, j], label=f"S{j+8}")
    ax3.legend(loc='best')
    ax3.set_title("Surface (S8-S22) Activation Path")

    with tab1: st.pyplot(fig1)
    with tab2: st.pyplot(fig2)
    with tab3: st.pyplot(fig3)

    # 5. DATA TABLE (Full width)
    st.subheader("Final State Values")
    df_results = pd.DataFrame({"State": labels, "Final Value": all_final, "Delta": deltas})
    st.dataframe(df_results.style.highlight_max(axis=0), use_container_width=True)

    # 6. PDF EXPORT (Fixed for all graphs and full text)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "Valence-Pi Structural Alignment Report", ln=True, align='C')
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(180, 7, f"Intent: {user_intent}")

    # Add ALL 3 Graphs to PDF
    for f in [fig1, fig2, fig3]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            f.savefig(tmp.name, bbox_inches='tight')
            pdf.image(tmp.name, x=10, w=180)
            pdf.ln(2)

    # Semantic Shift Detail
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Actionable Semantic Guidance", ln=True)
    for idx in impact_indices:
        guide = get_state_guide(idx + 1)
        if guide:
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(180, 8, f"{labels[idx]} ({guide['polarity']})", ln=True)
            pdf.set_font("Helvetica", size=9)
            pdf.multi_cell(180, 5, f"Keywords: {', '.join(guide.get('keywords', []))}")
            pdf.multi_cell(180, 5, f"Physical Function: {guide.get('physical_function', 'N/A')}")
            pdf.multi_cell(180, 5, f"Instantiation Effect: {guide.get('instantiation_effect', 'N/A')}")
            pdf.ln(4)

    # Data Table Page
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Full State Realignment Data", ln=True)
    pdf.set_font("Helvetica", 'B', 9)
    pdf.cell(30, 8, "State", 1); pdf.cell(80, 8, "Polarity", 1); pdf.cell(35, 8, "Value", 1); pdf.cell(35, 8, "Delta", 1, ln=True)
    pdf.set_font("Helvetica", size=8)
    for i, val in enumerate(all_final):
        g = get_state_guide(i + 1)
        pdf.cell(30, 7, labels[i], 1)
        pdf.cell(80, 7, g['polarity'] if g else "N/A", 1)
        pdf.cell(35, 7, f"{val:.3f}", 1)
        pdf.cell(35, 7, f"{deltas[i]:.3f}", 1, ln=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            st.download_button("📥 Download Full Research Report", data=f.read(), file_name="ValencePi_Full_Report.pdf")