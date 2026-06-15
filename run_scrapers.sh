#!/usr/bin/env bash
# run_scrapers.sh — Ejecuta el pipeline completo de scraping
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"

echo "🔍 PredictGool — Pipeline de Scraping"
echo "====================================="

if [ -f "../venv/bin/activate" ]; then
  source "../venv/bin/activate"
elif [ -f "../../venv/bin/activate" ]; then
  source "../../venv/bin/activate"
fi

python run_scrapers.py

echo ""
echo "✅ Datos generados en backend/data/"
echo "   - teams.json       (48 equipos)"
echo "   - groups.json      (12 grupos)"
echo "   - fixtures.json    (104 partidos)"
echo "   - elo_ratings.json (ratings Elo)"
echo "   - results.json     (resultados)"
