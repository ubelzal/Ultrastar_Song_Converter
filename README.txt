### Utilisation ####

  # Construire/reconstruire l'image
  docker build -t karaoke:latest .

  # Executer la mise a jour de la base de donnée
  docker compose run --rm karaoke python /app/input/IMPORT_ALL.py

  # Shell interactif
  docker compose run --rm karaoke /bin/bash


### MFA ###
  
  # Lancer
  docker compose -f docker-compose-mfa.yml run --rm mfa-init
  docker compose -f docker-compose-mfa.yml run --rm mfa bash

  # Arrêter
  docker compose -f docker-compose-mfa.yml down

  # Voir les logs
  docker compose -f docker-compose-mfa.yml logs

  # Rebuild (si nécessaire)
  docker compose -f docker-compose-mfa.yml build



### NOTES ###

# Shell interactif
docker compose run --rm karaoke /bin/bash
docker compose run --rm karaoke python --version

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
docker build -t karaoke:latest .

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

#💡 En résumé
#Dockerfile : comment construire l’image
#docker-compose.yml : comment lancer le container et le configurer
#Souvent, tu as les deux ensemble : Dockerfile construit l’image, Compose l’exécute avec tous les réglages.