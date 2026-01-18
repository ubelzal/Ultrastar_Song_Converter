#!/bin/bash

# Supprimer les paquets installés automatiquement mais plus utilisés
sudo apt autoremove -y && sudo apt autoclean -y

# 🛑 Arrêter tous les conteneurs actifs
docker stop $(docker ps -q)

# 🔥 Forcer l’arrêt (si un conteneur est bloqué)
# docker kill $(docker ps -q)

# docker compose run --rm karaoke python bash
docker compose -p karaoke run --rm karaoke python IMPORT_ALL.py

#docker compose -f docker-compose-mfa.yml run --rm mfa python /data/input/MFA.py
docker compose -p mfa -f docker-compose-mfa.yml run --rm mfa python MFA.py
