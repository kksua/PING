import streamlit as st
import numpy as np
from phonemizer import phonemize
from phonemizer.backend.espeak.wrapper import EspeakWrapper
import torch
import torchaudio
from transformers import Wav2Vec2Processor, AutoModelForCTC
import Levenshtein  # For calculating Levenshtein distance
from transformers import AutoProcessor
from tempfile import NamedTemporaryFile
import random
from PIL import Image
 
EspeakWrapper.set_library('/opt/homebrew/Cellar/espeak/1.48.04_1/lib/libespeak.1.1.48.dylib')
 
words= [
("fais attention a ce que tu dis", "fɛt atɑ̃sjɔ̃ a sə kə ty di"),
("il est temps d'y aller", "il ɛ tɑ̃ di ale"),
("je vais au cinéma ce week-end", "ʒə vɛ o sinema sə wikɛnd"),
("j'ai besoin de vacances", "ʒe bəzwɛ̃ də vakɑ̃s"),
("il est important d'écouter", "il ɛ ɛ̃pɔʁtɑ̃ dekute"),
#("peux-tu m'aider à préparer le dîner ?", "pø ty mɛde a pʁepaʁe lə dine"),
#("il y a un concert ce soir", "il j a ɛ̃ kɔ̃ sɛʁ səswaʁ"),
("il y a beaucoup de choses à faire", "il j a boku də ʃoz a fɛʁ"),
("tu as un joli sourire", "ty a ɛ̃ ʒoli suʁiʁ"),
("admirer", "admiʁe"),
("combiner", "kɔ̃bine"),
("décider", "deside"),
("éclairer", "eklɛʁe"),
("libérer", "libeʁe"),
("connaitre", "konɛtʁ"),
("danser", "dɑ̃se"),
("évoluer", "evolye"),
("expliquer", "ɛksplike"),
("ba", "ba"),
("da", "da"),
("fé", "fe"),
("la", "la"),
#("pa", "pa"),
("sé", "se"),
("za", "za"),
("pal", "pal"),
#("oui", "wi"),
#("bon", "bɔ̃"),
#("uriro","yʁiʁ"),
("valquin", "valkɛ̃"),
("balguet","balɡɛ"),
#("bedibodubo","bedibodybo")
]
 
def load_audio(temp_file_path, target_sample_rate=16000):
    """Load and resample the temporary audio file using torchaudio."""
    try:
        # Load audio using torchaudio
        waveform, sample_rate = torchaudio.load(temp_file_path)
        if sample_rate != target_sample_rate:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
            waveform = resampler(waveform)
        return waveform
    except Exception as e:
        st.error(f"Error loading the audio file: {e}")
        return None

 
 
def transcribe_audio(model, processor, waveform):
    """Transcribe the uploaded audio file using a pre-trained model and convert to phonemes."""
    input_values = processor(waveform.numpy(), return_tensors="pt", sampling_rate=16000).input_values
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)
    return transcription[0].split(" ") if transcription else ""
 
def reference_text_ipa(text, language="fr-fr"):
    phoneme = {word: phoneme for word, phoneme in words}
    return phoneme[text].split(" ")
 
def distance(reference, transcription):
    if transcription == ['']:
        return {}, 0
 
    if not transcription:  # Ensure transcription is not None or empty
        st.error("No valid transcription was generated.")
        return {}, 0
   
    score_dict = {}
   
    for i, pho_r in enumerate(reference):
        min_distance = float('inf')  # Start with a high value
        for j, pho_t in enumerate(transcription):
            dist = Levenshtein.distance(pho_r, pho_t)
            positional_penalty = abs(i - j)  # Penalize based on index difference
            total_distance = dist + positional_penalty
            if total_distance < min_distance:
                min_distance = total_distance  # Keep track of minimum total distance
        score_dict[pho_r] = min_distance
 
    final_score = (100*len(score_dict.keys()) - sum(np.array(list(score_dict.values())) / np.array([len(key)+i for key,i in zip(score_dict.keys(),score_dict.values())]))*100)/len(score_dict.keys())
    return score_dict, final_score
 
def color_alignment_score(score):
    """Returns color based on alignment score ranges."""
    if score < 52:
        return 'red'
    elif score < 70:
        return 'orange'
    else:
        return 'green'
 
 
def select_new_word():
    """Selects a new random word from the list."""
    first_elements = [word[0] for word in words]
    random_selection = random.choice(first_elements)
    return random_selection
 
def main():

 
    # Display the image in the center using Streamlit's layout management
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
 
    st.title("Outil de transcription phonétique")
   
    # Initialize session state
    if 'current_word' not in st.session_state:
        st.session_state.current_word = select_new_word()
    if 'audio_key' not in st.session_state:
        st.session_state.audio_key = 0
   
    # Button to select next word
    if st.button("Mot/Expression suivant(e)"):
        st.session_state.current_word = select_new_word()
        st.session_state.audio_key += 1  # Increment the key to force a new audio widget
   
    # Display current word
    st.write("Veuillez prononcer le mot ou la phrase suivante :")
    st.markdown(f"<h1 style='text-align: center; font-size: 32px; color: rgba(0, 0, 255, 1);'><b>{st.session_state.current_word}</b></h1>", unsafe_allow_html=True)
 
    # Audio recording with a key that changes when the word changes
    audio_value = st.audio_input("Enregistrer un message vocal", key=f"audio_{st.session_state.audio_key}")
 
    if audio_value is not None:
        with NamedTemporaryFile(suffix=".wav", delete=False) as temp:
            temp.write(audio_value.getvalue())
            temp.seek(0)
            model_id = "Cnam-LMSSC/phonemizer_headset_microphone"
            model = AutoModelForCTC.from_pretrained(model_id)
            processor = AutoProcessor.from_pretrained(model_id)
 
            waveform = load_audio(temp.name)
            if waveform is not None:
                transcription = transcribe_audio(model, processor, waveform)
               
                # Display transcription
                st.markdown(f"<h2 style='text-align: center; font-size: 24px;'>{' '.join(transcription)}</h2>", unsafe_allow_html=True)
 
                reference_phonemes = reference_text_ipa(st.session_state.current_word.lower())
                individual_scores, alignment_score = distance(transcription=transcription, reference=reference_phonemes)
               
                st.write("Normalize based on the length of the word:")
               
                scores_with_color = []
                for phoneme, score in individual_scores.items():
                    score = 100 - (score / (score + len(phoneme))) * 100
                    color = color_alignment_score(score)
                    scores_with_color.append(f"<span style='font-size:18px; color:{color};'>{phoneme}: {score:.2f}</span>")
               
                st.markdown(f"<div style='overflow-x: auto; white-space: nowrap;'>{' | '.join(scores_with_color)}</div>", unsafe_allow_html=True)
 
                color = color_alignment_score(alignment_score)
                st.markdown(f"<h3 style='color:{color};'>Score total d'alignement : {alignment_score}</h3>", unsafe_allow_html=True)
 
if __name__ == "__main__":
    main()