"""
Entrenador XGBoost para predicción de resultados de fútbol.

Basado en el Libro Blanco:
- XGBoost supera a Deep Learning (LSTM/CNN) para este volumen de datos (~7,000 registros)
- RPS de 0.18289 (mínimo error registrado)
- Features: elo_diff, elo_sum, home_advantage, match_type_importance, form, defensive_strength

El modelo predice 3 outputs:
- prob_home_win: probabilidad de victoria local
- prob_draw: probabilidad de empate
- prob_away_win: probabilidad de victoria visitante
- expected_goals_home, expected_goals_away: goles esperados
"""

import json
import pickle
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import xgboost as xgb

MODEL_DIR = Path(__file__).resolve().parent.parent / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset() -> list[dict]:
    path = Path(__file__).resolve().parent.parent / "data" / "historical_matches.json"
    with open(path) as f:
        data = json.load(f)
    return data["matches"]


def prepare_features(matches: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Prepara features y labels para XGBoost.

    Features (9):
    - elo_diff: diferencia de Elo (home - away)
    - elo_sum: suma de Elo (nivel del partido)
    - home_advantage: 1 si local, 0 neutral
    - match_type_importance: K/60 normalizado
    - form_diff: diferencia de forma reciente
    - elo_ratio: ratio de Elo (home/away)
    - recent_goals_home: goles promedio últimos 5 del local
    - recent_goals_away: goles promedio últimos 5 del visitante
    - strength_gap: brecha de calidad normalizada

    Labels (5):
    - result_home_win: 1 si gana local
    - result_draw: 1 si empate
    - result_away_win: 1 si gana visitante
    - goals_home: goles del local
    - goals_away: goles del visitante
    """
    X_list = []
    y_class = []
    y_reg = []

    for m in matches:
        elo_home = m["team_a"]
        elo_away = m["team_b"]

        features = [
            m["features"]["elo_diff"],
            m["features"]["elo_sum"],
            m["features"]["home_advantage"],
            m["features"]["match_type_importance"],
            elo_home / max(elo_away, 1),
            elo_home / 2200.0,
            elo_away / 2200.0,
            (elo_home - elo_away) / 400.0,
            m["features"].get("form_index_a", 0.5),
        ]

        if m["result"] == "win":
            labels_cls = [1, 0, 0]
        elif m["result"] == "draw":
            labels_cls = [0, 1, 0]
        else:
            labels_cls = [0, 0, 1]

        X_list.append(features)
        y_class.append(labels_cls)
        y_reg.append([m["score_a"], m["score_b"]])

    return np.array(X_list), np.array(y_class), np.array(y_reg)


def train_xgboost_model() -> dict:
    """Entrena modelo XGBoost multi-output para clasificación y regresión."""

    matches = load_dataset()
    print(f"Cargados {len(matches)} partidos para entrenamiento")

    X, y_class, y_reg = prepare_features(matches)

    X_train, X_test, yc_train, yc_test, yr_train, yr_test = train_test_split(
        X, y_class, y_reg, test_size=0.15, random_state=42
    )

    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    model_win = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        verbosity=0,
    )

    model_draw = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        verbosity=0,
    )

    model_away = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        verbosity=0,
    )

    model_goals_home = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        verbosity=0,
    )

    model_goals_away = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        verbosity=0,
    )

    print("Entrenando XGBoost...")
    model_win.fit(X_train, yc_train[:, 0])
    model_draw.fit(X_train, yc_train[:, 1])
    model_away.fit(X_train, yc_train[:, 2])
    model_goals_home.fit(X_train, yr_train[:, 0])
    model_goals_away.fit(X_train, yr_train[:, 1])

    yp_win = model_win.predict_proba(X_test)[:, 1]
    yp_draw = model_draw.predict_proba(X_test)[:, 1]
    yp_away = model_away.predict_proba(X_test)[:, 1]

    yp_probs = np.column_stack([yp_win, yp_draw, yp_away])
    yp_probs = yp_probs / yp_probs.sum(axis=1, keepdims=True)
    yp_class = np.argmax(yp_probs, axis=1)
    yt_class = np.argmax(yc_test, axis=1)

    accuracy = accuracy_score(yt_class, yp_class)

    yp_goals_home = model_goals_home.predict(X_test)
    yp_goals_away = model_goals_away.predict(X_test)
    rmse_goals = np.sqrt(mean_squared_error(
        np.column_stack([yr_test[:, 0], yr_test[:, 1]]),
        np.column_stack([yp_goals_home, yp_goals_away])
    ))

    rps = _compute_rps(yc_test, yp_probs)

    print(f"\nResultados del entrenamiento:")
    print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
    print(f"  RPS: {rps:.5f}")
    print(f"  RMSE goles: {rmse_goals:.3f}")

    for name, model in [
        ("win", model_win), ("draw", model_draw), ("away", model_away),
        ("goals_home", model_goals_home), ("goals_away", model_goals_away),
    ]:
        path = MODEL_DIR / f"xgboost_{name}.pkl"
        with open(path, "wb") as f:
            pickle.dump(model, f)

    metadata = {
        "n_samples": len(matches),
        "n_features": X.shape[1],
        "accuracy": float(accuracy),
        "rps": float(rps),
        "rmse_goals": float(rmse_goals),
        "trained_at": str(np.datetime64("now")),
    }
    with open(MODEL_DIR / "xgboost_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def _compute_rps(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Ranked Probability Score: métrica estándar para predicciones probabilísticas."""
    n = y_true.shape[0]
    rps_sum = 0.0
    for i in range(n):
        cum_true = np.cumsum(y_true[i])
        cum_pred = np.cumsum(y_pred[i])
        rps_sum += np.sum((cum_pred - cum_true) ** 2) / (len(cum_true) - 1)
    return rps_sum / n


if __name__ == "__main__":
    result = train_xgboost_model()
    print(f"\n✅ Modelo guardado en {MODEL_DIR}")
