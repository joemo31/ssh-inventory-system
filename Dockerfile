FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

ENV FRONTEND_DIR=/app/frontend \
    DB_PATH=/app/data/inventory.db \
    PYTHONUNBUFFERED=1

RUN mkdir -p /app/data

WORKDIR /app/backend
EXPOSE 5050

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5050/ || exit 1

CMD ["python", "app.py"]
