import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import wave
import random
import csv
import pyaudio
import torchaudio
import torch
from transformers import AutoModelForCTC, AutoProcessor
from phonemizer import phonemize
from Levenshtein import distance as levenshtein_distance
from phonemizer.backend.espeak.wrapper import EspeakWrapper
import numpy as np

# Configurer le chemin de la bibliothèque espeak
EspeakWrapper.set_library("/usr/lib/aarch64-linux-gnu/libespeak.so.1")

# Créer un dossier pour les fichiers audio enregistrés
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Charger le modèle et le processeur
MODEL_ID = "Cnam-LMSSC/wav2vec2-french-phonemizer"
model = AutoModelForCTC.from_pretrained(MODEL_ID)
processor = AutoProcessor.from_pretrained(MODEL_ID)

# Charger la liste des mots et phonèmes depuis un fichier CSV
def load_words_from_csv(file_path):
    words = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            words.append((row["word"], row["phoneme"]))
    return words

WORDS_CSV = "words.csv"
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
    
    if not trans_phonemes or trans_phonemes == [""]:
        return {}, 0

    scores = {}
    for i, ref_phoneme in enumerate(ref_phonemes):
        min_distance = float("inf")
        for j, trans_phoneme in enumerate(trans_phonemes):
            dist = levenshtein_distance(ref_phoneme, trans_phoneme)
            positional_penalty = abs(i - j)
            total_distance = dist + positional_penalty
            if total_distance < min_distance:
                min_distance = total_distance
        scores[ref_phoneme] = min_distance

    final_score = (
        100
        * len(scores)
        - sum(
            np.array(list(scores.values()))
            / np.array([len(k) + v for k, v in zip(scores.keys(), scores.values())])
        )
        * 100
    ) / len(scores)
    return scores, final_score


class PhoneticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Outil de Transcription Phonétique")
        
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stream = None
        self.recording = False

        # Identifier le périphérique audio
        self.input_device_index = self.get_input_device_index()
        self.init_ui()

    def get_input_device_index(self):
        """Trouve le bon périphérique audio pour l'entrée."""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if "Microphone" in device_info.get("name", "") or "USB Audio" in device_info.get("name", ""):
                return i
        messagebox.showerror("Erreur", "Microphone introuvable. Veuillez vérifier les connexions.")
        self.root.quit()

    def init_ui(self):
        # Mot ou phrase à prononcer
        ttk.Label(self.root, text="Mot ou phrase correcte :", font=("Arial", 14)).pack(pady=10)
        self.word_label = ttk.Label(self.root, text=current_word["text"], font=("Arial", 18, "bold"))
        self.word_label.pack()

        # Bouton pour changer de mot
        ttk.Button(self.root, text="Mot suivant", command=self.next_word).pack(pady=10)

        # Section d'enregistrement
        ttk.Label(self.root, text="Enregistrez un message vocal :", font=("Arial", 14)).pack(pady=10)
        self.record_button = ttk.Button(self.root, text="Démarrer l'enregistrement", command=self.start_recording)
        self.record_button.pack(pady=5)
        self.stop_button = ttk.Button(self.root, text="Arrêter l'enregistrement", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        # Résultats
        self.results_frame = ttk.LabelFrame(self.root, text="Résultats")
        self.results_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        ttk.Label(self.results_frame, text="Transcription correcte :").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.reference_label = ttk.Label(self.results_frame, text="")
        self.reference_label.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(self.results_frame, text="Votre transcription :").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.transcription_label = ttk.Label(self.results_frame, text="")
        self.transcription_label.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(self.results_frame, text="Score d'alignement :").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.score_label = ttk.Label(self.results_frame, text="")
        self.score_label.grid(row=2, column=1, sticky=tk.W)

    def start_recording(self):
        self.recording = True
        self.frames = []
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            input_device_index=self.input_device_index,
            frames_per_buffer=1024
        )

        threading.Thread(target=self.record).start()

    def record(self):
        while self.recording:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Erreur pendant l'enregistrement : {e}")
                break

    def stop_recording(self):
        self.recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        # Sauvegarder l'enregistrement dans un fichier temporaire
        filepath = os.path.join(UPLOAD_FOLDER, "recording.wav")
        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b"".join(self.frames))

        # Transcrire l'audio et afficher les résultats
        self.process_audio(filepath)

    def process_audio(self, filepath):
        try:
            transcription = transcribe_audio(filepath)
            reference = current_word["phonemes"]
            scores, alignment_score = calculate_alignment(reference, transcription)

            self.reference_label.config(text=reference)
            self.transcription_label.config(text=transcription)
            self.score_label.config(text=f"{alignment_score:.2f}%")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

    def next_word(self):
        global current_word
        current_word = get_random_word()
        self.word_label.config(text=current_word["text"])


if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneticApp(root)
    root.mainloop()
