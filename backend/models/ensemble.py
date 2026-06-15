"""
Ensemble predictivo: combina Elo + Dixon-Coles + XGBoost.

Pesos del ensemble (basados en backtest del Libro Blanco):
- Dixon-Coles: 50% (mejor en marcadores exactos y empates cortos)
- XGBoost: 30% (mejor en patrones no lineales, features estructuradas)
- Elo puro: 20% (mejor en tendencia general, menor varianza)
"""

import pickle
import numpy as np
from pathlib import Path

from models.elo import get_elo, win_probability
from models.dixon_coles import predict_match_simple, predict_scoreline

MODEL_DIR = Path(__file__).resolve().parent.parent / "data" / "models"

_models_cache: dict | None = None

ENSEMBLE_WEIGHTS = {
    "dixon_coles": 0.50,
    "xgboost": 0.30,
    "elo": 0.20,
}


def _load_xgboost_models() -> dict:
    global _models_cache
    if _models_cache is not None:
        return _models_cache

    _models_cache = {}
    for name in ["win", "draw", "away", "goals_home", "goals_away"]:
        path = MODEL_DIR / f"xgboost_{name}.pkl"
        if path.exists():
            with open(path, "rb") as f:
                _models_cache[name] = pickle.load(f)
    return _models_cache


def _build_features(team_a_id: str, team_b_id: str, neutral: bool = True, match_type: str = "world_cup") -> np.ndarray:
    elo_a = get_elo(team_a_id)
    elo_b = get_elo(team_b_id)
    elo_diff = elo_a - elo_b
    home_adv = 0 if neutral else 1

    match_type_map = {"world_cup": 1.0, "qualifier": 0.67, "continental": 0.5, "friendly": 0.33}
    importance = match_type_map.get(match_type, 0.67)

    features = np.array([[
        elo_diff,
        elo_a + elo_b,
        home_adv,
        importance,
        elo_a / max(elo_b, 1),
        elo_a / 2200.0,
        elo_b / 2200.0,
        elo_diff / 400.0,
        max(0.0, min(1.0, (elo_a - 1700) / 500.0)),
    ]])
    return features


def predict_ensemble(
    team_a_id: str,
    team_b_id: str,
    neutral: bool = True,
    match_type: str = "world_cup",
    detailed: bool = False,
) -> dict:
    """
    Predicción ensemble combinando los 3 modelos.

    Returns:
        Dict con win/draw/loss, expected goals, most_likely_score, y top_scorelines si detailed=True
    """
    dc_result = predict_match_simple(team_a_id, team_b_id, neutral)

    elo_result = win_probability(team_a_id, team_b_id, neutral)

    xgb_win = xgb_draw = xgb_loss = 0.0
    xgb_goals_home = xgb_goals_away = 0.0
    try:
        models = _load_xgboost_models()
        if models:
            features = _build_features(team_a_id, team_b_id, neutral, match_type)
            xgb_win = float(models["win"].predict_proba(features)[0, 1])
            xgb_draw = float(models["draw"].predict_proba(features)[0, 1])
            xgb_away = float(models["away"].predict_proba(features)[0, 1])
            total = xgb_win + xgb_draw + xgb_away
            if total > 0:
                xgb_win /= total
                xgb_draw /= total
                xgb_away /= total
            xgb_goals_home = float(models["goals_home"].predict(features)[0])
            xgb_goals_away = float(models["goals_away"].predict(features)[0])
    except Exception:
        pass

    w = ENSEMBLE_WEIGHTS

    final_win = (w["dixon_coles"] * dc_result["win"] + w["xgboost"] * xgb_win + w["elo"] * elo_result["win"])
    final_draw = (w["dixon_coles"] * dc_result["draw"] + w["xgboost"] * xgb_draw + w["elo"] * elo_result["draw"])
    final_loss = (w["dixon_coles"] * dc_result["loss"] + w["xgboost"] * xgb_loss + w["elo"] * elo_result["loss"])

    total = final_win + final_draw + final_loss
    if total > 0:
        final_win /= total
        final_draw /= total
        final_loss /= total

    goals_a = (w["dixon_coles"] * dc_result["expected_goals_a"] + w["xgboost"] * max(0, xgb_goals_home) + w["elo"] * dc_result["expected_goals_a"])
    goals_b = (w["dixon_coles"] * dc_result["expected_goals_b"] + w["xgboost"] * max(0, xgb_goals_away) + w["elo"] * dc_result["expected_goals_b"])

    result = {
        "team_a": team_a_id,
        "team_b": team_b_id,
        "win": round(final_win, 4),
        "draw": round(final_draw, 4),
        "loss": round(final_loss, 4),
        "expected_goals_a": round(goals_a, 3),
        "expected_goals_b": round(goals_b, 3),
        "most_likely_score": dc_result.get("most_likely_score", "?-?"),
        "model_contributions": {
            "dixon_coles": {"win": round(dc_result["win"], 4), "draw": round(dc_result["draw"], 4), "loss": round(dc_result["loss"], 4)},
            "elo": {"win": round(elo_result["win"], 4), "draw": round(elo_result["draw"], 4), "loss": round(elo_result["loss"], 4)},
            "xgboost": {"win": round(xgb_win, 4), "draw": round(xgb_draw, 4), "loss": round(xgb_loss, 4)},
        },
        "ensemble_weights": ENSEMBLE_WEIGHTS,
    }

    if detailed:
        dc_full = predict_scoreline(team_a_id, team_b_id, neutral)
        result["top_scorelines"] = dc_full.get("top_scorelines", [])[:10]

    return result


def sample_match_ensemble(
    team_a_id: str,
    team_b_id: str,
    neutral: bool = True,
    match_type: str = "world_cup",
) -> tuple[int, int]:
    """
    Muestrea un resultado usando el ensemble (para Monte Carlo).
    Usa las probabilidades ensemble + distribución Poisson.
    """
    pred = predict_ensemble(team_a_id, team_b_id, neutral, match_type)
    r = np.random.random()
    if r < pred["win"]:
        ga = np.random.poisson(max(0.3, pred["expected_goals_a"]))
        gb = np.random.poisson(max(0.3, pred["expected_goals_b"]))
        while ga <= gb:
            ga = np.random.poisson(max(0.3, pred["expected_goals_a"]))
    elif r < pred["win"] + pred["draw"]:
        g = np.random.poisson(1.0)
        ga = gb = max(0, g + np.random.choice([-1, 0, 0, 0, 0, 1]))
    else:
        ga = np.random.poisson(max(0.3, pred["expected_goals_a"]))
        gb = np.random.poisson(max(0.3, pred["expected_goals_b"]))
        while gb <= ga:
            gb = np.random.poisson(max(0.3, pred["expected_goals_b"]))
    return int(ga), int(gb)
