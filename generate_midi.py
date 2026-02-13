import os
from midiutil import MIDIFile

#MIDI directory
MIDI_FOLDER = "static/midi"
os.makedirs(MIDI_FOLDER, exist_ok=True)

def create_midi(chords, filename):
    """Generates a MIDI file from a list of chords."""
    
    chord_to_notes = {
        # Major chords
        "C": [60, 64, 67],  # C major
        "D": [62, 66, 69],  # D major
        "E": [64, 68, 71],  # E major
        "F": [65, 69, 72],  # F major
        "G": [67, 71, 74],  # G major
        "A": [69, 73, 76],  # A major
        "B": [71, 75, 78],  # B major

        # Minor chords
        "Cm": [60, 63, 67],  # C minor
        "Dm": [62, 65, 69],  # D minor
        "Em": [64, 67, 71],  # E minor
        "Fm": [65, 68, 72],  # F minor
        "Gm": [67, 70, 74],  # G minor
        "Am": [69, 72, 76],  # A minor
        "Bm": [71, 74, 78],  # B minor
    }

    
    midi = MIDIFile(1)
    track = 0
    midi.addTrackName(track, 0, "Chord Progression")
    midi.addTempo(track, 0, 120)  # Set tempo to 120 BPM
    time = 0

    # Generate chords
    for chord in chords:
        if chord not in chord_to_notes:
            print(f"⚠️ Warning: Chord '{chord}' not found in mappings!")
            continue  # Skip unknown chords

        notes = chord_to_notes[chord]
        print(f"🎵 Generating MIDI for chord: {chord} → Notes: {notes}")

        for note in notes:
            midi.addNote(track, 0, note, time, 1, 100)  # Add note with 1-beat duration
        
        time += 1  # Move to the next beat

    # Save the MIDI file
    midi_filepath = os.path.join(MIDI_FOLDER, filename)

    with open(midi_filepath, "wb") as output_file:
        midi.writeFile(output_file)

    print(f"✅ MIDI file saved at: {midi_filepath}")

    return midi_filepath  # Returns the file path for Flask to use

# Example Usage:
if __name__ == "__main__":
    create_midi(["C", "G", "Am", "F"], "chord_progression.mid")
