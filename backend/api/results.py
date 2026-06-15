"""Endpoints de resultados (tracking en vivo)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from utils.data_loader import load_json, save_json

router = APIRouter(prefix="/api/results", tags=["results"])


class ResultRequest(BaseModel):
    team_a: str
    team_b: str
    score_a: int
    score_b: int
    stage: str = "group"
    group: str | None = None
    date: str | None = None


@router.get("")
def get_results():
    results = load_json("results.json") or []
    return results


@router.post("")
def add_result(req: ResultRequest):
    results = load_json("results.json") or []

    result_id = f"res_{req.team_a}_{req.team_b}".replace(" ", "_").lower()
    existing = next((r for r in results if r.get("id") == result_id), None)

    entry = {
        "id": result_id,
        "team_a": req.team_a,
        "team_b": req.team_b,
        "score_a": req.score_a,
        "score_b": req.score_b,
        "stage": req.stage,
        "group": req.group,
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
    tid_a = req.team_a.lower().replace(" ", "_")
    tid_b = req.team_b.lower().replace(" ", "_")
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

    return {"status": "ok", "result": entry}


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
