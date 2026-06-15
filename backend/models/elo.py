"""
Sistema de rating Elo para selecciones nacionales.

Basado en la metodología descrita en el Libro Blanco:
- Elo es la variable de mayor peso predictivo (2 órdenes de magnitud sobre otras)
- K-factor variable según importancia del partido
- Home advantage (+100 Elo)
- Goal difference multiplier para partidos jugados
"""

import math

from config import (
    ELO_K_WORLD_CUP,
    ELO_K_QUALIFIERS,
    ELO_K_CONTINENTAL,
    ELO_K_FRIENDLY,
    ELO_HOME_ADVANTAGE,
)
from utils.data_loader import load_json, save_json


K_FACTORS = {
    "world_cup": ELO_K_WORLD_CUP,
    "qualifier": ELO_K_QUALIFIERS,
    "continental": ELO_K_CONTINENTAL,
    "friendly": ELO_K_FRIENDLY,
}


def _load_elo_ratings() -> dict[str, int]:
    data = load_json("elo_ratings.json")
    if data and "ratings" in data:
        return data["ratings"]
    return {}


def get_elo(team_id: str) -> int:
    """Obtiene el rating Elo actual de un equipo."""
    ratings = _load_elo_ratings()
    return ratings.get(team_id, 1500)


def get_all_elos() -> dict[str, int]:
    return _load_elo_ratings()


def expected_score(elo_a: int, elo_b: int, home_advantage: bool = False) -> float:
    """
    Probabilidad esperada de victoria para el equipo A.

    Args:
        elo_a: Rating Elo del equipo A
        elo_b: Rating Elo del equipo B
        home_advantage: si A es local (+100 Elo)

    Returns:
        Probabilidad esperada (0-1) de que A gane.
    """
    if home_advantage:
        elo_a += ELO_HOME_ADVANTAGE
    return 1.0 / (1.0 + math.pow(10, -(elo_a - elo_b) / 400.0))


def win_probability(team_a_id: str, team_b_id: str, neutral: bool = True) -> dict[str, float]:
    """
    Calcula probabilidades Win/Draw/Loss basadas en Elo.

    Args:
        team_a_id: ID del equipo A
        team_b_id: ID del equipo B
        neutral: True si es cancha neutral (sin home advantage)

    Returns:
        Dict con {win, draw, loss} como probabilidades (0-1)
    """
    elo_a = get_elo(team_a_id)
    elo_b = get_elo(team_b_id)

    home_adv = not neutral
    we = expected_score(elo_a, elo_b, home_adv)

    elo_gap = abs(elo_a - elo_b)
    draw_base = 0.32 - (elo_gap / 400.0) * 0.14
    draw_prob = max(0.16, min(0.34, draw_base))

    win_prob = we * (1.0 - draw_prob)
    loss_prob = (1.0 - we) * (1.0 - draw_prob)

    total = win_prob + draw_prob + loss_prob
    return {
        "win": round(win_prob / total, 4),
        "draw": round(draw_prob / total, 4),
        "loss": round(loss_prob / total, 4),
    }


def update_elo(
    team_a_id: str,
    team_b_id: str,
    score_a: int,
    score_b: int,
    match_type: str = "friendly",
    neutral: bool = True,
) -> dict[str, int]:
    """
    Actualiza ratings Elo tras un partido.

    Args:
        team_a_id: ID del equipo A
        team_b_id: ID del equipo B
        score_a: Goles de A
        score_b: Goles de B
        match_type: tipo de partido (world_cup, qualifier, continental, friendly)
        neutral: True si es cancha neutral

    Returns:
        Dict con los nuevos Elo de ambos equipos
    """
    elo_a = get_elo(team_a_id)
    elo_b = get_elo(team_b_id)
    k = K_FACTORS.get(match_type, ELO_K_FRIENDLY)

    if score_a > score_b:
        actual_a, actual_b = 1.0, 0.0
    elif score_b > score_a:
        actual_a, actual_b = 0.0, 1.0
    else:
        actual_a, actual_b = 0.5, 0.5

    home_adv = not neutral
    exp_a = expected_score(elo_a, elo_b, home_adv)
    exp_b = 1.0 - exp_a

    goal_diff = abs(score_a - score_b)
    k_multiplier = math.sqrt(1.0 + goal_diff) if goal_diff > 0 else 1.0
    k_adj = k * k_multiplier

    new_a = int(elo_a + k_adj * (actual_a - exp_a))
    new_b = int(elo_b + k_adj * (actual_b - exp_b))

    data = load_json("elo_ratings.json") or {"last_updated": "", "ratings": {}}
    data["ratings"][team_a_id] = new_a
    data["ratings"][team_b_id] = new_b
    save_json("elo_ratings.json", data)

    return {team_a_id: new_a, team_b_id: new_b}


def elo_diff_to_goals(elo_diff: int, neutral: bool = True) -> tuple[float, float]:
    """
    Convierte diferencia de Elo en parámetros lambda esperados de goles.

    Returns:
        (lambda_a, lambda_b) goles esperados
    """
    base = 1.2
    home_bonus = 0.0 if neutral else 0.3
    diff_effect = (elo_diff + 100) * 0.006

    lambda_a = max(0.3, base + diff_effect + home_bonus)
    lambda_b = max(0.3, base - diff_effect - home_bonus)

    return lambda_a, lambda_b
