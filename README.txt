### Utilisation ####

# Shell interactif
docker compose run --rm karaoke /bin/bash
docker compose run --rm karaoke python --version

# Exécuter un script Python
docker compose run --rm karaoke python votre_script.py

# Utiliser«««««««««««««««««««« MFA pour aligner audio/texte
docker compose run --rm karaoke mfa align input/audio.wav input/transcript.txt output/

# Séparer les stems avec Demucs
docker compose run --rm karaoke python -m demucs input/chanson.mp3

# Télécharger une vidéo YouTube
docker compose run --rm karaoke yt-dlp "URL_YOUTUBE" -o "input/%(title)s.%(ext)s"

# Lancer un script en arrière-plan (mode détaché)
docker compose run -d karaoke python long_script.py

# Voir les logs
docker compose logs -f


### COMMANDES DE GESTION ###

# Construire/reconstruire l'image
docker compose build

# Nettoyer les containers arrêtés
docker compose down

# Voir les containers en cours
docker compose ps
```

**Structure de votre projet recommandée :**
```
UltraStar_Song_Converter/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── input/              # Vos fichiers audio/vidéo source
├── output/             # Résultats générés
├── models/             # Modèles MFA ou autres
└── scripts/            # Vos scripts Python
    └── convert.py