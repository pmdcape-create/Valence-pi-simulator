# radial_engine/geometry.py
import numpy as np
from .config import N_SURFACE

# Placeholder for any geometric or radial computations
def polar_to_cartesian(r, theta):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

def circular_distance_matrix():
    angles = np.linspace(0, 2*np.pi, N_SURFACE, endpoint=False)
    dist = np.zeros((N_SURFACE, N_SURFACE))

    for i in range(N_SURFACE):
        for j in range(N_SURFACE):
            diff = abs(angles[i] - angles[j])
            diff = min(diff, 2*np.pi - diff)
            dist[i, j] = diff

    return dist
