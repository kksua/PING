# Utiliser une image de base légére
FROM python:3.11-slim

# Installer les dépendances systéme nécessaires
RUN apt-get update && apt-get install -y \
    espeak \
    libespeak1 \
    ffmpeg \
    build-essential \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*


# Copier les fichiers de l'application dans le conteneur
WORKDIR /app
COPY . /app

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Configurer les variables d'environnement
ENV PHONEMIZER_ESPEAK_LIBRARY=/usr/lib/aarch64-linux-gnu/libespeak.so.1

# Exposer le port pour Flask
EXPOSE 5000

# Lancer l'application Flask avec SSL
CMD ["python", "app.py"]
