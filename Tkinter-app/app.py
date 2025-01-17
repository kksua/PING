from flask import Flask, render_template, request, jsonify
import os
import random
import csv
import torchaudio
import torch
from transformers import AutoModelForCTC, AutoProcessor
from phonemizer import phonemize
from Levenshtein import distance as levenshtein_distance
import numpy as np
from phonemizer.backend.espeak.wrapper import EspeakWrapper

# Configurer le chemin de la biblioth�que espeak
EspeakWrapper.set_library("/usr/lib/aarch64-linux-gnu/libespeak.so.1")

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Charger le modéle et le processeur
MODEL_ID = "Cnam-LMSSC/wav2vec2-french-phonemizer"
model = AutoModelForCTC.from_pretrained(MODEL_ID)
processor = AutoProcessor.from_pretrained(MODEL_ID)

# Charger la liste des mots et phonémes depuis un fichier CSV
def load_words_from_csv(file_path):
    words = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            words.append((row['word'], row['phoneme']))
    return words

WORDS_CSV = 'words.csv'
words = load_words_from_csv(WORDS_CSV)
current_word = {"text": words[0][0], "phonemes": words[0][1]}


def get_random_word():
    """Sélectionne un mot ou une phrase au hasard."""
    word, phonemes = random.choice(words)
    return {"text": word, "phonemes": phonemes}


def transcribe_audio(filepath):
    """Transcrit un fichier audio en texte."""
    waveform, sample_rate = torchaudio.load(filepath)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)

    input_values = processor(waveform.numpy(), return_tensors="pt", sampling_rate=16000).input_values
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)
    return transcription[0].lower()


def calculate_alignment(reference, transcription):
    """Calcule le score d'alignement phonétique."""
    ref_phonemes = reference.split()
    trans_phonemes = phonemize(transcription, language="fr-fr", backend="espeak").split()
    
    if not trans_phonemes or trans_phonemes == ['']:
        return {}, 0

    scores = {}
    for i, ref_phoneme in enumerate(ref_phonemes):
        min_distance = float('inf')
        for j, trans_phoneme in enumerate(trans_phonemes):
            dist = levenshtein_distance(ref_phoneme, trans_phoneme)
            positional_penalty = abs(i - j)
            total_distance = dist + positional_penalty
            if total_distance < min_distance:
                min_distance = total_distance
        scores[ref_phoneme] = min_distance

    final_score = (100 * len(scores) - sum(np.array(list(scores.values())) / np.array([len(k) + v for k, v in zip(scores.keys(), scores.values())])) * 100) / len(scores)
    return scores, final_score


@app.route('/')
def index():
    return render_template('index.html', word=current_word["text"])


@app.route('/next', methods=['POST'])
def next_word():
    global current_word
    current_word = get_random_word()
    return jsonify({"word": current_word["text"]})


@app.route('/upload', methods=['POST'])
def upload_audio():
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({"error": "No audio file received"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(filepath)

    # Transcrire et comparer
    transcription = transcribe_audio(filepath)
    reference = current_word["phonemes"]
    scores, alignment_score = calculate_alignment(reference, transcription)

    return jsonify({
        "transcription": transcription,
        "alignment_score": alignment_score,
        "reference": current_word["phonemes"], 
        "scores": [{"phoneme": k, "score": 100 - (v / (v + len(k))) * 100} for k, v in scores.items()]
    })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=('certificate.crt', 'private.key'))
