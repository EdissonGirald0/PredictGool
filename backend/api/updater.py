"""
Sistema de actualización de resultados.

Endpoints:
- POST /api/admin/fetch-results: Busca nuevos resultados (validados contra equipos reales)
- POST /api/admin/recalibrate: Recalcula sesgos desde resultados
- POST /api/admin/clean-results: Elimina resultados inválidos (equipos no reconocidos)
- GET /api/admin/bias-status: Estado actual del sistema de sesgo
"""

from fastapi import APIRouter
from utils.data_loader import load_json, save_json, name_to_id

router = APIRouter(prefix="/api/admin", tags=["updater"])


def _load_team_names() -> set:
    """Carga todos los nombres de equipos válidos del torneo."""
    teams = load_json("teams.json") or []
    names = set()
    for t in teams:
        names.add(t["name"])
        names.add(t["id"])
    return names


def _match_team_name(text: str, valid_names: set) -> str | None:
    """Intenta hacer match de un texto contra los nombres válidos de equipos."""
    if text in valid_names:
        return text

    text_lower = text.lower().strip()
    for name in valid_names:
        if name.lower() == text_lower:
            return name

    return None


def _fuzzy_match(text: str, valid_names: set) -> str | None:
    """Match más flexible: ignora palabras extra al final (como 'Stats', 'Beat', etc.)."""
    words = text.split()
    for i in range(len(words), 0, -1):
        candidate = " ".join(words[:i]).strip()
        match = _match_team_name(candidate, valid_names)
        if match:
            return match
    return None


@router.post("/fetch-results")
def fetch_latest_results():
    """
    Busca nuevos resultados. Solo acepta equipos del torneo real.
    Los resultados se validan contra los 48 equipos de teams.json.
    """
    valid_names = _load_team_names()
    existing = load_json("results.json") or []

    existing_keys = set()
    for r in existing:
        key_a = f"{r.get('team_a','')}_{r.get('team_b','')}"
        key_b = f"{r.get('team_b','')}_{r.get('team_a','')}"
        existing_keys.add(key_a.lower())
        existing_keys.add(key_b.lower())

    return {
        "status": "ok",
        "new_results": 0,
        "message": "El scraping automático está deshabilitado. Registra los resultados manualmente en la vista En Vivo.",
        "total": len(existing),
        "valid_teams": len(valid_names),
    }


@router.post("/clean-results")
def clean_invalid_results():
    """
    Elimina resultados que no corresponden a equipos del torneo.
    Útil después de scraping incorrecto.
    """
    valid_names = _load_team_names()
    results = load_json("results.json") or []

    clean = []
    removed = []
    for r in results:
        team_a_ok = _fuzzy_match(r.get("team_a", ""), valid_names) is not None
        team_b_ok = _fuzzy_match(r.get("team_b", ""), valid_names) is not None

        if team_a_ok and team_b_ok:
            if _fuzzy_match(r.get("team_a", ""), valid_names) != r.get("team_a"):
                r["team_a"] = _fuzzy_match(r.get("team_a", ""), valid_names)
            if _fuzzy_match(r.get("team_b", ""), valid_names) != r.get("team_b"):
                r["team_b"] = _fuzzy_match(r.get("team_b", ""), valid_names)
            r["id"] = f"res_{name_to_id(r['team_a'])}_{name_to_id(r['team_b'])}"
            clean.append(r)
        else:
            removed.append(f"{r.get('team_a','?')} {r.get('score_a','?')}-{r.get('score_b','?')} {r.get('team_b','?')}")

    if removed:
        save_json("results.json", clean)

        from models.bias import recalibrate_from_results
        recalibrate_from_results()

    return {
        "status": "ok",
        "original_total": len(results),
        "clean_total": len(clean),
        "removed": len(removed),
        "removed_items": removed,
    }


@router.post("/recalibrate")
def recalibrate_bias():
    from models.bias import recalibrate_from_results
    result = recalibrate_from_results()
    return result


@router.get("/bias-status")
def get_bias_status():
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
