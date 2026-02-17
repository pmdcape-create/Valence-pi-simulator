# simulation.py
import numpy as np
from .matrices import (
    build_core_matrix, build_surface_matrix, 
    build_projection_matrix, build_feedback_matrix
)
from .dynamics import evolve

def run_simulation(initial_core=None, initial_surface=None,
                   target_core=None, target_surface=None,
                   steps=100, damping=None):
    """
    Runs the Valence-Pi simulation engine. 
    Accepts an optional 'damping' parameter to simulate biological Age/Plasticity.
    """
    
    # 1. Build the interaction matrices
    C = build_core_matrix()
    L = build_surface_matrix()
    R = build_projection_matrix()
    F = build_feedback_matrix()

    # 2. Initialize states
    if initial_core is None:
        from .config import N_CORE
        initial_core = np.random.uniform(-0.3, 0.3, N_CORE)
    if initial_surface is None:
        from .config import N_SURFACE
        initial_surface = np.random.uniform(-0.3, 0.3, N_SURFACE)

    # 3. Use KEYWORD ARGUMENTS to evolve the system
    # We pass the dynamic damping here so the 'evolve' function can use it
    history_core, history_surface = evolve(
        core=initial_core,
        surface=initial_surface,
        steps=steps,
        target_core=target_core,
        target_surface=target_surface,
        C=C, L=L, R=R, F=F,
        damping=damping  # Passed from app.py
    )

    return history_core, history_surface