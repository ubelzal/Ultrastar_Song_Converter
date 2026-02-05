#!/bin/bash

ssh -T git@github.com && \
git remote -v && \
git status && \
git add . && \
read -p "Commit message: " msg && \
git commit -m "$msg" && \
git push --set-upstream origin $(git branch --show-current)

# ✅ Comment ça marche
# ssh -T git@github.com → Vérifie que ta clé SSH est reconnue.

# git remote -v → Affiche ton remote actuel.

# git status → Montre les fichiers modifiés.

# git add . → Prépare tous les fichiers modifiés pour le commit.

# read -p "Commit message: " → Te demande un message de commit interactif.

# git commit -m "$msg" → Crée le commit.

# git push --set-upstream origin $(git branch --show-current) → Pousse ta branche actuelle et définit le suivi si nécessaire.