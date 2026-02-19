FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalamos dependencias y Node.js de repositorio oficial (más estable para yt-dlp)
RUN apt-get update && apt-get install -y \
    python3 python3-pip libgl1-mesa-glx libglib2.0-0 ffmpeg curl \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalamos librerías y nos aseguramos de que yt-dlp esté al día
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir yt-dlp opencv-python-headless

COPY . .

RUN mkdir -p /app/capturas

# Actualizamos yt-dlp cada vez que arranca el contenedor para evitar bloqueos de YouTube
ENTRYPOINT ["/bin/bash", "-c", "pip3 install --upgrade yt-dlp && python3 app/main.py"]