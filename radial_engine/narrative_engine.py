import json

class NarrativeEngine:
    def __init__(self, json_path):
        """Loads the state definitions from your local JSON file."""
        with open(json_path, 'r') as f:
            self.data = json.load(f)['stateGuides']

    def get_narrative(self, state_id, value):
        """
        Interprets the simulator value (-1 to +1) and manipulates 
        the sentence frame and keywords accordingly.
        """
        # Find the specific state by ID
        state = next((s for s in self.data if s['state'] == state_id), None)
        if not state:
            return "State configuration missing."

        # Variables for injection
        name = state.get('named_state_descriptor', f"State {state_id}")
        func = state['physical_function']
        # Get the first half of the polarity (e.g., "Unity" from "Unity / Division")
        primary_polarity = state['polarity'].split(' / ')[0]
        keywords = state['keywords']

        # LOGIC ENGINE BRANCHING
        if value >= 0.4:
            # FLOW BRANCH: Focuses on Achievement and the Outcome (Index 0 & 2)
            return (f"Your {name} indicates you have achieved a high level of {func}. "
                    f"This maximizes your capacity for {primary_polarity}, manifesting in a "
                    f"sustained sense of {keywords[0]} and {keywords[2]}.")

        elif value <= -0.4:
            # RESISTANCE BRANCH: Focuses on Restriction (Index 1)
            return (f"Your {name} indicates a restriction in your {func}. "
                    f"This triggers an unmet requirement in your capacity for {primary_polarity}, "
                    f"manifesting primarily as {keywords[1]}.")

        else:
            # STABILIZATION BRANCH: Focuses on Balance (Index 0 & 1)
            return (f"Your {name} is currently stabilizing. You are navigating the "
                    f"balance of {func}, resolving the tension between {keywords[0]} "
                    f"and {keywords[1]}.")