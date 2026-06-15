#!/usr/bin/env bash
# start.sh — Inicia backend (FastAPI) + frontend (Vite dev server)
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "⚽ PredictGool — Iniciando servidores"
echo "====================================="

ACTIVATE=""
if [ -f "$PROJECT_DIR/../venv/bin/activate" ]; then
  ACTIVATE="$PROJECT_DIR/../venv/bin/activate"
elif [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
  ACTIVATE="$PROJECT_DIR/venv/bin/activate"
fi

cleanup() {
  echo ""
  echo "🛑 Deteniendo servidores..."
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM

echo ""
echo "📦 [1/2] Iniciando backend (FastAPI) en http://localhost:8000 ..."
if [ -n "$ACTIVATE" ]; then
  source "$ACTIVATE"
fi
cd "$PROJECT_DIR/backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
sleep 2

echo ""
echo "🎨 [2/2] Iniciando frontend (Vite) en http://localhost:5173 ..."
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "====================================="
echo "✅ PredictGool iniciado"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener"
echo "====================================="

wait
