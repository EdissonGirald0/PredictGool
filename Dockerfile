# PredictGool — Dockerfile multi-stage para Railway
FROM node:22-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci 2>/dev/null || npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim AS runtime
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir \
    fastapi==0.115.6 \
    "uvicorn[standard]==0.34.0" \
    numpy==2.2.3 \
    scipy==1.15.2 \
    pandas==2.2.3 \
    httpx==0.28.1 \
    pydantic==2.10.5 \
    python-dotenv==1.1.0 \
    bcrypt==4.0.1

WORKDIR /app
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

RUN mkdir -p /app/backend/data /app/backend/data/models

ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "\
  cd /app/backend && \
  if [ -f data/teams.json ]; then \
    if python3 -c \"import json; t=json.load(open('data/teams.json')); exit(0 if any(x['name']=='México' for x in t) else 1)\" 2>/dev/null; then \
      echo '✅ Datos en español, preservando...'; \
      python run_scrapers.py 2>/dev/null || true; \
    else \
      echo '⚠️  Regenerando datos en español...'; \
      python apply_real_data.py --force 2>/dev/null || true; \
    fi; \
  else \
    python apply_real_data.py --force 2>/dev/null || true; \
  fi && \
  exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} \
"]
