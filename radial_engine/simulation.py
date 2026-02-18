import numpy as np
from .matrices import (
    build_core_matrix, build_surface_matrix, 
    build_projection_matrix, build_feedback_matrix
)
from .dynamics import evolve

def run_simulation(initial_core=None, initial_surface=None, steps=100, damping=None):
    # 1. Build matrices from matrices.py
    C = build_core_matrix()
    L = build_surface_matrix()
    R = build_projection_matrix()
    F = build_feedback_matrix()

    # 2. Run simulation
    history_core, history_surface = evolve(
        core=initial_core,
        surface=initial_surface,
        steps=steps,
        C=C, L=L, R=R, F=F,
        damping=damping
    )

    # 3. Extract ONLY the final equilibrium state for the UI
    final_combined = np.concatenate([history_core[-1], history_surface[-1]])
    
    return final_combined, (history_core, history_surface)