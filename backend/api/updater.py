"""
Sistema de actualización automática de resultados.

Fase 3: Scraping programado + ajuste de sesgo en tiempo real.

Endpoints:
- POST /api/admin/fetch-results: Intenta scrapear nuevos resultados
- POST /api/admin/recalibrate: Recalcula sesgos desde resultados
- GET /api/admin/bias-status: Estado actual del sistema de sesgo
"""

import httpx
import re
import json
from fastapi import APIRouter
from utils.data_loader import load_json, save_json

router = APIRouter(prefix="/api/admin", tags=["updater"])

SOURCES = [
    {
        "name": "Wikipedia-es",
        "url": "https://es.wikipedia.org/wiki/Copa_Mundial_de_F%C3%BAtbol_de_2026",
        "type": "wikipedia",
    },
    {
        "name": "Wikipedia-en-mobile",
        "url": "https://en.m.wikipedia.org/wiki/2026_FIFA_World_Cup",
        "type": "wikipedia",
    },
    {
        "name": "Google-matches",
        "url": "https://www.google.com/search?q=2026+world+cup+results+today&hl=en",
        "type": "google",
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


@router.post("/fetch-results")
def fetch_latest_results():
    """
    Intenta obtener nuevos resultados de múltiples fuentes.
    Compara con results.json y agrega solo los nuevos.
    """
    existing = load_json("results.json") or []
    existing_keys = set()
    for r in existing:
        key_a = f"{r.get('team_a','')}_{r.get('team_b','')}"
        key_b = f"{r.get('team_b','')}_{r.get('team_a','')}"
        existing_keys.update([key_a.lower(), key_b.lower()])

    new_results = []
    for source in SOURCES:
        try:
            fetched = _scrape_source(source)
            if not fetched:
                continue
            for r in fetched:
                key = f"{r['team_a']}_{r['team_b']}".lower()
                if key not in existing_keys:
                    r["id"] = key.replace(" ", "_")
                    r["stage"] = "group"
                    r["date"] = r.get("date", "2026-06-15")
                    r["played"] = True
                    new_results.append(r)
                    existing_keys.add(key)
        except Exception:
            continue

    if new_results:
        for r in new_results:
            existing.append(r)
        save_json("results.json", existing)

        from models.elo import update_elo
        for r in new_results:
            tid_a = r["team_a"].lower().replace(" ", "_")
            tid_b = r["team_b"].lower().replace(" ", "_")
            try:
                update_elo(tid_a, tid_b, r["score_a"], r["score_b"], match_type="world_cup")
            except Exception:
                pass

        _update_standings_and_fixtures()

        return {
            "status": "ok",
            "new_results": len(new_results),
            "results": new_results,
            "total": len(existing),
        }

    return {
        "status": "ok",
        "new_results": 0,
        "message": "No se encontraron nuevos resultados",
        "total": len(existing),
    }


@router.post("/recalibrate")
def recalibrate_bias():
    """Recalcula todo el sistema de sesgo desde cero."""
    from models.bias import recalibrate_from_results
    result = recalibrate_from_results()
    return result


@router.get("/bias-status")
def get_bias_status():
    """Estado actual del sistema de sesgo/bias."""
    from models.bias import get_bias_state
    state = get_bias_state()
    return {
        "total_tracked": state["total_tracked"],
        "ensemble_weights": state["ensemble_weights"],
        "model_performance": {
            "dixon_coles": {
                "accuracy": round(
                    state["model_performance"]["dixon_coles"]["correct"] /
                    max(state["model_performance"]["dixon_coles"]["total"], 1), 4
                ),
                "total": state["model_performance"]["dixon_coles"]["total"],
            },
            "elo": {
                "accuracy": round(
                    state["model_performance"]["elo"]["correct"] /
                    max(state["model_performance"]["elo"]["total"], 1), 4
                ),
                "total": state["model_performance"]["elo"]["total"],
            },
        },
        "teams_with_form": len(state.get("team_form", {})),
        "global_stats": state.get("global_stats", {}),
        "confidence_thresholds": state.get("confidence_thresholds", {}),
        "updated_at": state.get("updated_at", ""),
    }


def _scrape_source(source: dict) -> list[dict]:
    """Intenta scrapear una fuente de resultados."""
    try:
        resp = httpx.get(source["url"], timeout=20, follow_redirects=True, headers=HEADERS)
        if resp.status_code != 200:
            return []
        text = resp.text
    except Exception:
        return []

    return _extract_results_from_text(text)


def _extract_results_from_text(text: str) -> list[dict]:
    """Extrae resultados de partidos del texto HTML usando regex."""
    results = []
    seen = set()

    pattern = re.compile(
        r'(?P<team_a>[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+(?:\s+(?:and\s+)?[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)*?)\s*'
        r'(?:<[^>]+>)*\s*'
        r'(?P<score_a>\d+)\s*[–\-—]\s*(?P<score_b>\d+)\s*'
        r'(?:<[^>]+>)*\s*'
        r'(?P<team_b>[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+(?:\s+(?:and\s+)?[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)*)',
    )

    for match in pattern.finditer(text):
        team_a = match.group("team_a").strip()
        team_b = match.group("team_b").strip()
        score_a = int(match.group("score_a"))
        score_b = int(match.group("score_b"))

        if len(team_a) < 3 or len(team_b) < 3:
            continue
        if team_a.lower() in ("vs", "contra", "and", "the", "for"):
            continue
        if team_b.lower() in ("vs", "contra", "and", "the", "for"):
            continue

        key = f"{team_a}_{team_b}".lower()
        if key in seen:
            continue
        seen.add(key)

        if score_a < 0 or score_b < 0 or score_a > 15 or score_b > 15:
            continue

        results.append({
            "team_a": team_a,
            "team_b": team_b,
            "score_a": score_a,
            "score_b": score_b,
        })

    return results


def _update_standings_and_fixtures():
    """Actualiza elo_ratings.json con los resultados más recientes."""
    try:
        from models.bias import recalibrate_from_results
        recalibrate_from_results()
    except Exception:
        pass
