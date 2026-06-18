"""
Sistema de sesgo/bias dinámico basado en resultados reales.

Aprende de cada resultado registrado y ajusta:
1. Pesos del ensemble según accuracy reciente de cada modelo
2. Factor de forma por equipo (rendimiento real vs esperado)
3. Confianza de predicción basada en patrones históricos

El sistema persiste en data/bias_state.json para mantener el aprendizaje entre reinicios.
"""

import math
from datetime import datetime

from utils.data_loader import load_json, save_json, name_to_id

BIAS_FILE = "bias_state.json"
WINDOW_SIZE = 20


def get_bias_state() -> dict:
    return load_json(BIAS_FILE) or _init_state()


def _init_state() -> dict:
    return {
        "version": 2,
        "updated_at": "",
        "total_tracked": 0,
        "model_performance": {
            "dixon_coles": {"correct": 0, "total": 0, "recent": []},
            "elo": {"correct": 0, "total": 0, "recent": []},
        },
        "team_form": {},
        "ensemble_weights": {"dixon_coles": 0.50, "xgboost": 0.30, "elo": 0.20},
        "global_stats": {
            "home_win_rate": 0.0,
            "draw_rate": 0.0,
            "away_win_rate": 0.0,
            "avg_goals_per_match": 0.0,
        },
        "confidence_thresholds": {
            "high": 0.70,
            "medium": 0.50,
            "low": 0.35,
        },
    }


def save_bias_state(state: dict) -> None:
    state["updated_at"] = datetime.now().isoformat()
    save_json(BIAS_FILE, state)


def record_prediction_outcome(
    team_a_id: str,
    team_b_id: str,
    score_a: int,
    score_b: int,
    dc_pred: dict,
    elo_pred: dict,
) -> dict:
    """
    Registra el resultado real y actualiza el sesgo.

    Args:
        team_a_id, team_b_id: IDs de los equipos
        score_a, score_b: goles reales
        dc_pred: predicción de Dixon-Coles {win, draw, loss, expected_goals_a, expected_goals_b}
        elo_pred: predicción de Elo {win, draw, loss}

    Returns:
        Estado actualizado del bias
    """
    state = get_bias_state()

    actual_result = _determine_result(score_a, score_b)
    dc_result = _determine_prediction(dc_pred)
    elo_result = _determine_prediction(elo_pred)

    _track_model(state, "dixon_coles", dc_result == actual_result)
    _track_model(state, "elo", elo_result == actual_result)
    _update_team_form(state, team_a_id, team_b_id, score_a, score_b, dc_pred)
    _update_global_stats(state, score_a, score_b, actual_result)
    _recalibrate_weights(state)

    state["total_tracked"] += 1
    save_bias_state(state)
    return state


def get_dynamic_weights() -> dict:
    """Pesos del ensemble ajustados por rendimiento real."""
    state = get_bias_state()
    return state.get("ensemble_weights", {"dixon_coles": 0.50, "xgboost": 0.30, "elo": 0.20})


def get_team_form_factor(team_id: str) -> float:
    """
    Factor de forma del equipo.
    > 0: rindiendo mejor de lo esperado
    < 0: rindiendo peor de lo esperado
    0: neutral (sin datos)
    """
    state = get_bias_state()
    team_form = state.get("team_form", {}).get(team_id, {})
    return team_form.get("form_factor", 0.0)


def get_confidence_level(win_prob: float, draw_prob: float) -> str:
    """Nivel de confianza de la predicción basado en thresholds calibrados."""
    state = get_bias_state()
    thresholds = state.get("confidence_thresholds", {})
    max_prob = max(win_prob, draw_prob)

    if max_prob >= thresholds.get("high", 0.70):
        return "high"
    elif max_prob >= thresholds.get("medium", 0.50):
        return "medium"
    return "low"


def get_global_stats() -> dict:
    state = get_bias_state()
    return state.get("global_stats", {})


def apply_team_bias(team_a_id: str, team_b_id: str, dc_win: float, dc_draw: float, dc_loss: float) -> dict:
    """
    Aplica el factor de forma de cada equipo a las probabilidades base.
    Si un equipo está en mejor forma de lo esperado, se incrementa su probabilidad.
    """
    form_a = get_team_form_factor(team_a_id)
    form_b = get_team_form_factor(team_b_id)
    form_diff = form_a - form_b

    bias_strength = 0.08
    adjustment = form_diff * bias_strength

    adj_win = max(0.02, min(0.92, dc_win + adjustment))
    adj_loss = max(0.02, min(0.92, dc_loss - adjustment))
    adj_draw = 1.0 - adj_win - adj_loss

    if adj_draw < 0.05:
        adj_draw = 0.05
        total = adj_win + adj_loss
        if total > 0:
            adj_win /= (total / 0.95)
            adj_loss /= (total / 0.95)

    return {"win": round(adj_win, 4), "draw": round(adj_draw, 4), "loss": round(adj_loss, 4)}


