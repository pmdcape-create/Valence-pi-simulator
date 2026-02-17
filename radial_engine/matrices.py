# matrices.py
import numpy as np
from .config import N_CORE, N_SURFACE

def build_core_matrix():
    """
    Backbone (States 1-7): Structural Constraints.
    These govern the coherence required for all surface expression.
    """
    C = np.eye(N_CORE, dtype=np.float32) * 0.85
    # Strong inter-coupling: weakness in one destabilizes the entire backbone
    for i in range(N_CORE):
        for j in range(N_CORE):
            if i != j:
                C[i, j] = 0.12 
    return C

def build_surface_matrix():
    """
    Circumference (States 8-22): Expressive Capacities.
    Mappings based on 'Physical Polarity Functions' (Section 7.1).
    """
    L = np.eye(N_SURFACE, dtype=np.float32) * 0.6
    
    # INDICES calculation: State Number - 8
    # ---------------------------------------------------------
    # Knowledge (S12 -> index 4) supports Strategy (S15 -> index 7)
    # Logic: Potential Mapping guides the Feedback Loop 
    L[7, 4] = 0.35  
    
    # Knowledge (S12 -> index 4) increases Clarity (S9 -> index 1)
    # Logic: Insight improves the Signal-to-Noise Ratio 
    L[1, 4] = 0.45 

    # Purpose (S21 -> index 13) provides direction for Strategy (S15 -> index 7)
    # Logic: Gradient Direction biases the Feedback Loop 
    L[7, 13] = 0.50

    # Abundance (S17 -> index 9) allows for Expansion (S11 -> index 3)
    # Logic: Energy Reservoir enables Volume Modulation 
    L[3, 9] = 0.40

    # Endurance (S16 -> index 8) stabilizes Purpose (S21 -> index 13)
    # Logic: Resistance to stress maintains Gradient Direction 
    L[13, 8] = 0.25

    # Creation (S13 -> index 5) inversely affects Void/Completion (S22 -> index 14)
    # Logic: Generation vs Saturation/Release 
    L[14, 5] = -0.30

    return L

def build_projection_matrix():
    """
    Radius (Core to Surface):
    The 7 Primary states 'always impact' the 15 Secondary states[cite: 157].
    """
    # High baseline: Core changes are the primary drivers of the system
    R = np.ones((N_SURFACE, N_CORE), dtype=np.float32) * 0.15
    
    # Specific Rule: Coherence (C7/Index 6) is the gatekeeper for Clarity (S9/Index 1)
    # Logic: Phase alignment determines Signal-to-Noise ratio 
    R[1, 6] = 0.55 
    
    return R

def build_feedback_matrix():
    """
    Feedback (Surface to Core):
    Surface capacities feed back to resolve or stress the structural backbone.
    """
    # Identity baseline for self-persistence
    F = np.eye(N_SURFACE, dtype=np.float32) * 0.15
    
    # Specific Feedback: Strategy (S15/Index 7) feeds back to Static/Dynamic (C4/Index 3)
    # Logic: Purposeful action stabilizes the rate of change 
    F[7, 3] = 0.20
    
    return F