from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

#  Hardcoded quiz data
music_quiz_questions = [
    {"question": "What is the I-IV-V-I progression in C Major?", "options": ["C-F-G-C", "D-G-A-D", "E-A-B-E", "F-Bb-C-F"], "correct": "C-F-G-C"},
    {"question": "Which chord is the relative minor of C Major?", "options": ["D minor", "A minor", "E minor", "B minor"], "correct": "A minor"},
    {"question": "What is the V chord in G Major?", "options": ["D Major", "C Major", "F Major", "E Minor"], "correct": "D Major"},
    {"question": "Which note is the third in a B Major chord?", "options": ["E", "D#", "F#", "G#"], "correct": "D#"},
    {"question": "What does a dominant 7th chord contain?", "options": ["Root, Major Third, Perfect Fifth, Minor Seventh", "Root, Minor Third, Perfect Fifth, Minor Seventh", "Root, Major Third, Perfect Fifth, Major Seventh", "Root, Major Third, Augmented Fifth, Minor Seventh"], "correct": "Root, Major Third, Perfect Fifth, Minor Seventh"},
]

@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')

@app.route('/get-music-question')
def get_music_question():
    question = random.choice(music_quiz_questions)
    return jsonify(question)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
