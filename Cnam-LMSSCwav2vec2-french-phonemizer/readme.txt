Construire et exécuter l'image Docker

Construisez l'image Docker :
docker build -t phonetic-tool:cnam-lmssc-wav2vec2-french-phonemizer .
ou pour rebuild après nettoyage : docker build --no-cache -t phonetic-tool:cnam-lmssc-wav2vec2-french-phonemizer .

Lancez un conteneur à partir de l'image :
docker run --name phonetic-tool-wav2vec2 -p 8502:8502 phonetic-tool:cnam-lmssc-wav2vec2-french-phonemizer

-Cela expose l'application Streamlit sur votre machine locale au port 8502.
-Vous pourrez y accéder en ouvrant http://localhost:8502 dans un navigateur.