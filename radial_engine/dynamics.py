import numpy as np
from .config import PROPAGATION_DAMPING

def evolve(core, surface, steps=10, target_core=None, target_surface=None,
           C=None, L=None, R=None, F=None, damping=PROPAGATION_DAMPING):
    """
    Evolve core and surface states over a number of steps.
    """

    core = np.array(core, dtype=float).flatten()
    surface = np.array(surface, dtype=float).flatten()
    
    # Robust conversion for steps to handle both numpy scalars and python ints
    try:
        steps_val = int(np.ravel(steps)[0])
    except (TypeError, IndexError):
        steps_val = int(steps)

    N_CORE = core.size
    N_SURFACE = surface.size

    history_core = np.zeros((steps_val + 1, N_CORE))
    history_surface = np.zeros((steps_val + 1, N_SURFACE))

    history_core[0] = core
    history_surface[0] = surface

    for t in range(1, steps_val + 1):
        # Core update
        core_delta = np.zeros_like(core)
        if target_core is not None:
            core_delta += damping * (target_core - core)
        if C is not None:
            core_delta += C @ core

        # Surface update
        surface_delta = np.zeros_like(surface)
        if target_surface is not None:
            surface_delta += damping * (target_surface - surface)
        if R is not None:
            surface_delta += R @ core
        if F is not None:
            surface_delta += F @ surface
        if L is not None and target_surface is None:
            surface_delta += L @ surface

        # Apply updates and clip to maintain logical system boundaries (-1, 1)
        core = np.clip(core + core_delta, -1, 1)
        surface = np.clip(surface + surface_delta, -1, 1)

        history_core[t] = core
        history_surface[t] = surface

    return history_core, history_surface