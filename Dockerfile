# PredictGool — Dockerfile para Railway
# Backend FastAPI + Frontend Vue.js build estático

FROM python:3.13-slim AS backend

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --omit=dev 2>/dev/null || npm install

COPY frontend/ ./
RUN npm run build

WORKDIR /app
RUN cp -r frontend/dist dist/

WORKDIR /app/backend

RUN mkdir -p data/models

RUN python -c "
from models.generate_dataset import generate_dataset, save_dataset
save_dataset(generate_dataset(1000), 'data/historical_matches.json')
from models.train_xgboost import train_xgboost_model
train_xgboost_model()
" 2>/dev/null || echo "XGBoost training skipped (will run at startup)"

ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "python run_scrapers.py 2>/dev/null; uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
