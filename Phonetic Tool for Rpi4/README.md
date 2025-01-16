
# **Phonetic Tool**

## **Description**
Phonetic Tool est une application permettant de transcrire des fichiers audio en texte (phonèmes), de comparer des phonèmes, et de calculer des scores d'alignement phonétique. Ce projet utilise le modèle **Wav2Vec2-French-Phonemizer**, développé par le CNAM-LMSSC.

### **Lien vers le modèle original :**
[**CNAM-LMSSC Wav2Vec2-French-Phonemizer**](https://huggingface.co/Cnam-LMSSC/wav2vec2-french-phonemizer)

---

## **Arborescence du projet**

```
.
├── static/                    # Fichiers statiques (CSS, JS, etc.)
│   ├── style.css              # Feuilles de style pour l'application
│   └── script.js              # Script JS pour les interactions
├── templates/                 # Templates HTML Flask
│   └── index.html             # Page principale de l'application
├── uploads/                   # Répertoire pour stocker les fichiers audio uploadés
├── app.py                     # Code principal de l'application Flask
├── Dockerfile                 # Fichier Docker pour créer l'image du projet
├── certificate.crt            # Certificat SSL pour HTTPS
├── private.key                # Clé privée SSL pour HTTPS
├── requirements.txt           # Dépendances Python nécessaires
├── words.csv                  # Liste des mots et leurs phonèmes
├── baumann_edition_logo.png   # Image incluse dans l'interface
└── phonetic-tool.tar          # Image Docker préconstruite
```

---

## **Méthodes de Test**

### **1. Tester en local avec `app.py`**

#### Prérequis
- **Python 3.11** ou version compatible
- Installer les dépendances nécessaires à partir de `requirements.txt` :
  ```bash
  pip install -r requirements.txt
  ```
- Avoir **eSpeak** et ses bibliothèques installés sur votre système.

#### Commandes
1. Lancez le script Flask :
   ```bash
   python app.py
   ```
2. Accédez à l'application via le navigateur à l'adresse :
   ```
   https://127.0.0.1:5000
   ```

---

### **2. Construire l'image Docker à partir du Dockerfile**

#### Prérequis
- **Docker** installé sur votre machine.

#### Étapes
1. Naviguez dans le dossier du projet où se trouve le `Dockerfile`.
2. Construisez l'image Docker :
   ```bash
   docker build -t phonetic-tool .
   ```
3. Lancez un conteneur à partir de l'image :
   ```bash
   docker run --name phonetic-tool-container -p 5000:5000 phonetic-tool
   ```
4. Accédez à l'application via le navigateur à l'adresse :
   ```
   https://127.0.0.1:5000
   ```

#### Notes
- Si vous rencontrez des problèmes avec le cache Docker, reconstruisez avec :
  ```bash
  docker build --no-cache -t phonetic-tool .
  ```

---

### **3. Tester avec l'image Docker préconstruite**

#### Prérequis
- **Docker** installé sur votre machine.
- L'image Docker préconstruite : `phonetic-tool.tar`

#### Étapes
1. Importez l'image Docker :
   ```bash
   docker load < phonetic-tool.tar
   ```
2. Vérifiez que l'image est correctement importée :
   ```bash
   docker images
   ```
   Vous devriez voir une ligne contenant `phonetic-tool`.
3. Lancez un conteneur à partir de l'image :
   ```bash
   docker run --name phonetic-tool-container -p 5000:5000 phonetic-tool
   ```
4. Accédez à l'application via le navigateur à l'adresse :
   ```
   https://127.0.0.1:5000
   ```

---

## **Dépendances**

- Python 3.11+
- Flask 2.2.2
- Torch 2.5.1
- Torchaudio 2.5.1
- Transformers 4.48.0
- Phonemizer 3.3.0
- Levenshtein 0.26.1
- eSpeak et bibliothèques associées

---

## **Notes Importantes**
- Si vous testez en local, assurez-vous que **eSpeak** est installé et que son chemin est correctement configuré.
- L'application utilise HTTPS. Les fichiers `certificate.crt` et `private.key` sont nécessaires pour un fonctionnement sécurisé.
- Si vous utilisez un navigateur, vous devrez peut-être accepter l'exception de sécurité liée au certificat auto-signé.

---