def recalibrate_from_results() -> dict:
    """Recalcula todo el estado de sesgo desde los resultados registrados."""
    results = load_json("results.json") or []
    if not results:
        return {"status": "ok", "message": "No hay resultados para calibrar"}

    from models.elo import win_probability
    from models.dixon_coles import predict_match_simple

    state = _init_state()

    for r in results:
        if not r.get("played"):
            continue
        tid_a = name_to_id(r["team_a"])
        tid_b = name_to_id(r["team_b"])

        try:
            dc_pred = predict_match_simple(tid_a, tid_b)
            elo_pred = win_probability(tid_a, tid_b)
        except Exception:
            continue

        actual_result = _determine_result(r["score_a"], r["score_b"])
        dc_result = _determine_prediction(dc_pred)
        elo_result = _determine_prediction(elo_pred)

        _track_model(state, "dixon_coles", dc_result == actual_result)
        _track_model(state, "elo", elo_result == actual_result)
        _update_team_form(state, tid_a, tid_b, r["score_a"], r["score_b"], dc_pred)
        _update_global_stats(state, r["score_a"], r["score_b"], actual_result)
        state["total_tracked"] += 1

    _recalibrate_weights(state)
    _calibrate_confidence_thresholds(state)
    save_bias_state(state)

    return {
        "status": "ok",
        "total_tracked": state["total_tracked"],
        "weights": state["ensemble_weights"],
        "dc_accuracy": _model_accuracy(state, "dixon_coles"),
        "elo_accuracy": _model_accuracy(state, "elo"),
        "teams_tracked": len(state["team_form"]),
        "global_stats": state["global_stats"],
    }


def _track_model(state: dict, model: str, correct: bool) -> None:
    perf = state["model_performance"][model]
    perf["correct" if correct else "total"] += 0
    if correct:
        perf["correct"] += 1
    perf["total"] += 1
    perf["recent"].append(correct)
    if len(perf["recent"]) > WINDOW_SIZE:
        perf["recent"].pop(0)


def _model_accuracy(state: dict, model: str) -> float:
    perf = state["model_performance"][model]
    if perf["total"] == 0:
        return 0.0
    return perf["correct"] / perf["total"]


def _recent_accuracy(perf: dict) -> float:
    recent = perf.get("recent", [])
    if not recent:
        return 0.0
    return sum(recent) / len(recent)


def _recalibrate_weights(state: dict) -> None:
    dc_recent = _recent_accuracy(state["model_performance"]["dixon_coles"])
    elo_recent = _recent_accuracy(state["model_performance"]["elo"])

    if dc_recent == 0 and elo_recent == 0:
        return

    dc_w = 0.45 + (dc_recent - 0.55) * 0.2
    elo_w = 0.15 + (elo_recent - 0.55) * 0.15
    xgb_w = max(0.15, 1.0 - dc_w - elo_w)

    total = dc_w + elo_w + xgb_w
    dc_w /= total
    elo_w /= total
    xgb_w /= total

    dc_w = max(0.30, min(0.60, dc_w))
    elo_w = max(0.10, min(0.30, elo_w))
    xgb_w = 1.0 - dc_w - elo_w

    state["ensemble_weights"] = {
        "dixon_coles": round(dc_w, 4),
        "xgboost": round(xgb_w, 4),
        "elo": round(elo_w, 4),
    }


def _update_team_form(state: dict, tid_a: str, tid_b: str, score_a: int, score_b: int, dc_pred: dict) -> None:
    if "team_form" not in state:
        state["team_form"] = {}

    exp_ga = dc_pred.get("expected_goals_a", 1.2)
    exp_gb = dc_pred.get("expected_goals_b", 1.2)

    _update_single_team_form(state, tid_a, score_a, exp_ga, score_a - score_b)
    _update_single_team_form(state, tid_b, score_b, exp_gb, score_b - score_a)


def _update_single_team_form(state: dict, tid: str, actual_goals: int, expected_goals: float, goal_diff: int) -> None:
    if tid not in state["team_form"]:
        state["team_form"][tid] = {"form_factor": 0.0, "matches": 0, "total_overperformance": 0.0}

    tf = state["team_form"][tid]
    goal_overperformance = actual_goals - expected_goals

    if goal_diff > 0:
        goal_overperformance += 0.3
    elif goal_diff < 0:
        goal_overperformance -= 0.3

    tf["matches"] += 1
    tf["total_overperformance"] += goal_overperformance
    tf["form_factor"] = round(tf["total_overperformance"] / max(tf["matches"], 1), 4)


def _update_global_stats(state: dict, score_a: int, score_b: int, result: str) -> None:
    gs = state["global_stats"]
    total = state["total_tracked"] + 1

    prev_goals = gs.get("avg_goals_per_match", 0.0) * (total - 1)
    gs["avg_goals_per_match"] = round((prev_goals + score_a + score_b) / total, 2)

    prev_home = gs.get("home_win_rate", 0.0) * (total - 1)
    prev_draw = gs.get("draw_rate", 0.0) * (total - 1)
    prev_away = gs.get("away_win_rate", 0.0) * (total - 1)

    gs["home_win_rate"] = round((prev_home + (1 if result == "win" else 0)) / total, 3)
    gs["draw_rate"] = round((prev_draw + (1 if result == "draw" else 0)) / total, 3)
    gs["away_win_rate"] = round((prev_away + (1 if result == "loss" else 0)) / total, 3)


def _calibrate_confidence_thresholds(state: dict) -> None:
    dc_acc = _model_accuracy(state, "dixon_coles")
    if dc_acc > 0:
        state["confidence_thresholds"] = {
            "high": round(max(0.60, dc_acc + 0.08), 2),
            "medium": round(max(0.40, dc_acc - 0.05), 2),
            "low": round(max(0.25, dc_acc - 0.20), 2),
        }


def _determine_result(score_a: int, score_b: int) -> str:
    if score_a > score_b:
        return "win"
    elif score_a == score_b:
        return "draw"
    return "loss"


def _determine_prediction(pred: dict) -> str:
    w, d, l = pred.get("win", 0), pred.get("draw", 0), pred.get("loss", 0)
    if w >= d and w >= l:
        return "win"
    elif d >= w and d >= l:
        return "draw"
    return "loss"
