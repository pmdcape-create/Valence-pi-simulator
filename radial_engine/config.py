import numpy as np

# Core & surface sizes
N_CORE = 7
N_SURFACE = 15

# Propagation constants
PROPAGATION_DAMPING = 0.62
NORMALIZE_AFTER_ADJUST = True

# Baseline vectors (defaults for the 22 states)
BASELINE_CORE = np.array([0.50, -0.60, 0.20, -0.30, -0.40, -0.50, -0.70], dtype=np.float32)
BASELINE_SURFACE = np.array([-0.30, -0.50, -0.40, 0.30, 0.00, -0.20, 0.20,
                             -0.30, -0.40, -0.50, -0.40, -0.60, 0.30, -0.20, -0.10], dtype=np.float32)
