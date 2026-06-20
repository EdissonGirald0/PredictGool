"""Endpoints de resultados (tracking en vivo) con validación."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from utils.data_loader import load_json, save_json, name_to_id

router = APIRouter(prefix="/api/results", tags=["results"])


class ResultRequest(BaseModel):
    team_a: str
    team_b: str
    score_a: int
    score_b: int
    stage: str = "group"
    group: str | None = None
    date: str | None = None


def _get_valid_team_names() -> set:
    teams = load_json("teams.json") or []
    return {t["name"] for t in teams}


def _get_team_group(name: str) -> str | None:
    teams = load_json("teams.json") or []
    for t in teams:
        if t["name"] == name:
            return t["group"]
    return None


@router.get("")
def get_results():
    results = load_json("results.json") or []
    return results


@router.post("")
def add_result(req: ResultRequest):
    valid_names = _get_valid_team_names()

    if req.team_a not in valid_names:
        raise HTTPException(400, f"Equipo no reconocido: '{req.team_a}'. Debe ser uno de los 48 equipos del torneo.")
    if req.team_b not in valid_names:
        raise HTTPException(400, f"Equipo no reconocido: '{req.team_b}'. Debe ser uno de los 48 equipos del torneo.")
    if req.team_a == req.team_b:
        raise HTTPException(400, "Un equipo no puede jugar contra sí mismo.")
    if not (0 <= req.score_a <= 20 and 0 <= req.score_b <= 20):
        raise HTTPException(400, "Los goles deben estar entre 0 y 20.")

    group = req.group or _get_team_group(req.team_a) or ""
    if req.stage == "group" and group:
        group_teams = [t["name"] for t in (load_json("teams.json") or []) if t["group"] == group]
        if req.team_a not in group_teams or req.team_b not in group_teams:
            raise HTTPException(400, f"'{req.team_a}' y '{req.team_b}' no están en el mismo grupo ({group}).")

    result_id = f"res_{name_to_id(req.team_a)}_{name_to_id(req.team_b)}"
    results = load_json("results.json") or []
    existing = next((r for r in results if r.get("id") == result_id), None)

    entry = {
        "id": result_id,
        "team_a": req.team_a,
        "team_b": req.team_b,
        "score_a": req.score_a,
        "score_b": req.score_b,
        "stage": req.stage,
        "group": group,
        "date": req.date or "",
        "played": True,
    }

    if existing:
        idx = results.index(existing)
        results[idx] = entry
    else:
        results.append(entry)

    save_json("results.json", results)

    from models.elo import update_elo
    tid_a = name_to_id(req.team_a)
    tid_b = name_to_id(req.team_b)
    try:
        update_elo(tid_a, tid_b, req.score_a, req.score_b, match_type="world_cup")
    except Exception:
        pass

    from models.bias import record_prediction_outcome
    from models.dixon_coles import predict_match_simple
    from models.elo import win_probability
    try:
        dc_pred = predict_match_simple(tid_a, tid_b)
        elo_pred = win_probability(tid_a, tid_b)
        record_prediction_outcome(tid_a, tid_b, req.score_a, req.score_b, dc_pred, elo_pred)
    except Exception:
        pass

    return {"status": "ok", "result": entry, "action": "updated" if existing else "created"}


@router.get("/stats")
def get_results_stats():
    results = load_json("results.json") or []
    return {
        "total_played": len(results),
        "total_goals": sum(r["score_a"] + r["score_b"] for r in results),
        "home_wins": sum(1 for r in results if r["score_a"] > r["score_b"]),
        "draws": sum(1 for r in results if r["score_a"] == r["score_b"]),
        "away_wins": sum(1 for r in results if r["score_b"] > r["score_a"]),
        "results": results,
    }
