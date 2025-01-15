
# Test de plusieurs modèles STT et phonémisation avec Docker Compose

Ce projet permet de tester plusieurs modèles d'IA pour la reconnaissance vocale (Speech-to-Text) et la transcription en phonèmes (Speech-to-Phoneme). Chaque modèle possède sa propre licence.

---

## Structure du projet

```
/PING
  ├── Cnam-LMSSCphonemizer-headset-microphone/
  │   ├── hack.py
  │   ├── Dockerfile
  │   ├── requirements.txt
  ├── Cnam-LMSSCwav2vec2-french-phonemizer/
  │   ├── hack.py
  │   ├── Dockerfile
  │   ├── requirements.txt
  ├── docker-compose.yml
  └── README.md
```

---

## Utilisation

### 1. Prérequis
- Installer Docker : [Guide d'installation de Docker](https://docs.docker.com/get-docker/)
- Installer Docker Compose : [Guide d'installation de Docker Compose](https://docs.docker.com/compose/install/)

---

### 2. Construire et lancer les services

- Construisez les images et démarrez les services :
  ```bash
  docker-compose build
  docker-compose up
  ```

- Les outils seront accessibles sur :
  - [http://localhost:8501](http://localhost:8501) pour `headset-microphone`.
  - [http://localhost:8502](http://localhost:8502) pour `wav2vec2-french-phonemizer`.

---

### 3. Arrêter les services
- Pour arrêter les services :
  ```bash
  docker-compose down
  ```

---

## Licences

Chaque modèle utilisé dans ce projet possède sa propre licence. Consultez les fichiers correspondants pour plus de détails.
