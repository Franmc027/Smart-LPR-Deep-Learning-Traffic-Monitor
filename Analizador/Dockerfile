FROM python:3.10-slim

# Evitar archivos .pyc y forzar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalamos las librerías de sistema actualizadas para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalamos las librerías de IA
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir ultralytics easyocr opencv-python-headless

COPY brain.py .
RUN mkdir -p /app/capturas

CMD ["python3", "brain.py"] 