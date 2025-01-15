# Utiliser une image Python comme base
FROM python:3.9-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    libespeak1 \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet dans le conteneur
COPY . /app

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port pour Streamlit
EXPOSE 8501

# Commande pour exécuter Streamlit
CMD ["streamlit", "run", "hack.py", "--server.port=8501", "--server.address=0.0.0.0"]
