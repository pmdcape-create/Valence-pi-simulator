# Valence-Pi: 22 Valence States Adjustment Simulator

An interactive Streamlit app to model adjustments in a 22-dimensional valence domain inspired by polarity states, with **pi-relational (22/7) propagation between states**.

---

## Core Concept

- **22 valence states** represent fundamental polarities (e.g., Existence/Non-Existence, Coherence/Chaos, Endurance/Fragility, etc.).  
- **Core 7** act as foundational "radius" dimensions.  
- **Full 22** form the enclosing "circumference", scaled relationally via **pi ≈ 22/7**.  
- Adjustments propagate through a dependency matrix, with damping and normalization to preserve system continuity.  

---

## Simulation Philosophy

- **Incremental adjustments** reflect real-world trait evolution.  
  - *Why it’s realistic:* Personality traits like openness or defensiveness don’t shift instantly — small repeated efforts are needed to produce measurable change. Each simulation step models these **gradual, marginal changes**.

- **Target states allow intentional interventions.**  
  - *Why it’s realistic:* Humans can consciously work on traits. Setting a target simulates **deliberate effort**, while the simulation still applies gradual adjustments over steps, reflecting that even intentional change unfolds over time.

- **Core-to-surface influence.**  
  - *Why it’s realistic:* Foundational traits (core states) influence situational behaviors (surface states). For example, internal coherence shapes clarity and emotional regulation, so the simulation propagates changes hierarchically to maintain natural dependencies.

- **Realistic inertia.**  
  - *Why it’s realistic:* States resist abrupt changes without repeated effort, modeling **behavioral momentum** and natural resistance, making the simulation defensible in real-world personality contexts.

- **Defensible personality dynamics.**  
  - *Why it’s realistic:* This is not just a numeric slider tool — the combination of core/surface structure, incremental adjustments, and propagation logic mirrors real-world personality change dynamics, providing **a theoretically grounded model**.

---

## Baseline Vector (Default Starting State)

The hard-coded baseline reflects a 2025/2026 global/societal snapshot, informed by public data (Gallup, WHO, Stats SA, Edelman Trust, Transparency International, etc.):

- Negative lean overall (~ -0.25 average) due to polarization, trust erosion, inequality, youth fragility.  
- Core 7 as radius: Coherence/Chaos heavily negative (-0.70), Unity/Division (-0.60), etc.

**Baseline values** (from -1.0 strong negative to +1.0 strong positive):

State 1: Existence / Non-Existence     +0.50  
State 2: Unity / Division              -0.60  
State 3: Potential / Kinetic           +0.20  
State 4: Static / Dynamic              -0.30  
State 5: Inclusion / Exclusion         -0.40  
State 6: Symmetry / Asymmetry          -0.50  
State 7: Coherence / Chaos             -0.70  
State 8: Will / Submission             -0.30  
State 9: Clarity / Obscurity           -0.50  
State 10: Resonance / Dissonance       -0.40  
State 11: Expansion / Contraction      +0.30  
State 12: Knowledge / Ignorance        0.00  
State 13: Creation / Destruction       -0.20  
State 14: Love / Aversion              +0.20  
State 15: Strategy / Randomness        -0.30  
State 16: Endurance / Fragility        -0.40  
State 17: Abundance / Scarcity         -0.50  
State 18: Influence / Isolation        -0.40  
State 19: Justice / Equilibrium        -0.60  
State 20: Compassion / Detachment      +0.30  
State 21: Purpose / Drift              -0.20  
State 22: Completion / Void            -0.10  

---

## User Guidance

- Use **Incremental mode** to simulate subtle, realistic personality shifts.  
- Use **Target mode** to experiment with deliberate changes in traits.  
- The **State Inspector** shows current value, deviation from baseline, and visual indicators of each state.  
- Repeated simulation steps are required to achieve significant shifts in traits like openness, defensiveness, or resilience.  
