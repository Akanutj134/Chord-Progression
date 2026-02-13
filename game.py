from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  
import random
import os
import json
from generate_midi import create_midi 

app = Flask(__name__)
CORS(app)  #  Allow requests from any origin

MIDI_FOLDER = "static/midi"
os.makedirs(MIDI_FOLDER, exist_ok=True) 

# Load mood-based chord mappings
mappings = {}
moods = ["happy", "sad", "calm", "excited", "melancholic"]

for mood in moods:
    try:
        with open(f'mappings/{mood}_mappings.json', 'r') as f:
            mappings[mood] = json.load(f)
        print(f" Loaded mappings for mood: {mood}")
    except Exception as e:
        print(f" Error loading mappings for '{mood}': {e}")

selected_mood = "happy"
current_chord = "C"

@app.route('/')
def index():
    return render_template('game.html')

@app.route('/select-mood', methods=['POST'])
def select_mood():
    global selected_mood
    data = request.get_json()
    mood = data.get("mood", "happy")
    
    if mood in mappings:
        selected_mood = mood
        return jsonify({"status": "success", "mood": selected_mood}), 200
    else:
        return jsonify({"error": "Mood not found!"}), 400

@app.route('/next-chord', methods=['POST'])
def next_chord():
    global current_chord, selected_mood
    if selected_mood not in mappings:
        return jsonify({"error": "Mappings for mood not found!"}), 400

    chord_list = list(mappings[selected_mood]["index_to_chord"].values())
    if not chord_list:
        return jsonify({"error": "No chords found for the selected mood!"}), 400

    current_chord = random.choice(chord_list)
    return jsonify({"chord": current_chord}), 200

@app.route('/play-chord', methods=['POST'])
def play_chord():
    """Handles playing the chord by generating and returning a MIDI file URL."""
    data = request.get_json()
    chord = data.get("chord")

    if not chord:
        return jsonify({"error": "No chord provided"}), 400

    midi_filename = f"{chord}.mid"
    midi_filepath = os.path.join(MIDI_FOLDER, midi_filename)

    # Generate the MIDI file if it doesn't exist
    if not os.path.exists(midi_filepath):
        create_midi([chord], midi_filepath)

    midi_url = f"http://127.0.0.1:5002/static/midi/{midi_filename}"
    
    print(f"🎵 MIDI generated: {midi_url}")  # Debugging
    return jsonify({"midi_url": midi_url}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5002)




