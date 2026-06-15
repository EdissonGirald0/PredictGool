"""Endpoints de predicción de partidos."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.ensemble import predict_ensemble
from models.tournament import simulate_single_match

router = APIRouter(prefix="/api", tags=["predict"])


class PredictRequest(BaseModel):
    team_a: str
    team_b: str
    neutral: bool = True
    stage: str = "group"
    detailed: bool = False


class ScorelineItem(BaseModel):
    goals_a: int
    goals_b: int
    probability: float


class PredictResponse(BaseModel):
    team_a: str
    team_b: str
    win: float
    draw: float
    loss: float
    expected_goals_a: float
    expected_goals_b: float
    most_likely_score: str
    top_scorelines: list[ScorelineItem] = []


@router.post("/predict", response_model=PredictResponse)
def predict_match(req: PredictRequest):
    if not req.team_a or not req.team_b:
        raise HTTPException(400, "team_a y team_b son requeridos")

    if req.team_a == req.team_b:
        raise HTTPException(400, "Los equipos deben ser diferentes")

    result = predict_ensemble(req.team_a, req.team_b, req.neutral, detailed=req.detailed)
    scorelines = [
        ScorelineItem(goals_a=s["goals_a"], goals_b=s["goals_b"], probability=s["probability"])
        for s in result.get("top_scorelines", [])[:10]
    ]
    return PredictResponse(
        team_a=result["team_a"],
        team_b=result["team_b"],
        win=result["win"],
        draw=result["draw"],
        loss=result["loss"],
        expected_goals_a=result["expected_goals_a"],
        expected_goals_b=result["expected_goals_b"],
        most_likely_score=result["most_likely_score"],
        top_scorelines=scorelines,
    )


class SimulateMatchRequest(BaseModel):
    team_a: str
    team_b: str
    n: int = 1000


@router.post("/predict/simulate")
def predict_match_monte_carlo(req: SimulateMatchRequest):
    n = min(max(req.n, 100), 10000)
    result = simulate_single_match(req.team_a, req.team_b, n)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result
