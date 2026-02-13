import os
import json
import numpy as np
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from tensorflow.keras.models import load_model
from midiutil import MIDIFile
import sqlite3

def init_db():
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mood TEXT NOT NULL,
        input_sequence TEXT NOT NULL,
        generated_progression TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)
CORS(app)

os.makedirs("mappings", exist_ok=True)
os.makedirs("models", exist_ok=True)

moods = ["happy", "sad", "calm", "excited", "melancholic"]
models = {}
mappings = {}

for mood in moods:
    model_path = f"models/{mood}_chord_model.h5"
    mapping_path = f"mappings/{mood}_mappings.json"

    if os.path.exists(model_path):
        try:
            models[mood] = load_model(model_path)
            print(f"✅ Loaded model for '{mood}'")
        except Exception as e:
            print(f"❌ Error loading model '{mood}': {e}")
    else:
        print(f"❌ Model file '{model_path}' not found.")

    if os.path.exists(mapping_path):
        try:
            with open(mapping_path, 'r') as f:
                mappings[mood] = json.load(f)
            if not mappings[mood]:
                print(f"⚠️ Warning: Mappings file for '{mood}' is empty.")
            elif "chord_to_index" not in mappings[mood] or "index_to_chord" not in mappings[mood]:
                print(f"⚠️ Warning: Mappings for '{mood}' are missing required keys.")
        except Exception as e:
            print(f"❌ Error reading mappings for '{mood}': {e}")
    else:
        print(f"❌ Mappings file '{mapping_path}' not found.")

chord_to_notes = {
    "C": [60, 64, 67], "Cm": [60, 63, 67], "D": [62, 66, 69], "Dm": [62, 65, 69],
    "E": [64, 68, 71], "Em": [64, 67, 71], "F": [65, 69, 72], "Fm": [65, 68, 72],
    "G": [67, 71, 74], "Gm": [67, 70, 74], "A": [69, 73, 76], "Am": [69, 72, 76],
    "B": [71, 75, 78], "Bm": [71, 74, 78]
}

@app.route('/generate-progression', methods=['POST'])
def generate_progression():
    data = request.get_json()
    if not data or 'sequence' not in data or 'steps' not in data or 'mood' not in data:
        return jsonify({"error": "Invalid input data"}), 400

    sequence = data['sequence']
    steps = int(data['steps'])
    mood = data['mood']

    model = models.get(mood)
    mapping = mappings.get(mood)

    if not model or not mapping:
        return jsonify({"error": f"No model or mappings found for mood '{mood}'"}), 400

    chord_to_index = mapping['chord_to_index']
    index_to_chord = {int(k): v for k, v in mapping['index_to_chord'].items()}

    input_sequence = [chord_to_index.get(chord) for chord in sequence if chord in chord_to_index]
    if len(input_sequence) < 3:
        return jsonify({"error": "Input sequence too short"}), 400

    progression = sequence[:]
    try:
        for _ in range(steps):
            input_sequence_np = np.array(input_sequence[-3:]).reshape(1, 3)
            prediction = model.predict(input_sequence_np, verbose=0)
            predicted_chord_index = np.argmax(prediction)
            predicted_chord = index_to_chord.get(predicted_chord_index)
            if not predicted_chord:
                return jsonify({"error": f"Predicted chord index {predicted_chord_index} not found"}), 500
            progression.append(predicted_chord)
            input_sequence.append(predicted_chord_index)
    except Exception as e:
        print(f"❌ Error generating progression for '{mood}': {e}")
        return jsonify({"error": f"Error generating progression: {str(e)}"}), 500

    midi_filename = f"progression_{mood}.mid"
    create_midi(progression, midi_filename)

    try:
        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (mood, input_sequence, generated_progression)
            VALUES (?, ?, ?)
        """, (mood, ','.join(sequence), ','.join(progression)))
        conn.commit()
        conn.close()
    except Exception as db_error:
        print(f"⚠️ SQLite DB error: {db_error}")

    return jsonify({"full_progression": progression, "midi_file": midi_filename})

def create_midi(chords, filename):
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "Chord Progression")
    midi.addTempo(track, time, 120)
    for chord in chords:
        if chord in chord_to_notes:
            for note in chord_to_notes[chord]:
                midi.addNote(track, 0, note, time, 1, 100)
        time += 1
    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)

@app.route('/download-midi/<mood>', methods=['GET'])
def download_midi(mood):
    filename = f"progression_{mood}.mid"
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({"error": "MIDI file not found"}), 404

@app.route('/view-predictions', methods=['GET'])
def view_predictions():
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, mood, input_sequence, generated_progression, timestamp FROM predictions ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/play-note/<note>', methods=['GET'])
def play_note(note):
    """Generate and return a short MIDI file for a single chord (triad) when a piano key is clicked."""
    if note not in chord_to_notes:
        return jsonify({"error": f"Chord '{note}' not recognized."}), 400

    midi_filename = f"static/midi/{note}.mid"
    os.makedirs("static/midi", exist_ok=True)

    if not os.path.exists(midi_filename):
        midi = MIDIFile(1)
        track = 0
        time = 0
        midi.addTrackName(track, time, f"Note {note}")
        midi.addTempo(track, time, 120)
        for pitch in chord_to_notes[note]:
            midi.addNote(track, 0, pitch, time, 1, 100)
        with open(midi_filename, "wb") as output_file:
            midi.writeFile(output_file)

    return send_file(midi_filename, as_attachment=False)


if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    app.run(debug=True)
