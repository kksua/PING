Construire et exécuter l'image Docker

Construisez l'image Docker :
docker build -t phonetic-tool:cnam-lmssc-phonemizer-headset .

Lancez un conteneur à partir de l'image :
docker run --name phonetic-tool-phonemizer-headset -p 8501:8501 phonetic-tool:cnam-lmssc-phonemizer-headset

-Cela expose l'application Streamlit sur votre machine locale au port 8501.
-Vous pourrez y accéder en ouvrant http://localhost:8501 dans un navigateur.