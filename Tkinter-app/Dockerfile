# Utiliser une image de base légère
FROM python:3.11-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    espeak \
    libespeak1 \
    ffmpeg \
    build-essential \
    libportaudio2 \
    portaudio19-dev \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxrandr2 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    tk \
    && rm -rf /var/lib/apt/lists/*

# Configurer le dossier de travail
WORKDIR /app

# Copier les fichiers de l'application dans le conteneur
COPY requirements.txt /app/requirements.txt
COPY . /app

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Configurer les variables d'environnement
ENV PHONEMIZER_ESPEAK_LIBRARY=/usr/lib/aarch64-linux-gnu/libespeak.so.1
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1

# Commande de démarrage de l'application Tkinter
CMD ["python", "app_tkinter.py"]
