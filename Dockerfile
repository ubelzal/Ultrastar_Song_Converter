FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    MFA_ROOT_DIR=/app/models

RUN apt-get update && apt-get install -y \
    ffmpeg \
    sox \
    git \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/models

CMD ["/bin/bash"]
