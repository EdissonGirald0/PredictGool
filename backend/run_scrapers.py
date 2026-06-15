#!/usr/bin/env python3
"""
Orquestador de scraping: aplica datos reales del Mundial 2026 y puebla data/*.json
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.data_loader import load_json


def run_all():
    print("=" * 60)
    print("  PREDICTGOOL - Pipeline de Datos Mundial 2026")
    print("=" * 60)

    print("\n[1/1] Aplicando datos reales del Mundial 2026...")
    result = subprocess.run(
        [sys.executable, "apply_real_data.py"],
        capture_output=True, text=True, timeout=30,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)

    teams = load_json("teams.json") or []
    groups = load_json("groups.json") or []
    fixtures = load_json("fixtures.json") or []
    results = load_json("results.json") or []
    elo = load_json("elo_ratings.json") or {}

    print(f"  ✅ {len(teams)} equipos | {len(groups)} grupos | {len(fixtures)} fixtures | {len(results)} resultados | {len(elo.get('ratings', {}))} ratings Elo")
    print("=" * 60)


if __name__ == "__main__":
    run_all()
