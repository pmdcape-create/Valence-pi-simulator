import numpy as np

# Core & surface sizes
N_CORE = 7
N_SURFACE = 15

# Propagation constants
PROPAGATION_DAMPING = 0.62
NORMALIZE_AFTER_ADJUST = True

# NEUTRAL SOCIETAL BASELINES
# Based on the structural coherence required for a stable system
BASELINE_CORE = np.array([0.50, -0.60, 0.20, -0.30, -0.40, -0.50, -0.70], dtype=np.float32)

# Surface states (8-22) set to 0.0 (Neutral)
# This allows the public to see how their adjustments move the system from zero
BASELINE_SURFACE = np.zeros(N_SURFACE, dtype=np.float32)