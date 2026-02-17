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

run_sim = st.sidebar.button("Run Simulation")

# ==========================================
# SIMULATION EXECUTION & RESULTS
# ==========================================
if run_sim:
    # 1. Capture Target Values
    t_core = np.array([st.session_state[f"core_{i}"] for i in range(N_CORE)])
    t_surface = np.array([st.session_state[f"surface_{i}"] for i in range(N_SURFACE)])

    # 2. Identify Adjusted Triggers
    adj_c = [i for i in range(N_CORE) if abs(t_core[i] - CUSTOM_DEFAULTS.get(f"core_{i}", DEFAULT_CORE_VAL)) > 0.001]
    adj_s = [i for i in range(N_SURFACE) if abs(t_surface[i] - CUSTOM_DEFAULTS.get(f"surface_{i}", DEFAULT_SURFACE_AVG)) > 0.001]

    # 3. Define Start Point
    if use_target == "Target states (user-defined)":
        start_core, start_surface = np.array(BASELINE_CORE), np.array(BASELINE_SURFACE)
    else:
        start_core, start_surface = t_core, t_surface
        t_core, t_surface = None, None

    # 4. Run Simulation
    history_core, history_surface = run_simulation(
        initial_core=start_core, initial_surface=start_surface,
        target_core=t_core, target_surface=t_surface,
        steps=int(steps_input_val), damping=effective_damping
    )

    # 5. Data Preparation
    final_core = history_core[-1, :]
    final_surface = history_surface[-1, :]
    labels = [f"C{i+1}" for i in range(N_CORE)] + [f"S{i+8}" for i in range(N_SURFACE)]
    before_vals = list(start_core) + list(start_surface)
    after_vals = list(final_core) + list(final_surface)
    deltas = np.array(after_vals) - np.array(before_vals)
    steps_range = np.arange(history_core.shape[0])

    # --- Visuals in Streamlit ---
    st.subheader(f"State Dynamics: {age_cat}")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    cmap = plt.get_cmap("tab20")
    for i in range(N_CORE):
        bold = i in adj_c
        ax1.plot(steps_range, history_core[:, i], color=cmap(i % 20), lw=3.5 if bold else 1.0, alpha=1.0 if bold else 0.4, label=f"C{i+1}" + (" (TRIGGER)" if bold else ""))
    for j in range(N_SURFACE):
        bold = j in adj_s
        ax1.plot(steps_range, history_surface[:, j], color=cmap((j+N_CORE)%20), lw=3.0 if bold else 0.8, alpha=1.0 if bold else 0.3, ls='-' if bold else '--', label=f"S{N_CORE+j+1}" + (" (TRIGGER)" if bold else ""))
    ax1.legend(fontsize=7, bbox_to_anchor=(1.02, 1), loc='upper left')
    st.pyplot(fig1)

    st.subheader("System Stability Index (Field Residue)")
    stability_data = np.sum(np.abs(history_core - start_core), axis=1) + np.sum(np.abs(history_surface - start_surface), axis=1)
    fig2, ax2 = plt.subplots(figsize=(10, 2))
    ax2.plot(steps_range, stability_data, color="darkred", lw=2)
    st.pyplot(fig2)

    st.subheader("Structural Re-alignment: Final State Configuration")
    x = np.arange(len(labels))
    width = 0.35
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.bar(x - width/2, before_vals, width, label='Initial (Baseline)', color='lightgrey')
    after_colors = ['blue' if i < N_CORE and i in adj_c else 'green' if i >= N_CORE and (i-N_CORE) in adj_s else 'skyblue' if i < N_CORE else 'lightgreen' for i in range(len(labels))]
    ax3.bar(x + width/2, after_vals, width, label='Final (Instantiated)', color=after_colors)
    ax3.set_xticks(x)
    ax3.set_xticklabels(labels, rotation=45, fontsize=8)
    ax3.legend(fontsize=8)
    ax3.axhline(0, color='black', linewidth=0.8)
    st.pyplot(fig3)

    # ==========================================
    # PDF REPORT EXPORT (WITH DYNAMIC WRITING)
    # ==========================================
    st.divider()
    st.subheader("Export Research Data")
    
    safe_age_cat = age_cat.replace("–", "-") 
    
    # 1. Initialize PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Metadata
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt="Valence-Pi Structural Alignment Report", ln=True, align='C')
    pdf.set_font("Helvetica", size=10)
    pdf.ln(5)
    pdf.cell(200, 7, txt=f"Life Stage: {safe_age_cat}", ln=True)
    pdf.cell(200, 7, txt=f"Simulation Steps: {steps_input_val} | Damping: {effective_damping:.4f}", ln=True)

    # Analytics for Dynamic Commentary
    max_delta_idx = np.argmax(np.abs(deltas))
    max_delta_val = deltas[max_delta_idx]
    max_delta_label = labels[max_delta_idx]
    avg_delta = np.mean(np.abs(deltas))
    system_instantiated = all(v >= 0.99 for v in after_vals)
    total_field_residue = max(stability_data)
    active_triggers = [labels[i] for i in adj_c] + [labels[i+N_CORE] for i in adj_s]

    # Helper function to add plots
    def add_plot_to_pdf(fig, title, y_pos):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, format='png', bbox_inches='tight', dpi=150)
            pdf.set_font("Helvetica", 'I', 10)
            if title: pdf.cell(200, 8, txt=title, ln=True)
            pdf.image(tmpfile.name, x=10, y=None, w=180)
            pdf.ln(5)
        os.unlink(tmpfile.name)

    # 2. Dynamic Analysis Page
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(200, 10, txt="Visual Field Analysis & Structural Insights", ln=True)
    pdf.ln(5)

    # Dynamics Text
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(200, 7, txt="1. State Dynamics (Temporal Path Interpretation)", ln=True)
    pdf.set_font("Helvetica", size=10)
    dynamics_text = (f"In this {safe_age_cat} simulation, the system achieved convergence over {steps_input_val} steps. "
                     f"The trajectories of identity triggers ({', '.join(active_triggers)}) initiated a law-like re-alignment, "
                     "pulling the entire 22-state field toward the target valence.")
    pdf.multi_cell(0, 5, txt=dynamics_text)
    add_plot_to_pdf(fig1, "", pdf.get_y())

    # Stability Text
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(200, 7, txt="2. System Stability & Field Residue", ln=True)
    pdf.set_font("Helvetica", size=10)
    stability_text = (f"The Stability Index recorded a peak field residue of {total_field_residue:.2f}. "
                      "This represents the 'Awareness' or structural friction generated as the system "
                      "resolved initial contradictions to accommodate your intentional triggers.")
    pdf.multi_cell(0, 5, txt=stability_text)
    add_plot_to_pdf(fig2, "", pdf.get_y())

    # 3. Final Alignment Page
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(200, 7, txt="3. The 'System Dictate' & Final Alignment", ln=True)
    pdf.set_font("Helvetica", size=10)
    status = "achieved total uniform instantiation (1.000)." if system_instantiated else "reached a partial equilibrium."
    realignment_text = (f"The final configuration {status} The most radical induced shift occurred at {max_delta_label} "
                        f"with a Delta of {max_delta_val:.3f}. On average, the field shifted by {avg_delta:.3f} units "
                        "to maintain systemic integrity.")
    pdf.multi_cell(0, 5, txt=realignment_text)
    add_plot_to_pdf(fig3, "", pdf.get_y())

    # 4. Data Table Page
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(200, 10, txt="Induced Delta Table (System Dictate)", ln=True)
    pdf.set_font("Helvetica", size=8)
    pdf.cell(40, 8, "State", 1); pdf.cell(40, 8, "Initial", 1); pdf.cell(40, 8, "Final", 1); pdf.cell(40, 8, "Delta", 1); pdf.ln()
    for i in range(len(labels)):
        pdf.cell(40, 7, labels[i], 1); pdf.cell(40, 7, f"{before_vals[i]:.3f}", 1); pdf.cell(40, 7, f"{after_vals[i]:.3f}", 1); pdf.cell(40, 7, f"{deltas[i]:.3f}", 1); pdf.ln()

    pdf_bytes = pdf.output()
    st.download_button(label="📥 Download Full Research Report", data=bytes(pdf_bytes), file_name=f"ValencePi_Full_Report_{safe_age_cat.replace(' ', '_')}.pdf", mime="application/pdf")