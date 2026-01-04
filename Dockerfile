FROM mmcauliffe/montreal-forced-aligner:latest

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    MFA_ROOT_DIR=/app/models

USER root

# Installer les dépendances système supplémentaires
RUN apt-get update && apt-get install -y \
    git \
    wget \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier requirements.txt
COPY requirements.txt .

# Installer les packages Python supplémentaires
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Créer le dossier models et donner les permissions
RUN mkdir -p /app/models && chown -R 1000:1000 /app/models

# Télécharger les modèles **en root**, mais dans MFA_ROOT_DIR
RUN MFA_ROOT_DIR=/app/models mfa model download acoustic french_mfa && \
    MFA_ROOT_DIR=/app/models mfa model download dictionary french_mfa && \
    MFA_ROOT_DIR=/app/models mfa model download acoustic english_mfa && \
    MFA_ROOT_DIR=/app/models mfa model download dictionary english_mfa

# Vérifier que tout est installé
RUN MFA_ROOT_DIR=/app/models mfa model list acoustic && \
    MFA_ROOT_DIR=/app/models mfa model list dictionary

# Vérifier les installations
RUN python --version && \
    mfa version && \
    ffmpeg -version

# Donner les permissions à l'utilisateur existant
RUN chown -R 1000:1000 /app

# Utiliser l'utilisateur existant
USER 1000

# Ouvrir un shell au lancement
CMD ["/bin/bash"]