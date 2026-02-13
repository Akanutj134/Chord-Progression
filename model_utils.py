Model_utils.py

import json
from tensorflow.keras.models import load_model

def load_model_and_mappings(model_path, mappings_path):
    """
    Load the trained model and chord mappings.
    """
    try:
        model = load_model(model_path)
    except Exception as e:
        raise RuntimeError(f"Error loading model: {e}")

    try:
        with open(mappings_path, 'r') as f:
            mappings = json.load(f)
        chord_to_index = mappings['chord_to_index']
        index_to_chord = {int(k): v for k, v in mappings['index_to_chord'].items()}
    except Exception as e:
        raise RuntimeError(f"Error loading mappings: {e}")

