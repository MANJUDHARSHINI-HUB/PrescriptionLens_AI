# PrescriptionLens AI - Single Dockerfile used by both services via docker-compose
FROM python:3.11-slim

# System dependencies required by OpenCV and EasyOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

EXPOSE 8000 8501

# Default command is overridden per-service in docker-compose.yml
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
