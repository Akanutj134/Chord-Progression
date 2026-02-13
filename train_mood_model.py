import os
import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import LearningRateScheduler
import json

dataset_path = "datasets/cleaned_chords_with_moods.csv"

def load_chord_dataset(filepath):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    required_columns = ["chord sequence", "mood"]

    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing required columns. Found: {df.columns}")

    df = df.dropna()
    df["chord sequence"] = df["chord sequence"].astype(str)
    return df[["chord sequence", "mood"]]

chord_data = load_chord_dataset(dataset_path)

all_chords = set()
for progression in chord_data["chord sequence"]:
    chords = progression.strip().split()
    all_chords.update(chords)

all_chords = sorted(all_chords)
chord_to_index = {chord: i for i, chord in enumerate(all_chords)}
index_to_chord = {i: chord for chord, i in chord_to_index.items()}
vocab_size = len(all_chords)



sequence_length = 3

def preprocess_data(df, target_mood):
    mood_sequences = df[df['mood'] == target_mood]['chord sequence'].tolist()

    chord_tokens = []
    for seq in mood_sequences:
        chord_tokens += seq.split()

    numerical_sequences = [chord_to_index[ch] for ch in chord_tokens if ch in chord_to_index]

    X, y = [], []
    for i in range(len(numerical_sequences) - sequence_length):
        X.append(numerical_sequences[i:i + sequence_length])
        y.append(numerical_sequences[i + sequence_length])

    return np.array(X), to_categorical(y, num_classes=vocab_size)



def plot_training_results(history, mood):
    plt.figure(figsize=(14, 5))

    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title(f'{mood.capitalize()} - Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title(f'{mood.capitalize()} - Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'models/{mood}_training_plot.png')
    plt.show()



moods = chord_data["mood"].unique()
os.makedirs("models", exist_ok=True)
os.makedirs("mappings", exist_ok=True)

for mood in moods:
    print(f"\nTraining model for mood: {mood}")

    X, y = preprocess_data(chord_data, mood)

    if X.shape[0] == 0 or y.shape[0] == 0:
        print(f"Skipping mood '{mood}' due to insufficient data.")
        continue

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

    chords_input = Input(shape=(sequence_length,))
    chords_embedding = Embedding(input_dim=vocab_size, output_dim=128)(chords_input)
    lstm_output = Bidirectional(LSTM(256, dropout=0.3))(chords_embedding)
    dropout = Dropout(0.5)(lstm_output)
    output = Dense(vocab_size, activation='softmax')(dropout)

    model = Model(inputs=chords_input, outputs=output)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    callbacks = [LearningRateScheduler(lambda epoch: 0.001 * (0.95 ** epoch))]
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=50,
        batch_size=16,
        callbacks=callbacks,
        verbose=1
    )

    model.save(f'models/{mood}_chord_model.h5')
    mappings = {"chord_to_index": chord_to_index, "index_to_chord": index_to_chord}
    with open(f'mappings/{mood}_mappings.json', 'w') as f:
        json.dump(mappings, f)

    plot_training_results(history, mood)

    print(f"\nResults for '{mood}':")
    print(f"Final Training Accuracy: {history.history['accuracy'][-1]:.4f}")
    print(f"Final Validation Accuracy: {history.history['val_accuracy'][-1]:.4f}")

print("\n Training completed!")

