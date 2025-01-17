
# **Phonetic Tool**

## **Description**
Phonetic Tool est une application permettant de transcrire des fichiers audio en texte (phonèmes), de comparer des phonèmes, et de calculer des scores d'alignement phonétique. Ce projet utilise le modèle **Wav2Vec2-French-Phonemizer**, développé par le CNAM-LMSSC.

### **Lien vers le modèle original :**
[**CNAM-LMSSC Wav2Vec2-French-Phonemizer**](https://huggingface.co/Cnam-LMSSC/wav2vec2-french-phonemizer)

---

## **Méthodes de Test**

### **1. Tester en local avec `app_tkinter.py`**

#### Prérequis
- **Python 3.11** ou version compatible
- Installer les dépendances nécessaires à partir de `requirements.txt` :
  ```bash
  pip install -r requirements.txt
  ```
- Avoir **eSpeak** et ses bibliothèques installés sur votre système.

#### Commandes
1. Lancez le script Tkinter :
   ```bash
   python app_tkinter.py
   ```
---

### **2. Construire l'image Docker à partir du Dockerfile**

#### Prérequis
- **Docker** installé sur votre machine.

#### Étapes
1. Naviguez dans le dossier du projet où se trouve le `Dockerfile`.
2. Construisez l'image Docker :
   ```bash
   docker build -t tkinter-image .
   ```
3. Lancez un conteneur à partir de l'image :
   ```bash
   docker run -it \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --device /dev/snd \
    tkinter-image

   ```
---

### **3. Tester avec l'image Docker préconstruite**

#### Prérequis
- **Docker** installé sur votre machine.
- L'image Docker préconstruite : `tkinter-image.tar`

#### Étapes
1. Importez l'image Docker :
   ```bash
   docker load < tkinter-image.tar
   ```
2. Vérifiez que l'image est correctement importée :
   ```bash
   docker images
   ```
   Vous devriez voir une ligne contenant `tkinter-image`.
3. Lancez un conteneur à partir de l'image :
   ```bash
   docker run -it \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --device /dev/snd \
    tkinter-image

   ```
