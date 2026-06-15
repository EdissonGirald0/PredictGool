"""
Endpoints de accuracy: comparativa de predicciones vs resultados reales.
"""

from fastapi import APIRouter

from utils.data_loader import load_json
from models.ensemble import predict_ensemble

router = APIRouter(prefix="/api/accuracy", tags=["accuracy"])


@router.get("")
def get_accuracy():
    """Compara predicciones con resultados reales registrados."""
    results = load_json("results.json") or []
    if not results:
        return {"message": "No hay resultados para comparar", "total": 0, "accuracy": None}

    comparisons = []
    correct = 0
    total = 0

    for r in results:
        if not r.get("played"):
            continue
        tid_a = r["team_a"].lower().replace(" ", "_")
        tid_b = r["team_b"].lower().replace(" ", "_")

        try:
            pred = predict_ensemble(tid_a, tid_b)
        except Exception:
            continue

        predicted_result = "win" if pred["win"] > max(pred["draw"], pred["loss"]) else \
                          "draw" if pred["draw"] > max(pred["win"], pred["loss"]) else "loss"

        actual_result = "win" if r["score_a"] > r["score_b"] else \
                       "draw" if r["score_a"] == r["score_b"] else "loss"

        is_correct = predicted_result == actual_result
        if is_correct:
            correct += 1
        total += 1

        comparisons.append({
            "team_a": r["team_a"],
            "team_b": r["team_b"],
            "score_a": r["score_a"],
            "score_b": r["score_b"],
            "date": r.get("date", ""),
            "actual_result": actual_result,
            "predicted_result": predicted_result,
            "predicted_probabilities": {
                "win": pred["win"],
                "draw": pred["draw"],
                "loss": pred["loss"],
            },
            "correct": is_correct,
        })

    accuracy = correct / total if total > 0 else None

    daily_accuracy = {}
    for c in comparisons:
        date = c.get("date", "unknown")
        if date not in daily_accuracy:
            daily_accuracy[date] = {"correct": 0, "total": 0}
        daily_accuracy[date]["total"] += 1
        if c["correct"]:
            daily_accuracy[date]["correct"] += 1

    by_result_type = {"win": {"correct": 0, "total": 0}, "draw": {"correct": 0, "total": 0}, "loss": {"correct": 0, "total": 0}}
    for c in comparisons:
        by_result_type[c["actual_result"]]["total"] += 1
        if c["correct"]:
            by_result_type[c["actual_result"]]["correct"] += 1

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 4) if accuracy is not None else None,
        "comparisons": comparisons,
        "by_result_type": {
            k: {
                "accuracy": round(v["correct"] / v["total"], 4) if v["total"] > 0 else None,
                "correct": v["correct"],
                "total": v["total"],
            }
            for k, v in by_result_type.items()
        },
    }
