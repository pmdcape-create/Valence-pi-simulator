# radial_engine/visualization.py

import plotly.graph_objects as go
import numpy as np

def plot_core_surface(core, surface, title="Valence States Simulation"):
    """Combined polar plot of core + surface."""
    theta_core = np.linspace(0, 2*np.pi, len(core), endpoint=False)
    theta_surf = np.linspace(0, 2*np.pi, len(surface), endpoint=False)

    fig = go.Figure()

    # Core
    fig.add_trace(go.Scatterpolar(
        r=np.concatenate([core, [core[0]]]),
        theta=np.concatenate([theta_core, [theta_core[0]]]),
        fill='toself',
        name='Core',
        line_color='blue'
    ))

    # Surface
    fig.add_trace(go.Scatterpolar(
        r=np.concatenate([surface, [surface[0]]]),
        theta=np.concatenate([theta_surf, [theta_surf[0]]]),
        fill='toself',
        name='Surface',
        line_color='green'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(range=[-1, 1])),
        title=title
    )
    return fig
