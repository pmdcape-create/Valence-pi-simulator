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
st.set_page_config(
    page_title="Valence-Pi Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# DATA LOADING (Multi-path for flexibility)
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
# SIDEBAR UI (User-Friendly Controls)
# ==========================================
st.sidebar.title("System Dynamics")
age_cat = st.sidebar.selectbox("Subject Life Stage", 
    options=["Childhood", "Adolescence", "Adulthood", "Early Ageing", "Late Ageing"], 
    index=2
)
steps_input = st.sidebar.number_input("Simulation Steps", 1, 100, 10)

st.sidebar.subheader("Simulation Intent")
user_intent = st.sidebar.text_area("Describe your goal:", height=100, placeholder="e.g., Influence through Knowledge...")

st.sidebar.subheader("Adjust States (Baseline)")
# Clean slider labels for better UX
for i in range(N_CORE):
    guide = get_state_guide(i + 1)
    # Extracts only the first word of polarity for the label to keep it clean
    short_label = guide['polarity'].split(' / ')[0] if guide else "Core"
    st.sidebar.slider(f"C{i+1}: {short_label}", -1.0, 1.0, step=0.01, key=f"core_{i}", value=0.70)

for i in range(N_SURFACE):
    guide = get_state_guide(i + N_CORE + 1)
    short_label = guide['polarity'].split(' / ')[0] if guide else "Surface"
    st.sidebar.slider(f"S{i+N_CORE+1}: {short_label}", -1.0, 1.0, step=0.01, key=f"surface_{i}", value=0.65)

run_sim = st.sidebar.button("Run Realignment Simulation", use_container_width=True)

# ==========================================
# MAIN INTERFACE
# ==========================================
st.title("Valence-Pi Structural Simulator")
st.caption(f"System Status: {len(state_guides_data)} semantic states active.")

if run_sim:
    # 1. Prepare Target Data
    t_core = np.array([st.session_state[f"core_{i}"] for i in range(N_CORE)])
    t_surface = np.array([st.session_state[f"surface_{i}"] for i in range(N_SURFACE)])

    # 2. Run Engine (Corrected Try/Except Syntax)
    try:
        # Based on your logs, the engine only accepts 4 positional arguments
        history_core, history_surface = run_simulation(
            BASELINE_CORE, 
            BASELINE_SURFACE, 
            t_core, 
            t_surface
        )
    except Exception as e:
        st.error(f"Simulation Engine Error: {e}")
        st.info("Attempting fallback with combined targets...")
        try:
            target_combined = np.concatenate([t_core, t_surface])
            history_core, history_surface = run_simulation(
                BASELINE_CORE, BASELINE_SURFACE, target_combined
            )
        except Exception as e2:
            st.error(f"Fallback failed: {e2}")
            st.stop()

    # --- SAFETY GATE: Prevent 'Zero-Dimensional' Error ---
    if history_core is None or len(history_core) == 0:
        st.error("The simulation returned no data. Please check your engine configuration.")
        st.stop()

    # 3. Process Results
    # history_core[-1] extracts the final state of the simulation
    all_final = np.concatenate([history_core[-1], history_surface[-1]])
    all_initial = np.concatenate([BASELINE_CORE, BASELINE_SURFACE])
    deltas = all_final - all_initial
    labels = [f"C{i+1}" for i in range(N_CORE)] + [f"S{i+8}" for i in range(N_SURFACE)]
    # 4. TOP IMPACT INSPECTOR (Semantic Highlights)
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

    # 5. THE SIMULATION HEART (Restored Tabbed Visuals)
    st.markdown("---")
    st.header("Visual Field Analysis")
    tab1, tab2, tab3 = st.tabs(["Full Field Trajectory", "Core Stability (C1-C7)", "Surface Alignment (S8-S22)"])
    
    # Figure Generation
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    for i in range(N_CORE): ax1.plot(history_core[:, i], label=f"C{i+1}")
    for j in range(N_SURFACE): ax1.plot(history_surface[:, j], linestyle='--', label=f"S{j+8}")
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small', ncol=1)
    ax1.set_title("Total Field Convergence")

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    for i in range(N_CORE): ax2.plot(history_core[:, i], label=f"C{i+1}")
    ax2.legend(loc='best', fontsize='x-small')
    ax2.set_title("Core Structural Path")

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    for j in range(N_SURFACE): ax3.plot(history_surface[:, j], label=f"S{j+8}")
    ax3.legend(loc='best', fontsize='x-small')
    ax3.set_title("Surface Trigger Activation")

    with tab1: st.pyplot(fig1)
    with tab2: st.pyplot(fig2)
    with tab3: st.pyplot(fig3)

    # 6. INDUCED DELTA TABLE
    st.subheader("Induced Delta Table (System Dictate)")
    df_results = pd.DataFrame({
        "State": labels,
        "Initial": all_initial,
        "Final": all_final,
        "Induced Delta": deltas
    })
    st.dataframe(df_results.style.background_gradient(cmap='RdYlGn', subset=['Induced Delta']), use_container_width=True)

    # 7. RESEARCH REPORT EXPORT (Full Logic)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Page 1: Header & Main Graph
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "Valence-Pi Structural Alignment Report", ln=True, align='C')
    pdf.set_font("Helvetica", size=10)
    pdf.ln(5)
    pdf.multi_cell(180, 7, f"Life Stage: {age_cat}\nIntent: {user_intent}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig1.savefig(tmp.name, bbox_inches='tight')
        pdf.image(tmp.name, x=10, w=185)
    
    # Page 2: Stability & Surface Graphs
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Sub-Field Dynamics", ln=True)
    for f in [fig2, fig3]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            f.savefig(tmp.name, bbox_inches='tight')
            pdf.image(tmp.name, x=10, w=160)
            pdf.ln(5)

    # Page 3: Semantic Actionable Guidance
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "Actionable Semantic Guidance", ln=True)
    pdf.ln(5)
    for idx in impact_indices:
        guide = get_state_guide(idx + 1)
        if guide:
            pdf.set_font("Helvetica", 'B', 11)
            pdf.cell(0, 8, f"{labels[idx]} ({guide['polarity']})", ln=True)
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(180, 6, f"Keywords: {', '.join(guide.get('keywords', []))}")
            pdf.multi_cell(180, 6, f"Physical Function: {guide.get('physical_function', 'N/A')}")
            pdf.multi_cell(180, 6, f"Instantiation Effect: {guide.get('instantiation_effect', 'N/A')}")
            pdf.ln(5)

    # Page 4: Data Table
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Full Induced Delta Data", ln=True)
    pdf.set_font("Helvetica", 'B', 9)
    # Table headers
    pdf.cell(35, 8, "State", 1); pdf.cell(75, 8, "Polarity", 1); pdf.cell(35, 8, "Final Val", 1); pdf.cell(35, 8, "Delta", 1, ln=True)
    pdf.set_font("Helvetica", size=8)
    for i, row in df_results.iterrows():
        g = get_state_guide(i + 1)
        pdf.cell(35, 7, row['State'], 1)
        pdf.cell(75, 7, g['polarity'] if g else "N/A", 1)
        pdf.cell(35, 7, f"{row['Final']:.3f}", 1)
        pdf.cell(35, 7, f"{row['Induced Delta']:.3f}", 1, ln=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            st.download_button("📥 Download Full Research Report", data=f.read(), file_name=f"ValencePi_Report_{age_cat.replace(' ','_')}.pdf")